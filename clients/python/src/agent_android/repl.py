from __future__ import annotations

import json
import os
import shlex
import sys
import traceback
from typing import Any, Dict, List, Optional, Tuple

from .client import AgentAndroidClient
from .config import CONFIG_FILE_PATH, save_token_to_config, save_url_to_config
from .formatting import (
    _format_launcher_app,
    format_detail_card,
    format_element,
    format_status,
    print_tree,
)

try:
    import readline
    _HAS_READLINE = True
except ImportError:
    _HAS_READLINE = False

_REPL_EXIT = object()

class AriaReplSession:
    """
    agent-android REPL session.

    Command syntax: verb [+ modifiers/arguments]
    Examples:
      l                    -> list elements (reuse cache)
      ss                   -> refresh the tree and list again
      t 5                  -> tap refId=5
      i 5 hello            -> input text into refId=5
      s                    -> capture a screenshot with an auto-generated name
      s my.png             -> capture a screenshot to a specific path
      sw d                 -> swipe down (down/up/left/right)
      sw d --dur 500 --dist 0.7  -> swipe down for 500ms at distance 0.7
      wf Search            -> wait for a "Search" element (default 30s)
      wf Search --t 60     -> wait up to 60s
      g 5 text             -> get the text attribute for refId=5
      p home               -> press the Home key
      b                    -> navigate back
      la com.xingin.xhs    -> launch an app
      f Search             -> filter elements containing "Search"
      id com.example:id/btn -> filter by resourceId
      ref 5                -> show refId=5 details
      x 5                  -> show XPath candidates for refId=5
      vx //EditText[1] 0   -> inspect the first runtime match for an XPath
      raw                  -> toggle raw JSON output
      vars                 -> show session variables
      set url http://...   -> set the server URL
      set timeout 30       -> set the default wait timeout
      h                    -> show help
      q                    -> quit
    """

    COMMANDS = [
        ('l', 'list',          'List elements (reuse cache)'),
        ('ss', 'snapshot',     'Refresh the tree and list again'),
        ('hl', 'health',       'Check service health'),
        ('f', 'find',          'Filter by text or content description'),
        ('id', None,           'Filter by resourceId'),
        ('ref', None,          'Show element details'),
        ('node', None,         'Print raw UI-tree node XML for a refId'),
        ('x', 'xpath',         'Show XPath candidates and match counts'),
        ('mx', 'multixpath',   'Find shared XPath candidates for multiple refIds'),
        ('xx', None,           'Tap via the best unique auto-generated XPath'),
        ('vx', 'validatex',    'Validate an XPath at runtime'),
        ('vn', 'validatenodes','Print raw UI-tree node XML for XPath matches'),
        ('t', 'tap',           'Tap an element by refId'),
        ('tx', 'tapx',         'Tap an element by XPath'),
        ('i', 'input',         'Input text (refId text)'),
        ('ix', 'inputx',       'Input text by XPath'),
        ('sw', 'swipe',        'Swipe (d/u/l/r)'),
        ('p', 'press',         'Press a key (back/home/recents)'),
        ('b', 'back',          'Press Back'),
        ('wf', 'waitfor',      'Wait for an element to appear'),
        ('g', 'get',           'Read an element attribute'),
        ('s', 'screenshot',    'Capture a screenshot'),
        ('ux', 'uitree',       'Print or save the current UI tree XML'),
        ('la', 'launch',       'Launch an app'),
        ('raw', None,          'Toggle raw JSON output'),
        ('vars', None,         'Show session variables'),
        ('apps', None,         'List launcher apps'),
        ('set', None,          'Set variables (url/timeout)'),
        ('h', 'help',          'Show help'),
        ('q', 'quit',          'Quit'),
    ]

    def __init__(self, url: str, token: str = None, history_file: str = None):
        self.client = AgentAndroidClient(url, token=token)
        self._tree: Optional[List[Dict]] = None   # Currently cached tree
        self._raw_output: bool = False            # Raw JSON output toggle
        self._timeout: int = 30                  # Default wait timeout in seconds
        self._prompt: str = "aria> "
        self.variables: Dict[str, Any] = {}      # Session variables

        if _HAS_READLINE and history_file:
            try:
                readline.read_history_file(history_file)
            except FileNotFoundError:
                pass
            self._history_file = history_file

        self._aliases: Dict[str, str] = {}
        for short, full, _ in self.COMMANDS:
            if short:
                self._aliases[short] = full or short
            if full:
                self._aliases[full] = full

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def run(self):
        self._print_banner()
        while True:
            try:
                line = self._readline()
                if line is None:  # EOF / Ctrl+D
                    break
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                result = self._execute_line(line)
                if result is _REPL_EXIT:
                    break

            except KeyboardInterrupt:
                print()  # New line after Ctrl+C
                print("  (Ctrl+C: type q to quit)", file=sys.stderr)
                continue
            except EOFError:
                break
            except Exception:
                print(f"  [!] Error: {traceback.format_exc(limit=3)}", file=sys.stderr)

        self._save_history()
        print("Goodbye!")

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _parse_line(self, line: str) -> Tuple[str, List[str]]:
        """
        Parse a single REPL command line.

        Returns (command_name, [arg1, arg2, ...]).
        Supports:
          - whitespace-separated tokens
          - double-quoted or single-quoted strings
          - --flag value style parameters
        """
        stripped = line.strip()
        if not stripped:
            return '', []

        first, _, remainder = stripped.partition(' ')
        cmd = first
        remainder = remainder.strip()

        if cmd in ('tx', 'tapx'):
            return cmd, [remainder] if remainder else []

        if cmd in ('vx', 'validatex', 'vn', 'validatenodes'):
            xpath, extra = self._split_xpath_expression(remainder)
            if not xpath:
                return cmd, []
            if cmd in ('vx', 'validatex') and extra and extra.isdigit():
                return cmd, [xpath, extra]
            if cmd in ('vx', 'validatex') and extra.startswith('(') and extra.endswith(')'):
                return cmd, [xpath]
            return cmd, [xpath] if xpath else []

        if cmd in ('ix', 'inputx'):
            return cmd, self._parse_xpath_input_args(remainder)

        if cmd in ('i', 'input'):
            return cmd, self._parse_ref_input_args(remainder)

        tokens = shlex.split(line, posix=False)
        if not tokens:
            return '', []
        cmd = tokens[0]
        args = tokens[1:]

        return cmd, args

    def _split_xpath_expression(self, remainder: str) -> Tuple[str, str]:
        """Split '<xpath> <rest>' without breaking spaces inside predicates."""
        text = remainder.strip()
        if not text:
            return '', ''

        depth = 0
        in_quote: Optional[str] = None
        for index, ch in enumerate(text):
            if in_quote is not None:
                if ch == in_quote:
                    in_quote = None
                continue
            if ch in ("'", '"'):
                in_quote = ch
                continue
            if ch == '[':
                depth += 1
                continue
            if ch == ']':
                depth = max(0, depth - 1)
                continue
            if ch.isspace() and depth == 0:
                return text[:index].strip(), text[index + 1:].strip()
        return text, ''

    def _parse_xpath_input_args(self, remainder: str) -> List[str]:
        remainder = remainder.strip()
        if not remainder:
            return []
        if remainder.endswith(' --'):
            xpath = remainder[:-3].strip()
            return [xpath, ''] if xpath else []
        if ' -- ' in remainder:
            xpath, text = remainder.split(' -- ', 1)
            xpath = xpath.strip()
            return [xpath, text] if xpath else []
        xpath, text = self._split_xpath_expression(remainder)
        if not xpath:
            return []
        if not text:
            return [xpath]
        return [xpath, text]

    def _parse_ref_input_args(self, remainder: str) -> List[str]:
        remainder = remainder.strip()
        if not remainder:
            return []
        ref_id, sep, text = remainder.partition(' ')
        if not sep:
            return [ref_id]
        return [ref_id, text]

    def _decode_input_payload(self, raw_text: str) -> str:
        if raw_text == '--clear':
            return ''
        if raw_text in {'""', "''"}:
            return ''
        return raw_text

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _execute_line(self, line: str) -> Any:
        cmd, args = self._parse_line(line)

        resolved = self._aliases.get(cmd, cmd)
        handler_name = f"_cmd_{resolved}"
        handler = getattr(self, handler_name, None)
        if handler is None:
            self._print_error(f"Unknown command: {cmd!r}.  Type 'h' for help.")
            return False

        try:
            return handler(args)
        except TypeError as e:
            self._print_error(f"Usage: {e}")
            return False

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _readline(self) -> Optional[str]:
        if _HAS_READLINE:
            return input(self._prompt)
        else:
            return input(self._prompt)

    def _add_history(self, line: str):
        if _HAS_READLINE:
            try:
                readline.add_history(line)
            except Exception:
                pass

    def _save_history(self):
        if _HAS_READLINE and hasattr(self, '_history_file'):
            try:
                readline.write_history_file(self._history_file)
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _ensure_tree(self, force=False) -> Optional[List[Dict]]:
        """Ensure a cached tree exists, refreshing it when needed."""
        if force or self._tree is None:
            self._tree = self.client.get_ui_elements(force_refresh=True)
        return self._tree

    def _invalidate_tree(self):
        """Invalidate the cached tree after a UI action."""
        self._tree = None
        self.client._local_tree = None

    def _current_package_label(self) -> str:
        pkg = self.client.get_current_package_name()
        return pkg or "unknown"

    def _print_tree(self, elements: List[Dict], title: str = None):
        """Pretty-print a list of elements."""
        print()
        n = len(elements)
        title = title or f"ARIA Tree - {n} elements"
        print(f"  ╭{'─' * 66}╮")
        print(f"  │ {title:<64} │")
        print(f"  ╰{'─' * 66}╯")
        print(f"  Current package: {self._current_package_label()}")
        for e in elements:
            rid = e.get('refId', '?')
            text = str(e.get('text', '') or e.get('contentDesc', '') or '-')
            cls = e.get('simpleClassName', '')
            x, y = e.get('x', '?'), e.get('y', '?')
            flags = []
            if e.get('clickable'): flags.append('click')
            if e.get('focusable'): flags.append('focus')
            flag = f"[{','.join(flags)}]" if flags else ""
            text_disp = text[:22] + '...' if len(text) > 22 else text
            print(f"  [{rid:>2}] {text_disp:<24} {cls:<16} ({str(x):>4},{str(y):>4}) {flag}")
        print()

    def _runtime_validate_candidates(
        self, candidates: List[Tuple[str, int, str]]
    ) -> List[Tuple[str, int, str, Optional[Dict[str, Any]]]]:
        """Validate XPath candidates with the Android runtime evaluator."""
        validated: List[Tuple[str, int, str, Optional[Dict[str, Any]]]] = []
        strategy_order = {
            'text': 0,
            'contentDescription': 1,
            'ancestor-relative': 2,
            'className+position': 3,
            'className+resourceId': 4,
            'className+text+resourceId': 5,
            'className+text+contentDescription': 6,
            'text+clickable': 7,
            'className-only': 99,
        }

        for xp, _, strategy in candidates:
            info = self.client.validate_xpath_runtime(xp)
            count = info.get('count', -1) if info else -1
            validated.append((xp, count, strategy, info))

        validated.sort(key=lambda c: (
            0 if c[1] == 1 else 1,
            0 if c[1] >= 0 else 2,
            strategy_order.get(c[2], 99),
            c[1] if c[1] >= 0 else 999999,
        ))
        return validated

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_list(self, args: List[str]) -> bool:
        """l [n] - list the first n elements, or all elements by default."""
        limit = None
        if args and args[0].isdigit():
            limit = int(args[0])
        tree = self._ensure_tree()
        if not tree:
            self._print_error(
                f"Failed to get ARIA tree (package={self._current_package_label()}). "
                "Check the connection hints above."
            )
            return False
        elems = tree[:limit] if limit else tree
        self._print_tree(elems)
        return True

    def _cmd_snapshot(self, args: List[str]) -> bool:
        """ss - force-refresh the tree and print it."""
        tree = self._ensure_tree(force=True)
        if not tree:
            self._print_error(
                f"Failed to get ARIA tree (package={self._current_package_label()}). "
                "Check the connection hints above."
            )
            return False
        self._print_tree(tree, f"ARIA Tree (refreshed) - {len(tree)} elements")
        return True

    def _cmd_l(self, args: List[str]) -> bool:
        return self._cmd_list(args)

    def _cmd_ss(self, args: List[str]) -> bool:
        return self._cmd_snapshot(args)

    def _cmd_health(self, args: List[str]) -> bool:
        """health - fetch and print the /health payload."""
        health = self.client.get_health()
        if health is None:
            self._print_error("Failed to fetch health. Check the connection hints above.")
            return False
        if self._raw_output:
            print(json.dumps(health, indent=2, ensure_ascii=False))
            return True
        print("Health:")
        for key, value in health.items():
            print(f"  {key}: {value}")
        return True

    def _cmd_hl(self, args: List[str]) -> bool:
        return self._cmd_health(args)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_find(self, args: List[str]) -> bool:
        """f [text] - filter elements by text or content description."""
        if not args:
            self._print_error("Usage: f <text>")
            return False
        text = ' '.join(args)
        tree = self._ensure_tree()
        if not tree:
            return False
        results = self.client.find_by_text(tree, text)
        if not results:
            print(f"  [!] No elements matching: {text!r}")
            return False
        self._print_tree(results, f"Find: '{text}' ({len(results)} matches)")
        return True

    def _cmd_f(self, args: List[str]) -> bool:
        return self._cmd_find(args)

    def _cmd_id(self, args: List[str]) -> bool:
        """id <resourceId> - filter elements by resourceId."""
        if not args:
            self._print_error("Usage: id <resourceId>")
            return False
        rid = ' '.join(args)
        tree = self._ensure_tree()
        if not tree:
            return False
        results = self.client.find_by_resourceId(tree, rid)
        if not results:
            print(f"  [!] No elements with resourceId: {rid!r}")
            return False
        self._print_tree(results, f"resourceId: {rid!r} ({len(results)} matches)")
        return True

    def _cmd_ref(self, args: List[str]) -> bool:
        """ref <N> - show details for refId=N."""
        if not args or not args[0].isdigit():
            self._print_error("Usage: ref <refId>")
            return False
        refId = int(args[0])
        tree = self._ensure_tree()
        if not tree:
            return False
        elem = self.client.find_by_refId(tree, refId)
        if not elem:
            print(f"  [!] Element refId={refId} not found ({len(tree)} elements in tree)")
            return False
        print(format_element(elem))
        return True

    def _cmd_node(self, args: List[str]) -> bool:
        """node <refId> - print the raw UI-tree node XML for a refId."""
        if not args or not args[0].isdigit():
            self._print_error("Usage: node <refId>")
            return False
        refId = int(args[0])
        tree = self._ensure_tree()
        if not tree:
            return False
        elem = self.client.find_by_refId(tree, refId)
        if not elem:
            print(f"  [!] Element refId={refId} not found ({len(tree)} elements in tree)")
            return False
        snippet = self.client.get_node_snippet_for_element(elem)
        if not snippet:
            print(f"  [!] Could not resolve a UI-tree node snippet for refId={refId}")
            return False
        print(snippet)
        return True

    def _cmd_xpath(self, args: List[str]) -> bool:
        """x <N> - show XPath candidates validated by Android runtime match counts."""
        if len(args) != 1 or not args[0].isdigit():
            self._print_error("Usage: x <refId>")
            return False
        refId = int(args[0])
        tree = self._ensure_tree()
        if not tree:
            return False
        elem = self.client.find_by_refId(tree, refId)
        if not elem:
            print(f"  [!] Element refId={refId} not found")
            return False

        raw_candidates = self.client.generate_xpath_candidates(elem, tree)
        if not raw_candidates:
            print(f"  [!] No XPath candidates generated")
            return False
        candidates = self._runtime_validate_candidates(raw_candidates)
        ui_tree_absolute = self.client.build_ui_tree_absolute_xpath(tree, elem)
        runtime_absolute = self.client.build_runtime_absolute_xpath(tree, elem)
        runtime_absolute_info = self.client.validate_xpath_runtime(runtime_absolute) if runtime_absolute else None
        visible_candidates = [candidate for candidate in candidates if candidate[1] != 0]
        if not visible_candidates:
            visible_candidates = candidates

        print()
        print(f"  refId={refId}  text='{elem.get('text', '')[:30]}'  "
              f"class={elem.get('simpleClassName', '')}")
        if ui_tree_absolute and ui_tree_absolute != runtime_absolute:
            print(f"  UI tree absolute path: {ui_tree_absolute}")
        if runtime_absolute:
            runtime_count = runtime_absolute_info.get('count') if runtime_absolute_info else '?'
            print(f"  Runtime absolute path: {runtime_absolute}  (match={runtime_count})")
        print(f"  {'-' * 60}")
        print(f"  {'Idx':<4} {'Runtime':<10} {'XPath'}")
        print(f"  {'-' * 60}")

        for i, (xp, count, strategy, info) in enumerate(visible_candidates):
            badge = ''
            if count < 0:
                badge = ' ? error'
            elif count == 1:
                badge = ' OK unique'
            elif count <= 3:
                badge = f' ! {count} matches'
            else:
                badge = f' X {count} matches'
            xp_display = xp if len(xp) <= 55 else xp[:52] + '...'
            print(f"  [{i}] {badge:<8} {xp_display}  ({strategy})")
            if info and count == 1:
                summary = info.get('text') or info.get('contentDescription') or '-'
                print(f"      -> {info.get('className') or '-'} | {summary!r}")

        print(f"  {'-' * 60}")
        best = visible_candidates[0]
        if best[1] == 1:
            print(f"  Recommended: {best[0]}")
            print(f"    strategy={best[2]}, runtime matched exactly 1 element")
        elif best[1] < 0:
            print(f"  Warning: best candidate validation failed; try 'vx <xpath>' first")
            print(f"     recommended: {best[0]}")
        else:
            print(f"  Warning: best candidate matched {best[1]} elements at runtime and may not be unique")
            print(f"     recommended: {best[0]}")

        self.variables['LAST_UI_TREE_ABSOLUTE_XPATH'] = ui_tree_absolute
        self.variables['LAST_RUNTIME_ABSOLUTE_XPATH'] = runtime_absolute
        self.variables['LAST_RUNTIME_ABSOLUTE_INFO'] = runtime_absolute_info
        self.variables.pop('LAST_XPATH', None)
        self.variables.pop('LAST_XPATH_COUNT', None)
        self.variables.pop('LAST_XPATH_STRATEGY', None)
        self.variables.pop('LAST_XPATH_RUNTIME', None)
        return True

    def _cmd_x(self, args: List[str]) -> bool:
        return self._cmd_xpath(args)

    def _parse_refid_list(self, args: List[str]) -> List[int]:
        ref_ids: List[int] = []
        for arg in args:
            for part in arg.split(","):
                value = part.strip()
                if not value:
                    continue
                if not value.isdigit():
                    raise ValueError(value)
                ref_ids.append(int(value))
        deduped: List[int] = []
        seen: set[int] = set()
        for ref_id in ref_ids:
            if ref_id in seen:
                continue
            seen.add(ref_id)
            deduped.append(ref_id)
        return deduped

    def _cmd_multixpath(self, args: List[str]) -> bool:
        """mx <id1,id2,...> - find shared XPath candidates for multiple refIds."""
        if not args:
            self._print_error("Usage: mx <refId[,refId...] ...>")
            return False
        try:
            ref_ids = self._parse_refid_list(args)
        except ValueError:
            self._print_error("Usage: mx <refId[,refId...] ...>")
            return False
        if len(ref_ids) < 2:
            self._print_error("Usage: mx <refId[,refId...] ...>")
            self._print_error("  Provide at least two refIds, for example: mx 13,14")
            return False

        tree = self._ensure_tree()
        if not tree:
            return False

        elems: List[Dict[str, Any]] = []
        for ref_id in ref_ids:
            elem = self.client.find_by_refId(tree, ref_id)
            if not elem:
                print(f"  [!] Element refId={ref_id} not found")
                return False
            elems.append(elem)

        candidates = self.client.generate_multi_xpath_candidates(elems, tree)
        if not candidates:
            print("  [!] No shared XPath candidates generated")
            return False

        target_count = len(elems)
        exact_candidates = [candidate for candidate in candidates if candidate[1] == target_count]
        superset_candidates = [candidate for candidate in candidates if candidate[1] > target_count]
        partial_candidates = [candidate for candidate in candidates if 0 <= candidate[1] < target_count]
        error_candidates = [candidate for candidate in candidates if candidate[1] < 0]
        visible_candidates = exact_candidates + superset_candidates
        if not visible_candidates:
            visible_candidates = partial_candidates + error_candidates

        print()
        print(f"  refIds={','.join(str(ref_id) for ref_id in ref_ids)}  targetCount={target_count}")
        print(f"  {'-' * 60}")
        print(f"  {'Idx':<4} {'Runtime':<10} {'Strategy'}")
        print(f"  {'-' * 60}")

        for index, (xpath, count, strategy) in enumerate(visible_candidates):
            if count < 0:
                badge = " ? error"
                summary = "runtime validation failed"
            elif count == target_count:
                badge = f" OK exact"
                summary = f"exact match ({count})"
            elif count > target_count:
                badge = f" X {count} matches"
                if strategy in ("same-parent positions", "same-parent contiguous-range"):
                    summary = f"superset ({count}, runtime ignored predicate)"
                else:
                    summary = f"superset ({count})"
            else:
                badge = f" ! {count} matches"
                summary = f"partial ({count})"
            print(f"  [{index}] {badge:<10} {strategy}")
            print(f"      -> {summary}")
            print(f"      XPath: {xpath}")

        if partial_candidates:
            print(f"  {'-' * 60}")
            print("  Skipped partial candidates:")
            for xpath, count, strategy in partial_candidates:
                print(f"      {strategy}: matched {count}")

        print(f"  {'-' * 60}")
        best = visible_candidates[0]
        if best[1] == target_count:
            print(f"  Recommended exact: {best[0]}")
            print(f"    strategy={best[2]}, runtime matched exactly {target_count} elements")
        elif best[1] > target_count:
            if not exact_candidates:
                print("  Note: no exact multi-match XPath appears to be supported by the current runtime.")
            print(f"  Recommended superset: {best[0]}")
            print(f"    strategy={best[2]}, runtime matched {best[1]} elements")
        else:
            print(f"  Warning: best candidate is incomplete or failed validation")
            print(f"     recommended: {best[0]}")

        self.variables["LAST_MULTI_REFIDS"] = ref_ids
        self.variables["LAST_MULTI_XPATH"] = best[0]
        self.variables["LAST_MULTI_XPATH_COUNT"] = best[1]
        self.variables["LAST_MULTI_XPATH_STRATEGY"] = best[2]
        return True

    def _cmd_mx(self, args: List[str]) -> bool:
        return self._cmd_multixpath(args)

    def _cmd_xx(self, args: List[str]) -> bool:
        """xx <N> - tap via an auto-generated unique XPath when possible."""
        if not args or not args[0].isdigit():
            self._print_error("Usage: xx <refId>")
            return False
        refId = int(args[0])
        tree = self._ensure_tree()
        if not tree:
            return False
        elem = self.client.find_by_refId(tree, refId)
        if not elem:
            print(f"  [!] Element refId={refId} not found")
            return False

        raw_candidates = self.client.generate_xpath_candidates(elem, tree)
        if not raw_candidates:
            print(f"  [!] No XPath candidates generated")
            return False
        candidates = self._runtime_validate_candidates(raw_candidates)

        unique: Optional[Tuple[str, int, str, Optional[Dict[str, Any]]]] = None
        for xp, count, strategy, info in candidates:
            if count == 1:
                unique = (xp, count, strategy, info)
                break

        if unique:
            xp, count, strategy, _ = unique
            print(f"  Success: refId={refId} -> XPath (unique match): {xp}")
            print(f"    strategy: {strategy}")
        else:
            xp, count, strategy, _ = candidates[0]
            print(f"  [!] refId={refId}: no uniquely matching XPath was found")
            print(f"  Warning: best candidate: {xp}")
            print(f"     strategy: {strategy}, runtime matched {count} elements")
            print(f"  Tap refused - the XPath is not unique enough and may hit the wrong element")
            print(f"  ")
            print(f"  Tip: use 'x {refId}' to inspect all candidates, or 'vx <xpath> <index>' to inspect one runtime match")
            return False

        ok = self.client.tap_by_xpath(xp)
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_xx_alias(self, args: List[str]) -> bool:
        """tapx-auto <refId> - alias for xx."""
        return self._cmd_xx(args)

    def _cmd_validatex(self, args: List[str]) -> bool:
        """vx <xpath> [idx] - validate an XPath at runtime and optionally inspect one match."""
        if not args:
            self._print_error("Usage: vx <xpath> [idx]")
            return False
        xpath = args[0]
        detail_index: Optional[int] = None
        if len(args) >= 2:
            if not args[1].isdigit():
                self._print_error("Usage: vx <xpath> [idx]")
                return False
            detail_index = int(args[1])
        info = self.client.validate_xpath_runtime(xpath)
        if not info:
            print(f"  [!] Runtime validation failed: {xpath}")
            return False

        count = info.get("count")
        if detail_index is None and info.get('count') == 1:
            detail_index = 0
        if detail_index is not None:
            detail = self.client.describe_xpath_match(xpath, detail_index)
            if not detail:
                print(f"  [!] Match index {detail_index} is out of range")
                return False
            desc = detail.get("contentDescription") or "-"
            vx_elem = {
                "text": detail.get("text") or "-",
                "className": detail.get("className") or "-",
                "bounds": detail.get("bounds") or "-",
                "x": detail.get("x"),
                "y": detail.get("y"),
                "clickable": detail.get("clickable"),
                "focusable": detail.get("focusable"),
                "isInput": detail.get("isInput"),
            }
            print(
                format_detail_card(
                    f"XPath: {xpath}",
                    [
                        ("matches", count),
                        ("text", vx_elem["text"]),
                        ("className", str(vx_elem["className"]).rsplit(".", 1)[-1]),
                        ("bounds", vx_elem["bounds"]),
                        ("position", f"({vx_elem.get('x')}, {vx_elem.get('y')})"),
                        ("status", format_status(vx_elem)),
                    ],
                )
            )
        elif info.get('count', 0) > 1:
            print(f"  XPath: {xpath}")
            print(f"  Runtime match count: {count}")
            print("  Tip: append an index to inspect one match, for example: vx <xpath> 0")
            print("  Tip: use 'vn <xpath>' to print the matched <node .../> snippets")
        elif info.get('count', 0) == 0:
            print(f"  XPath: {xpath}")
            print("  Runtime match count: 0")
            print("  No elements matched.")
        else:
            print(
                format_detail_card(
                    f"XPath: {xpath}",
                    [
                        ("matches", count),
                        ("text", info.get("text") or "-"),
                        ("className", str(info.get("className") or "-").rsplit(".", 1)[-1]),
                        ("bounds", info.get("bounds") or "-"),
                        ("position", "(None, None)"),
                        ("status", "none"),
                    ],
                )
            )
        return True

    def _cmd_vx(self, args: List[str]) -> bool:
        return self._cmd_validatex(args)

    def _cmd_validatenodes(self, args: List[str]) -> bool:
        """vn <xpath> - print raw UI-tree node XML snippets for XPath matches."""
        if not args:
            self._print_error("Usage: vn <xpath>")
            return False
        xpath = args[0]
        snippets = self.client.get_node_snippets_for_xpath(xpath)
        if not snippets:
            print(f"  XPath: {xpath}")
            print("  No matched node snippets.")
            return True
        print(f"  XPath: {xpath}")
        print(f"  Matched node snippets: {len(snippets)}")
        for snippet in snippets:
            print(f"  {snippet}")
        return True

    def _cmd_vn(self, args: List[str]) -> bool:
        return self._cmd_validatenodes(args)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_tap(self, args: List[str]) -> bool:
        """t <refId> - tap an element."""
        if not args or not args[0].isdigit():
            self._print_error("Usage: t <refId>")
            return False
        refId = int(args[0])
        ok = self.client.tap_element(refId)
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_t(self, args: List[str]) -> bool:
        return self._cmd_tap(args)

    def _cmd_input(self, args: List[str]) -> bool:
        """i <refId> <text|--clear> - input text into an element."""
        if len(args) < 2 or not args[0].isdigit():
            self._print_error("Usage: i <refId> <text|--clear>")
            self._print_error("  Example: i 5 hello world")
            self._print_error("  Example: i 5 --clear")
            self._print_error('  Example: i 5 ""')
            return False
        refId = int(args[0])
        text = self._decode_input_payload(' '.join(args[1:]))
        ok = self.client.input_to_element(refId, text)
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_i(self, args: List[str]) -> bool:
        return self._cmd_input(args)

    def _cmd_tapx(self, args: List[str]) -> bool:
        """tx <xpath> - tap an element by XPath."""
        if not args:
            self._print_error("Usage: tx <xpath>")
            self._print_error("  Example: tx //EditText[@text='Search']")
            self._print_error("  Example: tx //Button[@text='OK']")
            self._print_error("  Example: tx //TextView[@contentDescription='Search'][clickable]")
            return False
        xpath = ' '.join(args)
        ok = self.client.tap_by_xpath(xpath)
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_tx(self, args: List[str]) -> bool:
        return self._cmd_tapx(args)

    def _cmd_inputx(self, args: List[str]) -> bool:
        """ix <xpath> <text|--clear> - input text into a field by XPath."""
        if len(args) < 2:
            self._print_error("Usage: ix <xpath> <text|--clear>")
            self._print_error("  Example: ix //EditText[@text='Search'] hello")
            self._print_error("  Example: ix //EditText[@text='Search'] -- hello world")
            self._print_error("  Example: ix //EditText[@text='Search'] --")
            self._print_error("  Example: ix //EditText[@text='Search'] --clear")
            return False
        xpath = args[0]
        text = self._decode_input_payload(' '.join(args[1:]))
        ok = self.client.input_by_xpath(xpath, text)
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_ix(self, args: List[str]) -> bool:
        return self._cmd_inputx(args)

    def _cmd_swipe(self, args: List[str]) -> bool:
        """sw <d|u|l|r> [--dur N] [--dist N] - swipe."""
        if not args or args[0] not in ('d', 'u', 'l', 'r',
                                          'down', 'up', 'left', 'right'):
            self._print_error("Usage: sw <d|u|l|r> [--dur N] [--dist N]")
            return False
        direction_map = {'d': 'down', 'u': 'up', 'l': 'left', 'r': 'right'}
        direction = direction_map.get(args[0], args[0])

        duration = 300
        distance = 0.5
        i = 1
        while i < len(args):
            if args[i] == '--dur' and i + 1 < len(args):
                duration = int(args[i + 1]); i += 2
            elif args[i] == '--dist' and i + 1 < len(args):
                distance = float(args[i + 1]); i += 2
            else:
                i += 1

        ok = self.client.swipe(direction, duration, distance)
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_sw(self, args: List[str]) -> bool:
        return self._cmd_swipe(args)

    def _cmd_press(self, args: List[str]) -> bool:
        """p <key> - press a key (back/home/recents)."""
        if not args:
            self._print_error("Usage: p <back|home|recents>")
            return False
        ok = self.client.press_key(args[0])
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_p(self, args: List[str]) -> bool:
        return self._cmd_press(args)

    def _cmd_back(self, args: List[str]) -> bool:
        """b - press Back."""
        ok = self.client.press_back()
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_b(self, args: List[str]) -> bool:
        return self._cmd_back(args)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_waitfor(self, args: List[str]) -> bool:
        """wf <text> [--t N] - wait for an element to appear."""
        if not args or args[0].startswith('--'):
            self._print_error("Usage: wf <text> [--t N]")
            return False

        text = args[0]
        timeout = self._timeout
        i = 1
        while i < len(args):
            if args[i] == '--t' and i + 1 < len(args):
                timeout = int(args[i + 1]); i += 2
            else:
                i += 1

        print(f"  Waiting for: {text!r} (timeout={timeout}s)...")
        elem = self.client.wait_for_element(text=text, timeout=timeout)
        if elem:
            print(f"  ✓ Found refId={elem.get('refId')}: "
                  f"text={elem.get('text', '')!r} "
                  f"at center=({elem.get('x')}, {elem.get('y')})")
            self._invalidate_tree()
            return True
        else:
            print(f"  ✗ Timeout after {timeout}s")
            return False

    def _cmd_wf(self, args: List[str]) -> bool:
        return self._cmd_waitfor(args)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_get(self, args: List[str]) -> bool:
        """g <refId> <attr> - read an element attribute."""
        if len(args) < 2:
            self._print_error("Usage: g <refId> <attr>  (attr: text/class/bounds/x/y/xpath/...)")
            return False
        refId = int(args[0])
        attr = args[1]
        value = self.client.get_attribute(refId, attr)
        return value is not None

    def _cmd_g(self, args: List[str]) -> bool:
        return self._cmd_get(args)

    def _cmd_screenshot(self, args: List[str]) -> bool:
        """s [path] - capture a screenshot."""
        path = args[0] if args else None
        result = self.client.screenshot(output_path=path)
        if result:
            print(f"  ✓ {result}")
            return True
        return False

    def _cmd_s(self, args: List[str]) -> bool:
        return self._cmd_screenshot(args)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_uitree(self, args: List[str]) -> bool:
        """ux [path] [--all] - print or save the current UI tree XML."""
        output_path: Optional[str] = None
        visible_only = True
        for arg in args:
            if arg == "--all":
                visible_only = False
            elif output_path is None:
                output_path = arg
            else:
                self._print_error("Usage: ux [path] [--all]")
                return False

        xml_text = self.client.get_ui_tree_xml(force_refresh=True, visible_only=visible_only)
        if not xml_text:
            self._print_error("Failed to fetch UI tree XML")
            return False

        if output_path:
            destination = os.path.expanduser(output_path)
            try:
                with open(destination, "w", encoding="utf-8") as handle:
                    handle.write(xml_text)
            except OSError as exc:
                self._print_error(f"Failed to save UI tree XML: {exc}")
                return False
            print(f"  ✓ UI tree XML saved to {destination}")
            return True

        print(xml_text)
        return True

    def _cmd_ux(self, args: List[str]) -> bool:
        return self._cmd_uitree(args)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_launch(self, args: List[str]) -> bool:
        """la <package> - launch an app."""
        if not args:
            self._print_error("Usage: la <package>")
            return False
        package = args[0]
        ok = self.client.launch_app(package)
        if ok:
            self._invalidate_tree()
        return ok

    def _cmd_la(self, args: List[str]) -> bool:
        return self._cmd_launch(args)

    def _cmd_apps(self, args: List[str]) -> bool:
        """apps - list launcher apps."""
        apps = self.client.list_launcher_apps()
        if apps is None:
            self._print_error(
                "Failed to fetch launcher apps. Check the connection hints above "
                "and confirm the service is healthy."
            )
            return False
        if not apps:
            print("  No launcher apps returned.")
            return True
        print("Launcher apps:")
        for index, app in enumerate(apps, start=1):
            print(f"  [{index:02d}] {_format_launcher_app(app)}")
        return True

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_raw(self, args: List[str]) -> bool:
        """raw - toggle raw JSON output."""
        self._raw_output = not self._raw_output
        print(f"  Raw JSON output: {'ON' if self._raw_output else 'OFF'}")
        return True

    def _cmd_vars(self, args: List[str]) -> bool:
        """vars - show session variables."""
        print("  Session:")
        print(f"    URL:      {self.client.base_url}")
        print(f"    Token:    {'SET' if self.client.token else 'NOT SET'}")
        print(f"    Timeout:  {self._timeout}s")
        print(f"    RawJSON:  {'ON' if self._raw_output else 'OFF'}")
        print(f"    Cached:   {'YES' if self._tree is not None else 'NO'}")
        if self._tree:
            print(f"    Elements: {len(self._tree)}")
        return True

    def _cmd_set(self, args: List[str]) -> bool:
        """set <url|token|timeout> <value> - set a session variable."""
        if len(args) < 2:
            self._print_error("Usage: set <url|token|timeout> <value>")
            return False
        key, value = args[0], ' '.join(args[1:])
        if key == 'url':
            trimmed_value = value.strip()
            if not trimmed_value:
                self._print_error("URL cannot be empty")
                return False
            self.client = AgentAndroidClient(trimmed_value, token=self.client.token)
            print(f"  URL set to: {trimmed_value}")
            try:
                save_url_to_config(trimmed_value)
                print(f"  Persisted to {CONFIG_FILE_PATH}")
            except OSError as exc:
                print(f"  Warning: could not save URL to {CONFIG_FILE_PATH}: {exc}", file=sys.stderr)
        elif key == 'token':
            decoded = self._decode_input_payload(value.strip())
            normalized = decoded.strip()
            token = normalized or None
            self.client = AgentAndroidClient(self.client.base_url, token=token)
            if token:
                print("  Token set for protected API access")
            else:
                print("  Token cleared")
            try:
                save_token_to_config(token)
                print(f"  Persisted to {CONFIG_FILE_PATH}")
            except OSError as exc:
                print(f"  Warning: could not save token to {CONFIG_FILE_PATH}: {exc}", file=sys.stderr)
        elif key == 'timeout':
            self._timeout = int(value)
            print(f"  Timeout set to: {self._timeout}s")
        else:
            self._print_error(f"Unknown variable: {key!r}.  Available: url, token, timeout")
            return False
        return True

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _cmd_help(self, args: List[str]) -> bool:
        """h - show help."""
        self._print_help()
        return True

    def _cmd_h(self, args: List[str]) -> bool:
        return self._cmd_help(args)

    def _cmd_quit(self, args: List[str]) -> Any:
        """q - quit."""
        return _REPL_EXIT

    def _cmd_q(self, args: List[str]) -> Any:
        return self._cmd_quit(args)

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------

    def _print_help(self):
        lines = [
            "",
            "  agent-android REPL v5.4 - Command Reference",
            "  " + "-" * 67,
            "  Local-first beta path: the phone hosts the HTTP service and the desktop",
            "  connects directly over LAN. If calls fail, first check whether the",
            "  AIVane app or phone-side API service has exited.",
            "",
            "  Browse",
            "    health            Check the /health endpoint",
            "    l [n]             List elements (show the first n entries, center coordinates, reuse cache)",
            "    ss                Refresh the tree and list again (force refresh)",
            "    f <text>          Filter elements by text or content description",
            "    id <resourceId>   Filter by resourceId",
            "    ref <refId>       Show detailed information for refId",
            "    node <refId>      Print the raw <node .../> XML snippet for a refId",
            "    x <refId>         Show XPath candidates for refId (validated by runtime match count)",
            "    mx <ids>          Find shared XPath candidates for multiple refIds",
            "                       Example: mx 13,14",
            "                       Example: mx 13,14,15",
            "    xx <refId>        Tap via a unique XPath candidate automatically (refuses non-unique candidates)",
            "    vx <xpath> [idx]  Validate the runtime match count for an XPath",
            "                       Use 'vx <xpath> <idx>' to inspect one runtime match in detail",
            "    vn <xpath>        Print the raw <node .../> XML snippets for XPath matches",
            "",
            "  Interact",
            "    t <refId>         Tap the element with refId using its center point",
            "    tx <xpath>        Tap an element by XPath",
            "                       Example: tx //Button[@text='Search']",
            "                       Example: tx //EditText[@text='Search']",
            "    i <refId> <text>  Input text into refId",
            "                       Use '--clear' or an empty string ('\"\"') to clear the field",
            "    ix <xpath> <text> Input text by XPath",
            "                       Use '--clear' or 'ix <xpath> --' to clear the field",
            "                       Example: ix //EditText[@text='Search'] hello",
            "    sw <d|u|l|r> [--dur N] [--dist N]",
            "                       Swipe (d=down, u=up, l=left, r=right)",
            "    p <key>           Press a key (back/home/recents)",
            "    b                  Press Back",
            "",
            "  Wait",
            "    wf <text> [--t N] Wait for an element to appear (default timeout: 30s)",
            "",
            "  Info",
            "    g <refId> <attr> Read an attribute from refId",
            "                       (text/class/bounds/x/y/xpath/selector/...)",
            "    s [path]          Capture a screenshot (no argument = auto filename)",
            "    ux [path] [--all] Print the current UI tree XML or save it to a file",
            "                       Use --all to include off-screen nodes in the XML dump",
            "    la <package>      Launch an app (for example com.xingin.xhs)",
            "",
            "  Session",
            "    raw                Toggle raw JSON output",
            "    vars               Show session variables",
            "    apps               List launcher apps",
            "    set url <url>      Switch the server URL",
            "    set token <value>  Save the shared token (--clear to remove it)",
            "    set timeout <N>    Set the default wait timeout (seconds)",
            "",
            "  Exit",
            "    q                  Quit the REPL",
            "    h                  Show this help",
            "",
            "  Shortcuts: l->list, ss->snapshot, t->tap, tx->tapx, xx->tapx-auto,",
            "              i->input, ix->inputx, sw->swipe, p->press, b->back,",
            "              wf->waitfor, g->get, s->screenshot, ux->uitree, la->launch, hl->health, vx->validatex,",
            "              mx->multixpath,",
            "              ref->ref, node->node, x->xpath, vn->validatenodes, f->find, h->help, q->quit",
            "",
            "  Troubleshooting",
            "    1. health",
            "    2. apps",
            "    3. ss",
            "    If health fails, verify the phone app is still running, the URL/IP is current,",
            "    and the desktop is still on the same LAN.",
            "",
        ]
        print('\n'.join(lines))

    def _print_banner(self):
        print()
        print("  agent-android REPL v5.4  -  Android UI Automation REPL")
        print(f"  Server: {self.client.base_url}")
        print("  Type 'h' for help, 'q' to quit.")
        print()

    def _print_error(self, msg: str):
        print(f"  [!] {msg}", file=sys.stderr)

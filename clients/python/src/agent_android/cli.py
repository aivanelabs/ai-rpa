from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

from . import __version__
from .client import AgentAndroidClient
from .config import TOKEN_ENV_VAR, require_base_url, resolve_api_token
from .formatting import print_tree
from .repl import AriaReplSession

EPILOG = """AIVane Android REPL CLI helper for agent-android.

The phone hosts the beta HTTP service locally and this client connects
directly to http://<device-ip>:8080. The public path is local-first and
does not require a cloud relay for the basic smoke flow.

Quick start:
    agent-android --repl --url http://<device-ip>:8080
    agent-android --health --url http://<device-ip>:8080
    agent-android --health --url http://<device-ip>:8080 --token YOUR_TOKEN
    agent-android --apps --url http://<device-ip>:8080
    agent-android --list --url http://<device-ip>:8080

One-off examples:
    agent-android --launch com.example.app --url http://<device-ip>:8080
    agent-android --tap 7 --url http://<device-ip>:8080
    agent-android --input 7 "hello world" --url http://<device-ip>:8080
    agent-android --template template.json --url http://<device-ip>:8080
    agent-android --swipe up --url http://<device-ip>:8080
    agent-android --screenshot --url http://<device-ip>:8080
    agent-android --wait-for Search --timeout 30 --url http://<device-ip>:8080
    agent-android --xpath 7 --url http://<device-ip>:8080
    agent-android --validate-xpath "//Button[@text='OK']" --url http://<device-ip>:8080
    agent-android --tap-xpath "//Button[@text='OK']" --url http://<device-ip>:8080
    agent-android --ui-tree ui.xml --url http://<device-ip>:8080

REPL quick reference:
    health / hl               Check the /health endpoint
    l [n] / list [n]          List elements (reuse cache)
    ss / snapshot             Force-refresh the UI tree
    apps                      List launcher apps
    ref <N>                   Dump one element
    node <N>                  Print the raw <node .../> XML snippet for refId=N
    x <N>                     Print XPath candidates for refId=N
    mx <ids>                  Find shared XPath candidates for multiple refIds
    vx <xpath> [idx]          Validate XPath match count and inspect one runtime match
    vn <xpath>                Print matched <node .../> snippets using runtime XPath results
    t <N>                     Tap element with refId=N
    tx <xpath>                Tap by XPath locator
    i <N> <text>              Enter text into refId=N (--clear or "" clears it)
    ix <xpath> <text>         Enter text via XPath locator
    sw <d|u|l|r>              Swipe direction (supports --dur/--dist)
    wf <text>                 Wait for element text (use --t to override timeout)
    g <N> <attr>              Inspect an attribute for refId=N
    s [path]                  Capture screenshot
    ux [path] [--all]         Print or save the current UI tree XML
    la <pkg>                  Launch an app by package name
    p <key>                   Press a system key (back/home/recents)
    b                         Navigate back
    vars                      Show session variables
    set url <u>               Switch the server URL
    set token <v>             Save or clear the shared token
    set timeout <N>           Adjust the default timeout
    h                         Show REPL help
    q                         Quit the REPL

Token:
    If the phone requires a shared token, use one of:
    - --token YOUR_TOKEN
    - Set environment variable {env_var}
    - In REPL: set token YOUR_TOKEN

Troubleshooting:
    If Python calls stop working, first check whether the AIVane app or
    the phone-side API service has exited, then retry /health.
""".format(env_var=TOKEN_ENV_VAR)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-android",
        description="agent-android v0.1 - local-first Android UI automation over the public AIVane REPL surface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
    )

    parser.add_argument("--repl", "-i", action="store_true", help="Enter REPL interactive mode (recommended)")
    parser.add_argument("--url", "-u", default=None, help="AIVane server URL (command-line overrides saved config)")
    parser.add_argument("--token", default=None, help=f"Shared token for protected device access. Overrides {TOKEN_ENV_VAR} and saved config.")
    parser.add_argument("--wait", "-w", type=int, default=0, help="Wait N seconds before fetching ARIA tree")
    parser.add_argument("--no-cache", action="store_true", help="Force refresh ARIA tree (bypass cache)")
    parser.add_argument("--wait-for", type=str, metavar="TEXT", help="Wait for element with text matching to appear")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Max wait time for --wait-for (default: 30s)")
    parser.add_argument("--include-offscreen", action="store_true", help="Include off-screen elements in the returned tree")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", "-l", action="store_true", help="List all elements")
    group.add_argument("--screenshot", "-s", nargs="?", const="_auto_", metavar="OUTPUT_PATH", help="Capture screenshot. Optional: output file path")
    group.add_argument("--swipe", type=str, metavar="DIRECTION", help="Swipe direction: up/down/left/right")
    group.add_argument("--tap", type=int, metavar="REFID", help="Tap element by refId")
    group.add_argument("--input", nargs=2, metavar=("REFID", "TEXT"), help="Input text to element by refId")
    group.add_argument("--template", metavar="TEMPLATE_JSON", help="Execute a template JSON file via /execute")
    group.add_argument("--launch", "-a", type=str, metavar="PACKAGE", help="Launch app")
    group.add_argument("--health", action="store_true", help="Check service health from /health")
    group.add_argument("--back", action="store_true", help="Press back button")
    group.add_argument("--apps", action="store_true", help="List launcher apps from /apps")
    group.add_argument("--press", type=str, metavar="KEY", help="Press key: back / home / recents")
    group.add_argument("--get-attr", nargs=2, metavar=("REFID", "ATTR"), help="Get element attribute by refId (text/className/bounds/...)")
    group.add_argument("--refId", "-r", type=int, metavar="N", help="Get element details")
    group.add_argument("--node", type=int, metavar="REFID", help="Print raw UI-tree node XML for refId")
    group.add_argument("--xpath", "-x", type=int, metavar="N", help="Show XPath candidates for refId")
    group.add_argument("--multi-xpath", "--multixpath", dest="multi_xpath", metavar="REFIDS", help="Find shared XPath candidates for comma/space-separated refIds")
    group.add_argument("--tap-xpath-auto", type=int, metavar="REFID", help="Tap via a unique auto-generated XPath candidate")
    group.add_argument("--validate-xpath", "--validatex", dest="validate_xpath", metavar="XPATH", help="Validate XPath runtime match count")
    group.add_argument("--xpath-nodes", "--validatenodes", dest="xpath_nodes", metavar="XPATH", help="Print raw UI-tree node XML for XPath matches")
    group.add_argument("--tap-xpath", "--tapx", dest="tap_xpath", metavar="XPATH", help="Tap by XPath locator")
    group.add_argument("--input-xpath", "--inputx", dest="input_xpath", nargs=2, metavar=("XPATH", "TEXT"), help="Input text by XPath locator")
    group.add_argument("--ui-tree", "--uitree", dest="ui_tree", nargs="?", const="_stdout_", metavar="OUTPUT_PATH", help="Print or save current UI tree XML")
    group.add_argument("--id", type=str, metavar="RESOURCE_ID", help="Query by resourceId")
    group.add_argument("--text", type=str, metavar="TEXT", help="Query by text")
    group.add_argument("--inputs", action="store_true", help="List all input fields")

    parser.add_argument("--duration", type=int, default=300, help="Swipe duration in ms (default: 300)")
    parser.add_argument("--distance", type=float, default=0.5, help="Swipe distance ratio 0.0-1.0 (default: 0.5)")
    parser.add_argument("--quality", "-q", type=int, default=80, help="Screenshot quality 1-100 (default: 80)")
    parser.add_argument("--match-index", type=int, help="Match index for --validate-xpath detail inspection")
    parser.add_argument("--ui-tree-all", action="store_true", help="Include off-screen nodes for --ui-tree")
    parser.add_argument("--filter", "-f", type=str, help="Filter elements by text or content description")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON")
    parser.add_argument("--output", "-o", type=str, help="Save ARIA tree to JSON file")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _load_template_payload(path_str: str) -> Dict[str, Any]:
    template_path = os.path.expanduser(path_str)
    try:
        with open(template_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"Template file not found: {template_path}", file=sys.stderr)
        raise SystemExit(1)
    except json.JSONDecodeError as exc:
        print(f"Template JSON is invalid: {exc}", file=sys.stderr)
        raise SystemExit(1)


def _session_for_client(
    client: AgentAndroidClient,
    *,
    elements: Optional[List[Dict[str, Any]]] = None,
    raw_output: bool = False,
    timeout: int = 30,
) -> AriaReplSession:
    return AriaReplSession.from_client(
        client,
        tree=elements,
        raw_output=raw_output,
        timeout=timeout,
    )


def _exit_with_repl_result(result: Any) -> None:
    raise SystemExit(0 if result else 1)


def _split_ref_ids(value: str) -> List[str]:
    return [part for part in value.replace(",", " ").split() if part]


def _run_direct_commands(args: argparse.Namespace, client: AgentAndroidClient) -> None:
    session = _session_for_client(client, raw_output=args.raw, timeout=args.timeout)
    if args.template:
        payload = _load_template_payload(args.template)
        response = client.execute_template_payload(payload)
        if response is None:
            print("Failed to execute template payload. Check the connection hints above.", file=sys.stderr)
            raise SystemExit(1)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        raise SystemExit(0 if response.get("success") is True else 1)
    if args.health:
        session._raw_output = True
        _exit_with_repl_result(session._cmd_health([]))
    if args.back:
        _exit_with_repl_result(session._cmd_back([]))
    if args.press:
        _exit_with_repl_result(session._cmd_press([args.press]))
    if args.launch:
        _exit_with_repl_result(session._cmd_launch([args.launch]))
    if args.apps:
        _exit_with_repl_result(session._cmd_apps([]))
    if args.screenshot is not None:
        output_path = None if args.screenshot == "_auto_" else args.screenshot
        raise SystemExit(0 if client.screenshot(output_path=output_path, quality=args.quality) else 1)
    if args.swipe:
        _exit_with_repl_result(
            session._cmd_swipe([args.swipe, "--dur", str(args.duration), "--dist", str(args.distance)])
        )
    if args.tap is not None:
        _exit_with_repl_result(session._cmd_tap([str(args.tap)]))
    if args.input:
        _exit_with_repl_result(session._cmd_input([args.input[0], args.input[1]]))
    if args.tap_xpath:
        _exit_with_repl_result(session._cmd_tapx([args.tap_xpath]))
    if args.input_xpath:
        _exit_with_repl_result(session._cmd_inputx([args.input_xpath[0], args.input_xpath[1]]))
    if args.validate_xpath:
        command_args = [args.validate_xpath]
        if args.match_index is not None:
            command_args.append(str(args.match_index))
        _exit_with_repl_result(session._cmd_validatex(command_args))
    if args.xpath_nodes:
        _exit_with_repl_result(session._cmd_validatenodes([args.xpath_nodes]))
    if args.ui_tree is not None:
        command_args: List[str] = []
        if args.ui_tree != "_stdout_":
            command_args.append(args.ui_tree)
        if args.ui_tree_all:
            command_args.append("--all")
        _exit_with_repl_result(session._cmd_uitree(command_args))


def _run_wait_command(args: argparse.Namespace, client: AgentAndroidClient) -> None:
    if not args.wait_for:
        return
    print(f"Waiting for element '{args.wait_for}' (timeout={args.timeout}s)...", file=sys.stderr)
    elem = client.wait_for_element(text=args.wait_for, timeout=args.timeout)
    if elem:
        ref_id = elem.get("refId")
        print(
            f"refId={ref_id} found: text='{elem.get('text', '')}' "
            f"class={elem.get('simpleClassName', '')} "
            f"at ({elem.get('x', '?')}, {elem.get('y', '?')})"
        )
        raise SystemExit(0)
    raise SystemExit(1)


def _dump_input_elements(
    client: AgentAndroidClient,
    elements: List[Dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    if not args.inputs:
        return
    input_elements = client.find_input_elements(elements)
    if not input_elements:
        print("No input fields found")
        raise SystemExit(0)
    print("\n" + "=" * 70)
    print(f"  Input Fields - {len(input_elements)} elements")
    print("=" * 70)
    for elem in input_elements:
        ref_id = elem.get("refId", "?")
        text = elem.get("text", "") or elem.get("contentDesc", "") or "-"
        cls = elem.get("simpleClassName", "")
        x, y = elem.get("x", "?"), elem.get("y", "?")
        editable = "editable" if elem.get("editable") else ""
        focusable = "focusable" if elem.get("focusable") else ""
        print(
            "  [{:2d}] {:<28} {:<18} ({:4s},{:4s}) [{}, {}]".format(
                ref_id,
                str(text)[:28],
                cls,
                str(x),
                str(y),
                editable,
                focusable,
            )
        )
    print("=" * 70)
    raise SystemExit(0)


def _handle_tree_queries(
    client: AgentAndroidClient,
    elements: List[Dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    session = _session_for_client(
        client,
        elements=elements,
        raw_output=args.raw,
        timeout=args.timeout,
    )
    results = elements

    if args.get_attr:
        _exit_with_repl_result(session._cmd_get([args.get_attr[0], args.get_attr[1]]))

    if args.refId is not None:
        _exit_with_repl_result(session._cmd_ref([str(args.refId)]))

    if args.node is not None:
        _exit_with_repl_result(session._cmd_node([str(args.node)]))

    if args.xpath is not None:
        _exit_with_repl_result(session._cmd_xpath([str(args.xpath)]))

    if args.multi_xpath:
        _exit_with_repl_result(session._cmd_multixpath(_split_ref_ids(args.multi_xpath)))

    if args.tap_xpath_auto is not None:
        _exit_with_repl_result(session._cmd_xx([str(args.tap_xpath_auto)]))

    if args.id:
        if not args.raw and not args.filter:
            _exit_with_repl_result(session._cmd_id([args.id]))
        results = client.find_by_resourceId(elements, args.id)
        if not results:
            print(f"No elements with resourceId={args.id}")
    elif args.text:
        if not args.raw and not args.filter:
            _exit_with_repl_result(session._cmd_find([args.text]))
        results = client.find_by_text(elements, args.text)
        if not results:
            print(f"No elements with text containing '{args.text}'")
    else:
        args.list = True

    if args.list or args.text or args.id:
        if args.list and not args.raw and not args.filter:
            _exit_with_repl_result(session._cmd_list([]))
        if args.raw:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_tree(results, args.filter, client.get_current_package_name())


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.match_index is not None and not args.validate_xpath:
        parser.error("--match-index requires --validate-xpath")
    if args.ui_tree_all and args.ui_tree is None:
        parser.error("--ui-tree-all requires --ui-tree")
    url = require_base_url(args.url)
    token = resolve_api_token(args.token)

    if args.repl:
        history_path = os.path.expanduser("~/.agent-android-history")
        session = AriaReplSession(url=url, token=token, history_file=history_path)
        session.run()
        return 0

    client = AgentAndroidClient(url, token=token)
    _run_direct_commands(args, client)
    _run_wait_command(args, client)

    print("Fetching ARIA tree...", file=sys.stderr)
    elements = client.get_ui_elements(
        wait=args.wait,
        force_refresh=args.no_cache,
        visible_only=not args.include_offscreen,
    )
    if not elements:
        print("Failed to get ARIA tree. Check the connection hints above.", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(elements, handle, ensure_ascii=False, indent=2)
        print(f"ARIA tree saved to: {args.output}", file=sys.stderr)

    _dump_input_elements(client, elements, args)
    _handle_tree_queries(client, elements, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

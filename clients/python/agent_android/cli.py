from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List

from .client import AgentAndroidClient
from .config import TOKEN_ENV_VAR, require_base_url, resolve_api_token
from .formatting import _format_launcher_app, format_element, print_tree
from .repl import AriaReplSession

EPILOG = """AIVane Android REPL CLI helper for agent-android.

The phone hosts the beta HTTP service locally and this client connects
directly to http://<device-ip>:8080. The public path is local-first and
does not require a cloud relay for the basic smoke flow.

Quick start:
    python agent-android.py --repl --url http://<device-ip>:8080
    python agent-android.py --health --url http://<device-ip>:8080
    python agent-android.py --health --url http://<device-ip>:8080 --token YOUR_TOKEN
    python agent-android.py --apps --url http://<device-ip>:8080
    python agent-android.py --list --url http://<device-ip>:8080

One-off examples:
    python agent-android.py --launch com.example.app --url http://<device-ip>:8080
    python agent-android.py --tap 7 --url http://<device-ip>:8080
    python agent-android.py --input 7 "hello world" --url http://<device-ip>:8080
    python agent-android.py --template template.json --url http://<device-ip>:8080
    python agent-android.py --swipe up --url http://<device-ip>:8080
    python agent-android.py --screenshot --url http://<device-ip>:8080
    python agent-android.py --wait-for Search --timeout 30 --url http://<device-ip>:8080

REPL quick reference:
    health / hl               Check the /health endpoint
    l [n] / list [n]          List elements (reuse cache)
    ss / snapshot             Force-refresh the UI tree
    apps                      List launcher apps
    ref <N>                   Dump one element
    x <N>                     Print XPath candidates for refId=N
    vx <xpath> [idx]          Validate XPath match count and inspect one runtime match
    t <N>                     Tap element with refId=N
    tx <xpath>                Tap by XPath locator
    i <N> <text>              Enter text into refId=N (--clear or "" clears it)
    ix <xpath> <text>         Enter text via XPath locator
    sw <d|u|l|r>              Swipe direction (supports --dur/--dist)
    wf <text>                 Wait for element text (use --t to override timeout)
    g <N> <attr>              Inspect an attribute for refId=N
    s [path]                  Capture screenshot
    la <pkg>                  Launch an app by package name
    p <key>                   Press a system key
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
    group.add_argument("--press", type=str, metavar="KEY", help="Press key: back / home / menu / enter / delete / power")
    group.add_argument("--get-attr", nargs=2, metavar=("REFID", "ATTR"), help="Get element attribute by refId (text/className/bounds/...)")
    group.add_argument("--refId", "-r", type=int, metavar="N", help="Get element details")
    group.add_argument("--xpath", "-x", type=int, metavar="N", help="Get element XPath")
    group.add_argument("--id", type=str, metavar="RESOURCE_ID", help="Query by resourceId")
    group.add_argument("--text", type=str, metavar="TEXT", help="Query by text")
    group.add_argument("--inputs", action="store_true", help="List all input fields")

    parser.add_argument("--duration", type=int, default=300, help="Swipe duration in ms (default: 300)")
    parser.add_argument("--distance", type=float, default=0.5, help="Swipe distance ratio 0.0-1.0 (default: 0.5)")
    parser.add_argument("--quality", "-q", type=int, default=80, help="Screenshot quality 1-100 (default: 80)")
    parser.add_argument("--filter", "-f", type=str, help="Filter elements by text or content description")
    parser.add_argument("--raw", action="store_true", help="Output raw JSON")
    parser.add_argument("--output", "-o", type=str, help="Save ARIA tree to JSON file")
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


def _run_direct_commands(args: argparse.Namespace, client: AgentAndroidClient) -> None:
    if args.template:
        payload = _load_template_payload(args.template)
        response = client.execute_template_payload(payload)
        if response is None:
            print("Failed to execute template payload. Check the connection hints above.", file=sys.stderr)
            raise SystemExit(1)
        print(json.dumps(response, indent=2, ensure_ascii=False))
        raise SystemExit(0 if response.get("success") is True else 1)
    if args.health:
        health = client.get_health()
        if health is None:
            print("Failed to fetch health. Check the connection hints above.", file=sys.stderr)
            raise SystemExit(1)
        print(json.dumps(health, indent=2, ensure_ascii=False))
        raise SystemExit(0)
    if args.back:
        raise SystemExit(0 if client.press_back() else 1)
    if args.press:
        raise SystemExit(0 if client.press_key(args.press) else 1)
    if args.launch:
        raise SystemExit(0 if client.launch_app(args.launch) else 1)
    if args.apps:
        apps = client.list_launcher_apps()
        if apps is None:
            print(
                "Failed to fetch launcher apps. Check the connection hints above "
                "and confirm the service is healthy.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        if not apps:
            print("No launcher apps returned.")
            raise SystemExit(0)
        print("Launcher apps:")
        for index, app in enumerate(apps, start=1):
            print(f"  [{index:02d}] {_format_launcher_app(app)}")
        raise SystemExit(0)
    if args.screenshot is not None:
        output_path = None if args.screenshot == "_auto_" else args.screenshot
        raise SystemExit(0 if client.screenshot(output_path=output_path, quality=args.quality) else 1)
    if args.swipe:
        success = client.swipe(direction=args.swipe, duration=args.duration, distance=args.distance)
        raise SystemExit(0 if success else 1)
    if args.tap is not None:
        raise SystemExit(0 if client.tap_element(args.tap) else 1)
    if args.input:
        ref_id = int(args.input[0])
        raise SystemExit(0 if client.input_to_element(ref_id, args.input[1]) else 1)


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
    results = elements

    if args.get_attr:
        ref_id = int(args.get_attr[0])
        value = client.get_attribute(ref_id, args.get_attr[1])
        if value is not None:
            print(value)
            raise SystemExit(0)
        raise SystemExit(1)

    if args.refId:
        elem = client.find_by_refId(elements, args.refId)
        if elem:
            print(format_element(elem))
            return
        print(f"Element with refId={args.refId} not found")
        raise SystemExit(1)

    if args.xpath:
        elem = client.find_by_refId(elements, args.xpath)
        if elem:
            print(elem.get("xpath", ""))
            return
        print(f"Element with refId={args.xpath} not found")
        raise SystemExit(1)

    if args.id:
        results = client.find_by_resourceId(elements, args.id)
        if not results:
            print(f"No elements with resourceId={args.id}")
    elif args.text:
        results = client.find_by_text(elements, args.text)
        if not results:
            print(f"No elements with text containing '{args.text}'")
    else:
        args.list = True

    if args.list or args.text or args.id:
        if args.raw:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_tree(results, args.filter, client.get_current_package_name())


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
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
    elements = client.get_ui_elements(wait=args.wait, force_refresh=args.no_cache)
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

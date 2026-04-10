from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional, Tuple


def _terminal_text(value: Any) -> str:
    text = str(value)
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def _first_text(app: Dict[str, Any], keys: Tuple[str, ...], default: str = "") -> str:
    for key in keys:
        value = app.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return default


def _format_launcher_app(app: Dict[str, Any]) -> str:
    label = _first_text(app, ("label", "name", "appName", "title"), "<unnamed>")
    package = _first_text(app, ("package", "packageName", "pkg"), "<unknown>")
    activity = _first_text(app, ("activity", "launcherActivity", "mainActivity"), "-")
    extras = []
    if app.get("launcher", True) is False:
        extras.append("launcher=false")
    enabled = app.get("enabled")
    if isinstance(enabled, bool):
        extras.append("enabled" if enabled else "disabled")
    extra_text = f" ({', '.join(extras)})" if extras else ""
    return _terminal_text(f"{label} - {package}{extra_text} [{activity}]")


def _short_class_name(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "-"
    return text.rsplit(".", 1)[-1]


def format_status(elem: Dict[str, Any]) -> str:
    status: List[str] = []
    if elem.get("clickable"):
        status.append("clickable")
    if elem.get("focusable"):
        status.append("focusable")
    if elem.get("isInput"):
        status.append("input")
    return ", ".join(status) if status else "none"


def format_detail_card(title: str, rows: List[Tuple[str, Any]]) -> str:
    lines = []

    lines.append("+" + "-" * 60 + "+")
    lines.append("| {}".format(_terminal_text(title)))
    lines.append("|" + "-" * 61 + "|")
    for label, value in rows:
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        lines.append("| {}: {}".format(label, _terminal_text(text)))
    lines.append("+" + "-" * 60 + "+")
    return "\n".join(lines)


def format_element(elem: Dict[str, Any]) -> str:
    ref_id = elem.get("refId", "?")
    text = elem.get("text", "")
    desc = elem.get("contentDesc", "")
    resource_id = elem.get("resourceId", "")
    cls = _short_class_name(elem.get("simpleClassName") or elem.get("className"))
    bounds = elem.get("bounds", "")
    x, y = elem.get("x", "?"), elem.get("y", "?")

    rows: List[Tuple[str, Any]] = []
    if text:
        rows.append(("text", text[:50]))
    if desc:
        rows.append(("contentDesc", desc[:50]))
    if resource_id:
        rows.append(("resourceId", resource_id))
    rows.extend([
        ("className", cls),
        ("bounds", bounds),
        ("position", f"({x}, {y})"),
        ("status", format_status(elem)),
    ])
    return format_detail_card(f"refId: {ref_id}", rows)


def print_tree(
    elements: List[Dict[str, Any]],
    filter_text: Optional[str] = None,
    package_name: Optional[str] = None,
) -> None:
    if not elements:
        print("No elements found")
        return

    if filter_text:
        lowered = filter_text.lower()
        elements = [
            elem
            for elem in elements
            if lowered in (elem.get("text", "") or "").lower()
            or lowered in (elem.get("contentDesc", "") or "").lower()
        ]

    print()
    print("=" * 70)
    print("  AIVane ARIA Tree - {} elements".format(len(elements)))
    if package_name:
        print("  Current package: {}".format(_terminal_text(package_name)))
    print("=" * 70)

    for elem in elements:
        ref_id = elem.get("refId", "?")
        text = elem.get("text", "") or elem.get("contentDesc", "") or "-"
        cls = elem.get("simpleClassName", "")
        x, y = elem.get("x", "?"), elem.get("y", "?")

        flags = []
        if elem.get("clickable"):
            flags.append("click")
        if elem.get("focusable"):
            flags.append("focus")
        flag_str = "[{}]".format(",".join(flags)) if flags else ""
        display_text = text[:25] + "..." if len(str(text)) > 25 else str(text)
        display_text = _terminal_text(display_text)
        cls_display = _terminal_text(cls)
        print(
            "  [{:2d}] {:<28} {:<18} ({:4s},{:4s}) {}".format(
                ref_id,
                display_text,
                cls_display,
                str(x),
                str(y),
                flag_str,
            )
        )

    print("=" * 70)
    print()

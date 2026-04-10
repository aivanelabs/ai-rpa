from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .snapshot import find_snapshot_element, load_snapshot, save_snapshot
from .transport import _build_http_opener

class AgentAndroidClient:
    """Client for the AIVane Android REPL public API."""

    def __init__(self, base_url: str, token: Optional[str] = None):
        trimmed = base_url.strip()
        if not trimmed:
            raise ValueError("Base URL is required")
        self.base_url = trimmed.rstrip('/')
        self.token = token.strip() if isinstance(token, str) and token.strip() else None
        self.execute_url = f"{self.base_url}/execute"
        self._opener = _build_http_opener(self.base_url)
        self._local_tree: Optional[List[Dict]] = None  # In-process UI tree cache
        self._local_tree_visible_only = True
        self._ui_tree_xml_cache: Optional[str] = None
        self._ui_tree_xml_cache_visible_only = True
        self._package_name_cache: Optional[str] = None
        self._snapshot: Optional[Dict[str, Any]] = None

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def _describe_transport_error(self, exc: Exception) -> str:
        """Return a short human-readable transport error summary."""
        if isinstance(exc, urllib.error.HTTPError):
            return f"HTTP {exc.code} {exc.reason}"
        if isinstance(exc, urllib.error.URLError):
            reason = exc.reason
            if isinstance(reason, TimeoutError):
                return "request timed out"
            if isinstance(reason, OSError):
                return reason.strerror or str(reason)
            if reason:
                return str(reason)
        return str(exc)

    def _print_transport_error(self, action: str, url: str, exc: Exception) -> None:
        """Print a consistent, actionable transport failure message."""
        print(f"{action} {url} failed: {self._describe_transport_error(exc)}", file=sys.stderr)

        if isinstance(exc, urllib.error.HTTPError):
            return

        print("Check these items before retrying:", file=sys.stderr)
        print("  - Confirm the AIVane app is still open on the phone; the local API service may have exited.", file=sys.stderr)
        print(f"  - Retry the local health check: curl {self.base_url}/health", file=sys.stderr)
        print("  - Confirm the phone and computer are still on the same LAN and the IP/port is still correct.", file=sys.stderr)

    def _build_headers(
        self,
        *,
        content_type: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if content_type:
            headers["Content-Type"] = content_type
        if user_agent:
            headers["User-Agent"] = user_agent
        if self.token:
            headers["x-api-token"] = self.token
        return headers

    def _api_call(self, template: Dict) -> Optional[Dict]:
        """Send an API request."""
        try:
            data = json.dumps(template, ensure_ascii=False).encode('utf-8')
            req = urllib.request.Request(
                self.execute_url,
                data=data,
                headers=self._build_headers(content_type="application/json"),
                method='POST'
            )
            with self._opener.open(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            self._print_transport_error("POST", self.execute_url, e)
            return None
        except Exception as e:
            print(f"POST {self.execute_url} failed: {e}", file=sys.stderr)
            return None

    def execute_template_payload(self, payload: Dict[str, Any]) -> Optional[Dict]:
        """Execute a raw template payload via /execute."""
        return self._api_call(payload)

    def _get_raw(self, path: str, params: Dict = None) -> Optional[Dict]:
        """Send a GET request for endpoints such as /health, /screenshot, and /download."""
        url = self.base_url + path
        if params:
            url += '?' + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(
                url,
                headers=self._build_headers(user_agent="agent-android.py/0.1")
            )
            with self._opener.open(req, timeout=30) as response:
                content = response.read()
                return json.loads(content.decode('utf-8'))
        except urllib.error.URLError as e:
            self._print_transport_error("GET", url, e)
            return None
        except Exception as e:
            print(f"GET {url} failed: {e}", file=sys.stderr)
            return None

    def list_launcher_apps(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieve the launcher app list from /apps."""
        result = self._get_raw("/apps")
        if not result:
            return None
        if result.get('success') is False:
            return None
        apps = result.get('apps')
        if apps is None:
            data = result.get('data')
            if isinstance(data, dict):
                apps = data.get('apps') or data.get('appList')
            elif isinstance(data, list):
                apps = data
        if isinstance(apps, dict):
            apps = [apps]
        if not isinstance(apps, list):
            return []
        return [entry for entry in apps if isinstance(entry, dict)]

    def get_health(self) -> Optional[Dict[str, Any]]:
        """Retrieve the service health payload from /health."""
        result = self._get_raw("/health")
        return result if isinstance(result, dict) else None

    def _download_binary(self, path: str, params: Dict = None) -> Optional[bytes]:
        """Download a binary payload from the Android runtime."""
        url = self.base_url + path
        if params:
            url += '?' + urllib.parse.urlencode(params)
        try:
            with self._opener.open(url, timeout=60) as response:
                return response.read()
        except urllib.error.URLError as e:
            self._print_transport_error("DOWNLOAD", url, e)
            return None
        except Exception as e:
            print(f"DOWNLOAD {url} failed: {e}", file=sys.stderr)
            return None

    def _execute_single_operation(self, template_id: str, operation_type: str,
                                  parameters: Optional[Dict[str, Any]] = None
                                  ) -> Optional[Dict]:
        """Execute a single template operation."""
        return self._api_call({
            "templateId": template_id,
            "operations": [
                {"operationType": operation_type, "parameters": parameters or {}}
            ]
        })

    def _execute_template(self, template_id: str,
                          operations: List[Dict[str, Any]],
                          output_names: Optional[List[str]] = None
                          ) -> Optional[Dict]:
        """Run a multi-step template and optionally declare output variables."""
        template: Dict[str, Any] = {
            "templateId": template_id,
            "operations": operations,
        }
        if output_names:
            template["parameters"] = [
                {"name": name, "type": "STRING", "direction": "OUTPUT"}
                for name in output_names
            ]
        return self._api_call(template)

    def _get_outputs(self, result: Optional[Dict]) -> Dict[str, Any]:
        """Extract the outputs block from a successful /execute response."""
        if not result or not result.get('success'):
            return {}
        outputs = result.get('data', {}).get('outputs', {})
        return outputs if isinstance(outputs, dict) else {}

    def _element_identity(self, elem: Dict[str, Any]) -> Tuple[Any, ...]:
        return (
            elem.get("resourceId"),
            elem.get("text"),
            elem.get("contentDesc"),
            elem.get("simpleClassName"),
            elem.get("xpath"),
        )

    def _find_in_elements(self, elements: List[Dict[str, Any]], refId: int) -> Optional[Dict[str, Any]]:
        for elem in elements:
            if elem.get("refId") == refId:
                return elem
        return None

    def _find_matching_snapshot_identity(
        self,
        snapshot_elem: Dict[str, Any],
        elements: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        wanted = self._element_identity(snapshot_elem)
        if not any(part for part in wanted):
            return None
        for elem in elements:
            if self._element_identity(elem) == wanted:
                return elem
        return None

    def _resolve_action_target(self, refId: int) -> Optional[Dict[str, Any]]:
        if self._local_tree:
            target = self._find_in_elements(self._local_tree, refId)
            if target is not None:
                return target

        snapshot = self._snapshot or load_snapshot(self.base_url)
        if snapshot:
            self._snapshot = snapshot
            snapshot_elem = find_snapshot_element(snapshot, refId)
            if snapshot_elem is not None:
                current_package = self.get_current_package_name()
                snapshot_package = snapshot.get("packageName")
                if (
                    current_package
                    and isinstance(snapshot_package, str)
                    and snapshot_package
                    and current_package != snapshot_package
                ):
                    print(
                        "RefId snapshot no longer matches the current screen: "
                        f"snapshot package={snapshot_package}, current package={current_package}. "
                        "Run --list again before tap/input.",
                        file=sys.stderr,
                    )
                    return None

                current_tree = self.get_ui_elements(force_refresh=True)
                if current_tree:
                    matched = self._find_matching_snapshot_identity(snapshot_elem, current_tree)
                    if matched is not None:
                        return matched
                return snapshot_elem

        return self._find_element_by_refId(refId, force_refresh=True)

    def _run_single_operation(self, template_id: str, operation_type: str,
                              parameters: Optional[Dict[str, Any]],
                              success_message: str,
                              failure_prefix: str) -> bool:
        """Execute an operation and print a consistent success/failure message."""
        result = self._execute_single_operation(template_id, operation_type, parameters)
        if result and result.get('success'):
            print(success_message)
            self._local_tree = None
            self._local_tree_visible_only = True
            self._ui_tree_xml_cache = None
            self._ui_tree_xml_cache_visible_only = True
            return True

        msg = result.get('errorMessage', 'Unknown error') if result else 'no response'
        print(f"{failure_prefix}: {msg}")
        return False

    def _get_coordinates(self, elem: Dict[str, Any], label: str
                         ) -> Optional[Tuple[Any, Any]]:
        """Retrieve tap coordinates, failing if none are provided."""
        x, y = elem.get('x'), elem.get('y')
        if x is None or y is None:
            print(f"{label} has no coordinates")
            return None
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and (x < 0 or y < 0):
            print(
                f"{label} resolved to off-screen coordinates ({x}, {y}). "
                "Run --list again to refresh the snapshot before tap/input.",
                file=sys.stderr,
            )
            return None
        return x, y

    def _parse_match_count(self, value: Any) -> int:
        """Convert a runtime match-count metadata value into an integer."""
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                return -1
        return -1

    def _is_input_element(self, elem: Optional[Dict[str, Any]]) -> bool:
        """Return whether the element is a direct text-input target."""
        if not isinstance(elem, dict):
            return False
        cls = (elem.get("simpleClassName") or "").strip()
        return bool(
            elem.get("editable")
            or elem.get("focusable")
            or cls in {"EditText", "AutoCompleteTextView", "TextInputEditText"}
        )

    def _describe_tree_match(self, elem: Dict[str, Any], index: int, count: int) -> Dict[str, Any]:
        return {
            "index": index,
            "count": count,
            "refId": elem.get("refId"),
            "text": elem.get("text"),
            "contentDescription": elem.get("contentDescription") or elem.get("contentDesc"),
            "className": elem.get("simpleClassName"),
            "bounds": elem.get("bounds"),
            "x": elem.get("x"),
            "y": elem.get("y"),
            "resourceId": elem.get("resourceId"),
            "isInput": self._is_input_element(elem),
        }

    def _get_xpath_match_count(self, xpath: str) -> Optional[int]:
        """Use the Android runtime evaluator to count XPath matches."""
        result = self._execute_template(
            template_id="xpath-validate-count",
            output_names=["matchCount"],
            operations=[
                {
                    "operationType": "android.element.getAll",
                    "parameters": {
                        "xpath": xpath,
                        "variableName": "matches",
                    }
                },
                {
                    "operationType": "list.process",
                    "parameters": {
                        "operation": "size",
                        "list": "${matches}",
                        "output": "matchCount",
                    }
                }
            ]
        )
        if not result:
            return None
        if not result.get('success'):
            return None
        outputs = self._get_outputs(result)
        if "matchCount" not in outputs:
            return None
        return self._parse_match_count(outputs.get("matchCount"))

    def _get_xpath_runtime_summaries(self, xpath: str) -> List[Dict[str, str]]:
        result = self._execute_template(
            template_id="xpath-runtime-summaries",
            output_names=["matches"],
            operations=[
                {
                    "operationType": "android.element.getAll",
                    "parameters": {
                        "xpath": xpath,
                        "variableName": "matches",
                    }
                }
            ]
        )
        outputs = self._get_outputs(result)
        raw_matches = outputs.get("matches")
        if not isinstance(raw_matches, str) or not raw_matches.strip():
            return []

        pattern = re.compile(
            r"AndroidElement\{id='[^']*', text='(.*?)', className='(.*?)', stale=(?:true|false)\}",
            re.DOTALL,
        )
        summaries: List[Dict[str, str]] = []
        for match in pattern.finditer(raw_matches):
            summaries.append(
                {
                    "text": match.group(1),
                    "className": match.group(2),
                }
            )
        return summaries

    def _describe_unique_xpath_match(self, xpath: str) -> Dict[str, Any]:
        """When an XPath is unique, read a few key attributes from the first match."""
        result = self._execute_template(
            template_id="xpath-describe-unique",
            output_names=["textValue", "contentDescriptionValue", "classNameValue", "boundsValue"],
            operations=[
                {
                    "operationType": "android.element.getAttribute",
                    "parameters": {
                        "xpath": xpath,
                        "attribute": "text",
                        "targetVariable": "textValue",
                        "optional": True,
                    }
                },
                {
                    "operationType": "android.element.getAttribute",
                    "parameters": {
                        "xpath": xpath,
                        "attribute": "content-desc",
                        "targetVariable": "contentDescriptionValue",
                        "optional": True,
                    }
                },
                {
                    "operationType": "android.element.getAttribute",
                    "parameters": {
                        "xpath": xpath,
                        "attribute": "className",
                        "targetVariable": "classNameValue",
                        "optional": True,
                    }
                },
                {
                    "operationType": "android.element.getAttribute",
                    "parameters": {
                        "xpath": xpath,
                        "attribute": "bounds",
                        "targetVariable": "boundsValue",
                        "optional": True,
                    }
                }
            ]
        )
        outputs = self._get_outputs(result)
        return {
            "text": outputs.get("textValue"),
            "contentDescription": outputs.get("contentDescriptionValue"),
            "className": outputs.get("classNameValue"),
            "bounds": outputs.get("boundsValue"),
        }

    def _describe_unique_xpath_match_runtime(self, xpath: str) -> Dict[str, Any]:
        detail = self._describe_unique_xpath_match(xpath)
        bounds = detail.get("bounds")
        parsed = self._parse_bounds_string(bounds) if isinstance(bounds, str) else None
        x = y = None
        if parsed:
            x1, y1, x2, y2 = parsed
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2

        class_name = detail.get("className")
        return {
            "index": 0,
            "count": 1,
            "refId": None,
            "text": detail.get("text"),
            "contentDescription": detail.get("contentDescription"),
            "className": class_name,
            "bounds": bounds,
            "x": x,
            "y": y,
            "resourceId": None,
            "isInput": class_name in {"EditText", "AutoCompleteTextView", "TextInputEditText"},
        }

    def validate_xpath_runtime(self, xpath: str) -> Optional[Dict[str, Any]]:
        """Validate an XPath in the Android runtime and return a summary for unique matches."""
        count = self._get_xpath_match_count(xpath)
        if count is None:
            return None

        info: Dict[str, Any] = {
            "xpath": xpath,
            "count": count,
        }
        if count == 1:
            info.update(self._describe_unique_xpath_match(xpath))
        return info

    def describe_xpath_match(self, xpath: str, index: int = 0) -> Optional[Dict[str, Any]]:
        """Describe one XPath match from the current UI tree."""
        if index < 0:
            return None
        runtime_count = self._get_xpath_match_count(xpath)
        if runtime_count == 1 and index == 0:
            return self._describe_unique_xpath_match_runtime(xpath)
        tree = self.get_ui_elements(force_refresh=True)
        if not tree:
            return None
        matches = self.find_by_xpath_all(tree, xpath)
        if index >= len(matches):
            return None
        return self._describe_tree_match(matches[index], index, len(matches))

    def _resolve_xpath_input_target(
        self, xpath: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[str]]:
        """Resolve one XPath input target without guessing nearby editable fields."""
        tree = self.get_ui_elements(force_refresh=True)
        if not tree:
            return None, None, "tree_unavailable"

        matches = self.find_by_xpath_all(tree, xpath)
        if not matches:
            return None, None, "not_found"
        if len(matches) != 1:
            return None, None, "multiple_matches"

        target = matches[0]
        detail = self._describe_tree_match(target, 0, 1)
        if not self._is_input_element(target):
            return target, detail, "not_input"
        return target, detail, None

    def get_ui_tree_xml(self, force_refresh: bool = False, visible_only: bool = True) -> Optional[str]:
        """Return the accessibility UI tree XML."""
        if (
            not force_refresh
            and self._ui_tree_xml_cache is not None
            and self._ui_tree_xml_cache_visible_only == visible_only
        ):
            return self._ui_tree_xml_cache

        result = self._execute_template(
            template_id="ui-tree-dump-inline",
            output_names=["uiTreeContent"],
            operations=[
                {
                    "operationType": "android.ui.dumpTree",
                    "parameters": {
                        "filePath": "/storage/emulated/0/Android/data/aivane.apprepl/files/ui_tree_dump.xml",
                        "format": "xml",
                        "visibleOnly": visible_only,
                        "variableName": "uiTreeContent",
                    },
                }
            ],
        )
        outputs = self._get_outputs(result)
        xml_text = outputs.get("uiTreeContent")
        if isinstance(xml_text, str) and xml_text.strip():
            self._ui_tree_xml_cache = xml_text
            self._ui_tree_xml_cache_visible_only = visible_only
            return xml_text
        return None

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def get_ui_elements(self, wait: int = 0, force_refresh: bool = False, visible_only: bool = True
                        ) -> Optional[List[Dict]]:
        """
        Fetch the current UI element list.

        Results are cached within this client instance unless
        `force_refresh=True`.
        """
        if wait > 0:
            time.sleep(wait)

        if (
            not force_refresh
            and self._local_tree is not None
            and self._local_tree_visible_only == visible_only
        ):
            return self._local_tree

        elements = self._fetch_ui_elements_impl(visible_only=visible_only)
        if elements is not None:
            self._local_tree = elements
            self._local_tree_visible_only = visible_only
            package_name = self.get_current_package_name()
            try:
                save_snapshot(self.base_url, package_name, elements)
                self._snapshot = {
                    "baseUrl": self.base_url,
                    "packageName": package_name,
                    "elements": elements,
                }
            except OSError:
                pass
        return elements

    def _fetch_ui_elements_impl(self, visible_only: bool = True) -> Optional[List[Dict]]:
        """Fetch the UI element list from the API."""
        json_str = (
            '{"templateId":"ui-elements-get","templateName":"UI Elements Query",'
            '"parameters":[{"name":"uiElements","type":"STRING","direction":"OUTPUT"}],'
            '"operations":['
            '{"operationType":"android.ui.getAriaTree","parameters":{"variableName":"tree","visibleOnly":%s}},'
            '{"operationType":"variable.assign","parameters":{"variableName":"uiElements","value":"\\u0024{tree}"}}'
            ']}'
        ) % ("true" if visible_only else "false")
        result = self._api_call(json.loads(json_str))
        if not result:
            return None

        if not result.get('success'):
            print(f"Error: {result.get('errorMessage', 'Unknown error')}", file=sys.stderr)
            return None

        outputs = result.get('data', {}).get('outputs', {})
        if isinstance(outputs, dict):
            ui_elements_json = outputs.get('uiElements', '[]')
        else:
            ui_elements_json = '[]'

        try:
            elements = json.loads(ui_elements_json)
            return elements
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            return None

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def wait_for_element(self, text: str = None, refId: int = None,
                         timeout: int = 30, interval: float = 1.0
                         ) -> Optional[Dict]:
        """
        Poll the UI tree until the target element is found or the timeout expires.

        Returns the matching element dict, or `None` if nothing is found.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            elements = self.get_ui_elements(force_refresh=True)
            if elements:
                if refId is not None:
                    for e in elements:
                        if e.get('refId') == refId:
                            print(f"[wait-for] Found refId={refId} after {timeout - int(deadline - time.time())}s")
                            return e
                elif text is not None:
                    for e in elements:
                        t = e.get('text', '') or ''
                        d = e.get('contentDesc', '') or ''
                        if text.lower() in t.lower() or text.lower() in d.lower():
                            print(f"[wait-for] Found text='{e.get('text', '')}' (refId={e.get('refId')}) after {timeout - int(deadline - time.time())}s")
                            return e
            remaining = int(deadline - time.time())
            if remaining > 0:
                time.sleep(min(interval, remaining))
        print(f"[wait-for] Timeout after {timeout}s (text='{text}', refId={refId})", file=sys.stderr)
        return None

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def tap_element(self, refId: int) -> bool:
        """Tap the element for the given refId using the cached tree when available."""
        target = self._resolve_action_target(refId)
        if not target:
            return False

        coords = self._get_coordinates(target, f"Element refId={refId}")
        if not coords:
            return False
        x, y = coords

        return self._run_single_operation(
            template_id=f"tap-refId-{refId}",
            operation_type="android.touch.tap",
            parameters={"mode": "coordinate", "x": x, "y": y},
            success_message=f"Tapped refId={refId} at ({x}, {y})",
            failure_prefix="Tap failed"
        )

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def input_to_element(self, refId: int, text: str, clearFirst: bool = True) -> bool:
        """Input text into the given refId using the cached tree when available."""
        target = self._resolve_action_target(refId)
        if not target:
            return False
        if not self._is_input_element(target):
            cls = target.get("simpleClassName") or "unknown"
            print(
                f"Input failed: refId={refId} resolved to non-input element "
                f"class={cls}. Refusing to guess a nearby input field.",
                file=sys.stderr,
            )
            return False

        elem_desc = target.get('text') or target.get('contentDesc') or f"refId={refId}"
        coords = self._get_coordinates(target, f"Element refId={refId}")
        if not coords:
            return False
        x, y = coords

        action = "Clearing" if clearFirst and text == "" else "Inputting"
        print(f"{action} '{text}' to '{elem_desc}' (refId={refId}) at ({x}, {y})")

        return self._run_single_operation(
            template_id=f"input-refId-{refId}",
            operation_type="android.element.input",
            parameters={
                "x": x,
                "y": y,
                "value": text,
                "clearFirst": clearFirst
            },
            success_message=(
                f"SUCCESS: Cleared element refId={refId}"
                if clearFirst and text == ""
                else f"SUCCESS: Input '{text}' to element refId={refId}"
            ),
            failure_prefix="FAILED"
        )

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def swipe(self, direction: str = "down", duration: int = 300,
              distance: float = 0.5) -> bool:
        """
        Execute a swipe gesture.

        direction: up / down / left / right
        duration: swipe duration in milliseconds
        distance: swipe distance as a screen ratio (0.0-1.0)
        """
        d = direction.lower()
        if d not in ('up', 'down', 'left', 'right'):
            print(f"Invalid direction: {direction}, use: up/down/left/right")
            return False

        return self._run_single_operation(
            template_id=f"swipe-{d}",
            operation_type="android.touch.swipe",
            parameters={
                "type": "direction",
                "direction": d,
                "duration": duration,
                "distance": distance
            },
            success_message=f"Swiped {d} (duration={duration}ms, distance={distance})",
            failure_prefix="Swipe failed"
        )

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def screenshot(self, output_path: str = None,
                   quality: int = 80) -> Optional[str]:
        """
        Capture a screenshot and download it locally.

        Returns the saved local file path, or `None` on failure.
        """
        print(f"Capturing screenshot (quality={quality})...", file=sys.stderr)
        data = self._get_raw("/screenshot", {"quality": str(quality)})

        if not data:
            print("Screenshot: fallback to template-based capture", file=sys.stderr)
            return self._screenshot_via_template(output_path, quality)

        if not data.get('success'):
            print(f"Screenshot failed: {data.get('errorMessage', 'Unknown error')}", file=sys.stderr)
            return None

        base64_data = data.get('base64', '')
        if not base64_data:
            print("Screenshot: no base64 data in response", file=sys.stderr)
            return None

        image_bytes = base64.b64decode(base64_data)
        size_kb = len(image_bytes) // 1024

        if not output_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"screenshot_{timestamp}.jpg"

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_path, 'wb') as f:
            f.write(image_bytes)

        print(f"Screenshot saved: {output_path} ({size_kb}KB)", file=sys.stderr)
        return output_path

    def _screenshot_via_template(self, output_path: str = None, quality: int = 80) -> Optional[str]:
        """Fallback path: capture a screenshot through the template API and then download it."""
        if not output_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"screenshot_{timestamp}.png"

        package = self._get_package_name()
        save_path = f"/data/data/{package}/files/aria_screenshot.png" if package else "/sdcard/aria_screenshot.png"
        fmt = "jpeg" if quality < 100 else "png"

        template = {
            "templateId": "screenshot-capture",
            "operations": [
                {"operationType": "android.screenshot.capture", "parameters": {
                    "savePath": save_path,
                    "format": fmt,
                    "quality": quality
                }}
            ]
        }
        result = self._api_call(template)
        if not result or not result.get('success'):
            msg = result.get('errorMessage', 'Unknown') if result else 'no response'
            print(f"Screenshot failed: {msg}", file=sys.stderr)
            return None

        file_data = self._download_binary("/download", {"path": save_path})
        if not file_data:
            print(f"Screenshot: file download failed (but API succeeded)", file=sys.stderr)
            return None

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_path, 'wb') as f:
            f.write(file_data)
        print(f"Screenshot saved: {output_path} ({len(file_data)//1024}KB)", file=sys.stderr)
        return output_path

    def _get_package_name(self) -> Optional[str]:
        """Return the current foreground app package name."""
        template = {
            "templateId": "current-app",
            "operations": [
                {"operationType": "android.app.current", "parameters": {}}
            ]
        }
        result = self._api_call(template)
        if result and result.get('success'):
            data = result.get('data', {})
            return data.get('packageName')
        return None

    def _get_package_name_from_dump_tree(self) -> Optional[str]:
        """Read the current foreground package name from the dumpTree(json) root node."""
        result = self._execute_template(
            template_id="ui-tree-package-probe",
            output_names=["uiTreeJson"],
            operations=[
                {
                    "operationType": "android.ui.dumpTree",
                    "parameters": {
                        "filePath": "/storage/emulated/0/Android/data/aivane.apprepl/files/ui_tree_dump.json",
                        "format": "json",
                        "variableName": "uiTreeJson",
                    },
                }
            ],
        )
        outputs = self._get_outputs(result)
        ui_tree_json = outputs.get("uiTreeJson")
        if not isinstance(ui_tree_json, str) or not ui_tree_json.strip():
            return None
        try:
            data = json.loads(ui_tree_json)
        except json.JSONDecodeError:
            return None
        package_name = data.get("packageName")
        return package_name if isinstance(package_name, str) and package_name.strip() else None

    def get_current_package_name(self) -> Optional[str]:
        """Public helper for querying the current foreground package name for listing and diagnostics."""
        package_name = self._get_package_name()
        if not package_name:
            package_name = self._get_package_name_from_dump_tree()
        if package_name:
            self._package_name_cache = package_name
            return package_name
        return self._package_name_cache

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def press_key(self, key: str) -> bool:
        """
        Press a supported system key.

        key: back / home / recents
        """
        key_map = {
            "back": "android.press.back",
            "home": "android.press.home",
            "recents": "android.press.recents",
        }
        op_type = key_map.get(key.lower())
        if not op_type:
            print(f"Unknown key: {key}. Available: {', '.join(key_map.keys())}", file=sys.stderr)
            return False

        template = {
            "templateId": f"press-{key.lower()}",
            "operations": [{"operationType": op_type, "parameters": {}}],
        }

        result = self._api_call(template)
        if result and result.get('success'):
            print(f"Pressed: {key}")
            self._local_tree = None
            self._local_tree_visible_only = True
            self._ui_tree_xml_cache = None
            self._ui_tree_xml_cache_visible_only = True
            return True

        msg = result.get('errorMessage', 'Unknown') if result else 'no response'
        print(f"Press key failed: {msg}")
        return False

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def get_attribute(self, refId: int, attribute: str) -> Optional[str]:
        """
        Return the requested attribute for the element identified by refId.

        attribute: text / content-desc / className / resourceId / bounds / ...
        """
        target = self._find_element_by_refId(refId)
        if not target:
            print(f"Element refId={refId} not found")
            return None

        attr_map = {
            "text": "text",
            "content-desc": "contentDesc",
            "contentdesc": "contentDesc",
            "desc": "contentDesc",
            "classname": "simpleClassName",
            "class": "simpleClassName",
            "classname": "simpleClassName",
            "resourceid": "resourceId",
            "id": "resourceId",
            "bounds": "bounds",
            "x": "x",
            "y": "y",
            "refid": "refId",
            "xpath": "xpath",
            "selector": "selector",
            "clickable": "clickable",
            "enabled": "enabled",
            "focusable": "focusable",
            "visible": "visible",
        }
        key = attr_map.get(attribute.lower())
        if not key:
            print(f"Unknown attribute: {attribute}")
            return None

        value = target.get(key, 'N/A')
        print(f"refId={refId} {attribute} = {value}")
        return str(value) if value is not None else None

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def launch_app(self, package: str) -> bool:
        return self._run_single_operation(
            template_id=f"launch-{package}",
            operation_type="android.app.launch",
            parameters={"packageName": package},
            success_message=f"Launched: {package}",
            failure_prefix="Launch failed"
        )

    def press_back(self) -> bool:
        return self._run_single_operation(
            template_id="back",
            operation_type="android.press.back",
            parameters={},
            success_message="Pressed back",
            failure_prefix="Back failed"
        )

    # ---------------------------------------------------------------------------
    # ---------------------------------------------------------------------------

    def _find_element_by_refId(self, refId: int,
                                force_refresh: bool = False) -> Optional[Dict]:
        """Find an element from the cached tree and only refetch when needed."""
        tree = self.get_ui_elements(force_refresh=force_refresh)
        if not tree:
            return None
        for elem in tree:
            if elem.get('refId') == refId:
                return elem
        print(f"Element with refId={refId} not found in tree ({len(tree)} elements)")
        return None

    def find_by_refId(self, elements: List[Dict], refId: int) -> Optional[Dict]:
        for elem in elements:
            if elem.get('refId') == refId:
                return elem
        return None

    def find_by_resourceId(self, elements: List[Dict], resourceId: str) -> List[Dict]:
        return [e for e in elements if e.get('resourceId') == resourceId]

    def find_by_text(self, elements: List[Dict], text: str) -> List[Dict]:
        needle = text.lower()
        matches: List[Dict] = []
        for elem in elements:
            haystacks = [
                elem.get("text", ""),
                elem.get("contentDesc", ""),
                elem.get("contentDescription", ""),
            ]
            if any(needle in (value or "").lower() for value in haystacks):
                matches.append(elem)
        return matches

    def find_input_elements(self, elements: List[Dict]) -> List[Dict]:
        return [e for e in elements if self._is_input_element(e)]

    def find_by_xpath(self, elements: List[Dict], xpath: str) -> Optional[Dict]:
        """
        Find the first element that matches the given XPath-like filter.

        Supported formats:
              //ClassName[@attr='value'][@attr2='value2']
              //ClassName[@following-sibling::OtherClass]
              //ClassName[@preceding-sibling::OtherClass]
        Examples:
              //EditText[@text='Search']
              //Button[@text='Search'][following-sibling::Button]
              //TextView[@contentDesc='Search'][clickable]
        Returns the first matching element, or `None`.
        """
        import re
        attrs = {}

        attrs = {}
        i = 0
        while i < len(xpath):
            if xpath[i] == '[':
                j = i + 1
                depth = 1
                in_quote = None  # Tracks whether we are inside a quoted string and which quote opened it
                while j < len(xpath) and depth > 0:
                    ch = xpath[j]
                    if in_quote is not None:
                        if ch == in_quote:
                            in_quote = None
                    else:
                        if ch == '[':
                            depth += 1
                        elif ch == ']':
                            depth -= 1
                        elif ch in ("'", '"'):
                            in_quote = ch
                    j += 1
                cond = xpath[i+1:j-1]
                if cond.startswith('@'):
                    eq_pos = cond.find('=')
                    if eq_pos > 0:
                        attr = cond[1:eq_pos].strip()
                        raw_value = cond[eq_pos+1:].strip()
                        if raw_value and raw_value[0] in ("'", '"'):
                            quote_char = raw_value[0]
                            end = 1
                            while end < len(raw_value):
                                if raw_value[end] == quote_char:
                                    num_backslash = 0
                                    j2 = end - 1
                                    while j2 >= 1 and raw_value[j2] == '\\':
                                        num_backslash += 1
                                        j2 -= 1
                                    if num_backslash % 2 == 0:  # Unescaped quote
                                        break
                                end += 1
                            value = raw_value[1:end]  # Strip the surrounding quotes
                        else:
                            bracket_pos = raw_value.find(']')
                            value = raw_value[:bracket_pos].strip() if bracket_pos >= 0 else raw_value.strip()
                        if value:
                            attrs[attr] = value
                else:
                    # following-sibling::ClassName / preceding-sibling::ClassName
                    cond_stripped = cond.strip()
                    for axis in ('following-sibling::', 'preceding-sibling::'):
                        if cond_stripped.startswith(axis):
                            tag = cond_stripped[len(axis):].strip()
                            if tag:
                                attrs[f'_{axis.rstrip(":")}'] = tag
                            break
                    else:
                        cond = cond.strip()
                        if cond in ('clickable', 'focusable', 'long-clickable', 'scrollable'):
                            attrs[cond] = True
                        elif cond.isdigit():
                            attrs['_position'] = int(cond)
                i = j
            else:
                i += 1

        elem_refId: Dict[int, Dict] = {e.get('refId'): e for e in elements if e.get('refId') is not None}
        # seg_to_elem[(depth, seg)] = elem
        seg_to_elem: Dict[tuple, Dict] = {}
        for e in elements:
            rid = e.get('refId')
            if rid is None:
                continue
            xp = e.get('xpath', '')
            segs = [s for s in xp.split('/') if s and s != 'WindowRoot']
            for di, seg in enumerate(segs):
                depth = di + 1
                key = (depth, seg)
                if key not in seg_to_elem:
                    seg_to_elem[key] = []
                seg_to_elem[key].append(e)

        def _get_prefix_seg(xp: str, up_to_depth: int) -> str:
            """Return the minimal common form of the first N xpath segments without indices such as [2]."""
            segs = [s for s in xp.split('/') if s and s != 'WindowRoot']
            parts = []
            for di in range(min(up_to_depth, len(segs))):
                seg = segs[di]
                idx = seg.find('[')
                cls = seg[:idx] if idx >= 0 else seg
                parts.append(cls)
            return '/'.join(parts)

        parent_of: Dict[int, int] = {}
        for e in elements:
            rid = e.get('refId')
            if rid is None:
                continue
            xp = e.get('xpath', '')
            segs = [s for s in xp.split('/') if s and s != 'WindowRoot']
            depth = len(segs)
            if depth < 2:
                parent_of[rid] = None
                continue
            parent_seg = segs[-2]  # The second-to-last segment is the parent node
            candidates = seg_to_elem.get((depth - 1, parent_seg), [])
            if len(candidates) == 1:
                parent_of[rid] = candidates[0].get('refId')
            elif len(candidates) > 1:
                best = None
                best_len = 0
                xp_prefix = '/'.join(segs[:-1])
                for c in candidates:
                    c_xp = c.get('xpath', '')
                    c_prefix = '/'.join(
                        s for s in c_xp.split('/')
                        if s and s != 'WindowRoot'
                    )
                    if c_prefix and xp_prefix.startswith(c_prefix) and len(c_prefix) > best_len:
                        best = c.get('refId')
                        best_len = len(c_prefix)
                parent_of[rid] = best
            else:
                parent_of[rid] = None

        parent_children2: Dict[int, List[int]] = {}
        for rid, pid in parent_of.items():
            if pid is not None:
                parent_children2.setdefault(pid, []).append(rid)

        elem_refId2: Dict[int, Dict] = {e.get('refId'): e for e in elements if e.get('refId') is not None}

        def matches(elem: Dict) -> bool:
            for k, v in attrs.items():
                if k == 'refId':
                    if str(elem.get('refId', '')) != v:
                        return False
                elif k == 'text':
                    if (elem.get('text', '') or '') != v:
                        return False
                elif k in ('contentDesc', 'contentDescription', 'content-desc', 'contentdesc'):
                    if v.lower() not in (elem.get('contentDesc', '') or '').lower():
                        return False
                elif k == 'resourceId':
                    if elem.get('resourceId', '') != v:
                        return False
                elif k == 'className' or k == 'class':
                    if v.lower() not in (elem.get('simpleClassName', '') or '').lower():
                        return False
                elif k == 'clickable':
                    if not elem.get('clickable'):
                        return False
                elif k == 'focusable':
                    if not elem.get('focusable'):
                        return False
                elif k in ('x', 'y'):
                    elem_coord = elem.get(k)
                    try:
                        target = int(v)
                    except (ValueError, TypeError):
                        target = v
                    if elem_coord != target:
                        return False
                elif k == '_position':
                    target_idx = v
                    cls = elem.get('simpleClassName', '')
                    if not cls:
                        return False
                    same_cls_all = [e for e in elements if e.get('simpleClassName') == cls]
                    try:
                        actual_idx = same_cls_all.index(elem) + 1
                        if actual_idx != target_idx:
                            return False
                    except ValueError:
                        return False
                elif k == '_following-sibling':
                    rid = elem.get('refId')
                    pid = parent_of.get(rid)
                    siblings = parent_children2.get(pid, []) if pid else []
                    try:
                        idx = siblings.index(rid)
                        siblings_after = siblings[idx + 1:]
                    except ValueError:
                        siblings_after = []
                    for sib_rid in siblings_after:
                        sib = elem_refId2.get(sib_rid)
                        if sib and sib.get('simpleClassName', '') == v:
                            return True
                    return False
                elif k == '_preceding-sibling':
                    rid = elem.get('refId')
                    pid = parent_of.get(rid)
                    siblings = parent_children2.get(pid, []) if pid else []
                    try:
                        idx = siblings.index(rid)
                        siblings_before = siblings[:idx]
                    except ValueError:
                        siblings_before = []
                    for sib_rid in reversed(siblings_before):
                        sib = elem_refId2.get(sib_rid)
                        if sib and sib.get('simpleClassName', '') == v:
                            return True
                    return False
            return True

        for elem in elements:
            if matches(elem):
                return elem
        return None

    def find_by_xpath_all(self, elements: List[Dict], xpath: str) -> List[Dict]:
        """
        Find all elements that match the given XPath-like filter.

        This uses the same logic as `find_by_xpath`, but returns every match
        instead of only the first one.
        """
        import re
        attrs = {}

        i = 0
        while i < len(xpath):
            if xpath[i] == '[':
                j = i + 1
                depth = 1
                in_quote = None
                while j < len(xpath) and depth > 0:
                    ch = xpath[j]
                    if in_quote is not None:
                        if ch == in_quote:
                            in_quote = None
                    else:
                        if ch == '[':
                            depth += 1
                        elif ch == ']':
                            depth -= 1
                        elif ch in ("'", '"'):
                            in_quote = ch
                    j += 1
                cond = xpath[i+1:j-1]
                if cond.startswith('@'):
                    eq_pos = cond.find('=')
                    if eq_pos > 0:
                        attr = cond[1:eq_pos].strip()
                        raw_value = cond[eq_pos+1:].strip()
                        if raw_value and raw_value[0] in ("'", '"'):
                            quote_char = raw_value[0]
                            end = 1
                            while end < len(raw_value):
                                if raw_value[end] == quote_char:
                                    num_backslash = 0
                                    j2 = end - 1
                                    while j2 >= 1 and raw_value[j2] == '\\':
                                        num_backslash += 1
                                        j2 -= 1
                                    if num_backslash % 2 == 0:
                                        break
                                end += 1
                            value = raw_value[1:end]
                        else:
                            bracket_pos = raw_value.find(']')
                            value = raw_value[:bracket_pos].strip() if bracket_pos >= 0 else raw_value.strip()
                        if value:
                            attrs[attr] = value
                else:
                    cond_stripped = cond.strip()
                    for axis in ('following-sibling::', 'preceding-sibling::'):
                        if cond_stripped.startswith(axis):
                            tag = cond_stripped[len(axis):].strip()
                            if tag:
                                attrs[f'_{axis.rstrip(":")}'] = tag
                            break
                    else:
                        cond = cond.strip()
                        if cond in ('clickable', 'focusable', 'long-clickable', 'scrollable'):
                            attrs[cond] = True
                i = j
            else:
                i += 1

        elem_refId: Dict[int, Dict] = {e.get('refId'): e for e in elements if e.get('refId') is not None}
        nodes = self._build_tree_structure(elements)
        parent_children: Dict[int, List[int]] = {}
        for ref_id, node in nodes.items():
            pid = node.get('parent_ref_id')
            if pid is not None:
                parent_children.setdefault(pid, []).append(ref_id)

        def matches(elem: Dict) -> bool:
            for k, v in attrs.items():
                if k == 'refId':
                    if str(elem.get('refId', '')) != v:
                        return False
                elif k == 'text':
                    if (elem.get('text', '') or '') != v:
                        return False
                elif k in ('contentDesc', 'contentDescription', 'content-desc', 'contentdesc'):
                    if v.lower() not in (elem.get('contentDesc', '') or '').lower():
                        return False
                elif k == 'resourceId':
                    if elem.get('resourceId', '') != v:
                        return False
                elif k == 'className' or k == 'class':
                    if v.lower() not in (elem.get('simpleClassName', '') or '').lower():
                        return False
                elif k == 'clickable':
                    if not elem.get('clickable'):
                        return False
                elif k == 'focusable':
                    if not elem.get('focusable'):
                        return False
                elif k in ('x', 'y'):
                    elem_coord = elem.get(k)
                    try:
                        target = int(v)
                    except (ValueError, TypeError):
                        target = v
                    if elem_coord != target:
                        return False
                elif k == '_position':
                    target_idx = v
                    cls = elem.get('simpleClassName', '')
                    if not cls:
                        return False
                    same_cls_all = [e for e in elements if e.get('simpleClassName') == cls]
                    try:
                        actual_idx = same_cls_all.index(elem) + 1
                        if actual_idx != target_idx:
                            return False
                    except ValueError:
                        return False
                elif k == '_following-sibling':
                    rid = elem.get('refId')
                    pid = None
                    siblings_after = []
                    for p, kids in parent_children.items():
                        try:
                            idx = kids.index(rid)
                            pid = p
                            siblings_after = kids[idx + 1:]
                            break
                        except ValueError:
                            continue
                    if pid is None:
                        return False
                    for sib_rid in siblings_after:
                        sib = elem_refId.get(sib_rid)
                        if sib and sib.get('simpleClassName', '') == v:
                            return True
                    return False
                elif k == '_preceding-sibling':
                    rid = elem.get('refId')
                    pid = None
                    siblings_before = []
                    for p, kids in parent_children.items():
                        try:
                            idx = kids.index(rid)
                            pid = p
                            siblings_before = kids[:idx]
                            break
                        except ValueError:
                            continue
                    if pid is None:
                        return False
                    for sib_rid in reversed(siblings_before):
                        sib = elem_refId.get(sib_rid)
                        if sib and sib.get('simpleClassName', '') == v:
                            return True
                    return False
            return True

        return [elem for elem in elements if matches(elem)]

    def _escape_xpath_value(self, value: str) -> str:
        """Choose the best quotes for an XPath attribute value and escape the content."""
        if "'" in value and '"' not in value:
            return f'"{value}"'
        return f"'{value}'"

    def _make_xpath(self, cls: str, **conditions: Any) -> str:
        """
        Build an XPath string.

        cls: class name such as 'Button' or 'EditText'
        **conditions: attribute conditions such as text='Search', refId=5,
                      clickable=True, resourceId='...'
        """
        parts = [f'//{cls}']
        for k, v in conditions.items():
            if v is True:
                parts.append(f'[{k}]')
            elif v is not None and v is not False:
                parts.append(f'[@{k}={self._escape_xpath_value(str(v))}]')
        return ''.join(parts)

    def _parse_refid_from_xpath_segment(self, segment: str) -> Optional[int]:
        """Extract a refId from an xpath segment such as 'LinearLayout[1][@refId=5]'."""
        i = 0
        while i < len(segment):
            if segment[i] == '[':
                j = i + 1
                depth = 1
                in_quote = None
                while j < len(segment) and depth > 0:
                    ch = segment[j]
                    if in_quote is not None:
                        if ch == in_quote:
                            in_quote = None
                    else:
                        if ch == '[':
                            depth += 1
                        elif ch == ']':
                            depth -= 1
                        elif ch in ("'", '"'):
                            in_quote = ch
                    j += 1
                inner = segment[i+1:j-1]
                if inner.startswith('@refId='):
                    try:
                        return int(inner[8:].strip("'\""))
                    except ValueError:
                        pass
                i = j
            else:
                i += 1
        return None

    def _build_tree_structure(
        self, tree: List[Dict]
    ) -> Dict[int, Dict]:
        """
        Build a tree structure from a flat element list (parent -> children mapping).

        Strategy:
        Some intermediate nodes in accessibility xpaths may not expose @refId,
        so we cannot always derive the parent from the parent segment's @refId.
        Instead we walk the flat list in its original UI order and keep a stack
        of the currently open refIds by depth. This preserves sibling and
        ancestor relationships from the source traversal order; sorting by depth
        can incorrectly attach later shallow nodes as parents of unrelated deep
        descendants.

        Each node contains:
        {elem, parent_ref_id, depth, xpath_prefix, children_ref_ids}
        """
        elem_xpath: Dict[int, str] = {}  # refId -> xpath prefix (without the current segment)
        elem_depth: Dict[int, int] = {}

        for elem in tree:
            ref_id = elem.get('refId')
            if ref_id is None:
                continue
            xpath = elem.get('xpath', '')
            segments = [s for s in xpath.split('/') if s and s != 'WindowRoot']
            depth = len(segments)
            elem_depth[ref_id] = depth
            if len(segments) >= 1:
                prefix = '/' + '/'.join(segments[:-1])
            else:
                prefix = '/WindowRoot'
            elem_xpath[ref_id] = prefix

        stack: List[int] = []
        elem_parent: Dict[int, Optional[int]] = {}

        for elem in tree:
            ref_id = elem.get('refId')
            if ref_id is None:
                continue
            depth = elem_depth.get(ref_id, 0)
            elem_parent[ref_id] = None
            while len(stack) >= depth and stack:
                stack.pop()
            if stack:
                elem_parent[ref_id] = stack[-1]
            stack.append(ref_id)

        nodes: Dict[int, Dict] = {}
        for elem in tree:
            ref_id = elem.get('refId')
            if ref_id is None:
                continue
            nodes[ref_id] = {
                'elem': elem,
                'parent_ref_id': elem_parent.get(ref_id),
                'depth': elem_depth.get(ref_id, 0),
                'xpath_prefix': elem_xpath.get(ref_id, ''),
                'children_ref_ids': [],
            }

        for ref_id, parent_ref_id in elem_parent.items():
            if parent_ref_id is not None and parent_ref_id in nodes:
                nodes[parent_ref_id]['children_ref_ids'].append(ref_id)

        return nodes

    def _depth_from_xpath(self, xpath: str) -> int:
        """Count the depth of an accessibility xpath, excluding WindowRoot."""
        if not xpath:
            return -1
        segments = [s for s in xpath.split('/') if s and s != 'WindowRoot']
        return len(segments)

    def _make_absolute_xpath(self, tree: List[Dict], target_ref_id: int) -> Optional[str]:
        """
        Build an absolute XPath such as ClassName[1]/ClassName[3]/TargetClassName[N].

        The path is traced from the root to the target, numbering each step by
        the position among siblings of the same class.
        """
        nodes = self._build_tree_structure(tree)
        if target_ref_id not in nodes:
            return None

        path_ref_ids: List[int] = []
        cur = target_ref_id
        while cur is not None:
            path_ref_ids.append(cur)
            cur = nodes[cur]['parent_ref_id']
        path_ref_ids.reverse()  # Order from root to target

        segments: List[str] = []
        for ref_id in path_ref_ids:
            node = nodes[ref_id]
            elem = node['elem']
            cls = elem.get('simpleClassName', '')
            if not cls:
                continue

            parent_ref_id = node['parent_ref_id']
            if parent_ref_id is None:
                idx = 1
            else:
                parent_node = nodes.get(parent_ref_id)
                if not parent_node:
                    idx = 1
                else:
                    siblings = parent_node['children_ref_ids']
                    same_class_siblings = [
                        sid for sid in siblings
                        if sid in nodes and
                        nodes[sid]['elem'].get('simpleClassName') == cls
                    ]
                    try:
                        idx = same_class_siblings.index(ref_id) + 1
                    except ValueError:
                        idx = 1

            segments.append(f'{cls}[{idx}]')

        return '//' + '/'.join(segments)

    def _strip_refid_annotation(self, segment: str) -> str:
        return re.sub(r'\[@refId=\d+\]', '', segment)

    def _split_debug_xpath(self, xpath: str) -> List[str]:
        return [self._strip_refid_annotation(s) for s in xpath.split('/') if s and s != 'WindowRoot']

    def _extract_path_index(self, segment: str) -> Optional[int]:
        match = re.search(r'\[(\d+)\](?!.*\[\d+\])', segment)
        if not match:
            return None
        try:
            return int(match.group(1))
        except ValueError:
            return None

    def _extract_segment_class(self, segment: str) -> str:
        stripped = segment.strip()
        if not stripped:
            return ''
        return re.sub(r'\[.*$', '', stripped)

    def _common_path_segments(self, paths: List[List[str]]) -> List[str]:
        if not paths:
            return []
        prefix = list(paths[0])
        for path in paths[1:]:
            limit = min(len(prefix), len(path))
            i = 0
            while i < limit and prefix[i] == path[i]:
                i += 1
            prefix = prefix[:i]
            if not prefix:
                break
        return prefix

    def _make_target_segment(
        self,
        elem: Dict,
        fallback_segment: str = '',
        index: Optional[int] = None,
    ) -> str:
        cls = elem.get('simpleClassName', '') or re.sub(r'\[.*$', '', fallback_segment) or 'node'
        text = (elem.get('text', '') or '').strip()
        desc = (elem.get('contentDesc', '') or '').strip()
        rid = (elem.get('resourceId', '') or '').strip()
        same_class_index = index if index and index > 0 else 1

        if desc:
            return f"{cls}[@content-desc={self._escape_xpath_value(desc)}]"
        if cls == 'EditText' and rid:
            return f"{cls}[@resourceId={self._escape_xpath_value(rid)}]"
        if text:
            return f"{cls}[@text={self._escape_xpath_value(text)}]"
        if rid:
            return f"{cls}[@resourceId={self._escape_xpath_value(rid)}]"
        return f"{cls}[{same_class_index}]"

    def _make_target_segment_from_xml(
        self,
        xml_node: ET.Element,
        index: int,
        parent: Optional[ET.Element],
    ) -> str:
        full_cls = xml_node.attrib.get('class', '') or 'node'
        cls = full_cls.split('.')[-1] if '.' in full_cls else full_cls
        text = (xml_node.attrib.get('text', '') or '').strip()
        desc = (xml_node.attrib.get('content-desc', '') or '').strip()
        rid = (xml_node.attrib.get('resource-id', '') or '').strip()

        def predicate_index(attr_name: str, attr_value: str) -> Optional[int]:
            if parent is None:
                return None
            siblings = []
            for child in list(parent):
                child_cls = child.attrib.get('class', '') or ''
                if child_cls != full_cls:
                    continue
                if (child.attrib.get(attr_name, '') or '').strip() != attr_value:
                    continue
                siblings.append(child)
            if len(siblings) <= 1:
                return None
            try:
                return siblings.index(xml_node) + 1
            except ValueError:
                return None

        if desc:
            same_attr_index = predicate_index('content-desc', desc)
            if same_attr_index and same_attr_index > 1:
                return f"{cls}[@content-desc={self._escape_xpath_value(desc)}][{same_attr_index}]"
            return f"{cls}[@content-desc={self._escape_xpath_value(desc)}]"
        if cls == 'EditText' and rid:
            same_attr_index = predicate_index('resource-id', rid)
            if same_attr_index and same_attr_index > 1:
                return f"{cls}[@resourceId={self._escape_xpath_value(rid)}][{same_attr_index}]"
            return f"{cls}[@resourceId={self._escape_xpath_value(rid)}]"
        if text:
            same_attr_index = predicate_index('text', text)
            if same_attr_index and same_attr_index > 1:
                return f"{cls}[@text={self._escape_xpath_value(text)}][{same_attr_index}]"
            return f"{cls}[@text={self._escape_xpath_value(text)}]"
        if rid:
            same_attr_index = predicate_index('resource-id', rid)
            if same_attr_index and same_attr_index > 1:
                return f"{cls}[@resourceId={self._escape_xpath_value(rid)}][{same_attr_index}]"
            return f"{cls}[@resourceId={self._escape_xpath_value(rid)}]"
        return f"{cls}[{index}]"

    def _parse_bounds_string(self, bounds: str) -> Optional[Tuple[int, int, int, int]]:
        match = re.match(r'^\[(\-?\d+),(\-?\d+)\]\[(\-?\d+),(\-?\d+)\]$', bounds.strip())
        if not match:
            return None
        return tuple(int(match.group(i)) for i in range(1, 5))

    def _score_xml_node_match(self, elem: Dict, xml_node: ET.Element) -> int:
        full_cls = xml_node.attrib.get('class', '') or ''
        simple_cls = full_cls.split('.')[-1] if '.' in full_cls else full_cls
        if simple_cls != (elem.get('simpleClassName') or ''):
            return -1

        score = 10
        elem_bounds = self._parse_bounds_string(elem.get('bounds', '') or '')
        xml_bounds = self._parse_bounds_string(xml_node.attrib.get('bounds', '') or '')
        if elem_bounds and xml_bounds:
            if elem_bounds == xml_bounds:
                score += 1000
            else:
                ex1, ey1, ex2, ey2 = elem_bounds
                xx1, xy1, xx2, xy2 = xml_bounds
                ex = (ex1 + ex2) // 2
                ey = (ey1 + ey2) // 2
                if xx1 <= ex <= xx2 and xy1 <= ey <= xy2:
                    score += 200

        elem_text = (elem.get('text', '') or '').strip()
        xml_text = (xml_node.attrib.get('text', '') or '').strip()
        if elem_text:
            if elem_text == xml_text:
                score += 120
            else:
                return -1

        elem_desc = (elem.get('contentDesc', '') or '').strip()
        xml_desc = (xml_node.attrib.get('content-desc', '') or '').strip()
        if elem_desc:
            if elem_desc == xml_desc:
                score += 120
            else:
                return -1

        elem_rid = (elem.get('resourceId', '') or '').strip()
        xml_rid = (xml_node.attrib.get('resource-id', '') or '').strip()
        if elem_rid:
            if elem_rid == xml_rid:
                score += 60
            else:
                return -1

        if elem.get('clickable') and xml_node.attrib.get('clickable') == 'true':
            score += 20
        if elem.get('focusable') and xml_node.attrib.get('focusable') == 'true':
            score += 10

        return score

    def _build_xml_parent_map(self, root: ET.Element) -> Dict[int, Optional[ET.Element]]:
        parent_map: Dict[int, Optional[ET.Element]] = {id(root): None}
        for parent in root.iter():
            for child in list(parent):
                parent_map[id(child)] = parent
        return parent_map

    def _get_ui_tree_root(self, force_refresh: bool = True, visible_only: bool = True) -> Optional[ET.Element]:
        xml_text = self.get_ui_tree_xml(force_refresh=force_refresh, visible_only=visible_only)
        if not xml_text:
            return None
        try:
            return ET.fromstring(xml_text)
        except ET.ParseError:
            return None

    def _format_xml_node_snippet(self, xml_node: ET.Element) -> str:
        snippet = ET.Element("node")
        for key, value in xml_node.attrib.items():
            snippet.set(key, value)
        return ET.tostring(snippet, encoding="unicode", short_empty_elements=True)

    def _split_xpath_segments_runtime(self, xpath: str) -> List[str]:
        text = xpath.strip()
        if text.startswith("/hierarchy/"):
            text = text[len("/hierarchy/"):]
        elif text.startswith("/hierarchy"):
            text = text[len("/hierarchy"):].lstrip("/")
        elif text.startswith("/"):
            text = text.lstrip("/")
        if not text:
            return []

        segments: List[str] = []
        current: List[str] = []
        depth = 0
        in_quote: Optional[str] = None
        for ch in text:
            if in_quote is not None:
                current.append(ch)
                if ch == in_quote:
                    in_quote = None
                continue
            if ch in ("'", '"'):
                in_quote = ch
                current.append(ch)
                continue
            if ch == "[":
                depth += 1
                current.append(ch)
                continue
            if ch == "]":
                depth = max(0, depth - 1)
                current.append(ch)
                continue
            if ch == "/" and depth == 0:
                segment = "".join(current).strip()
                if segment:
                    segments.append(segment)
                current = []
                continue
            current.append(ch)
        segment = "".join(current).strip()
        if segment:
            segments.append(segment)
        return segments

    def _xml_short_class(self, xml_node: ET.Element) -> str:
        full_cls = xml_node.attrib.get("class", "") or ""
        return full_cls.split(".")[-1] if "." in full_cls else full_cls

    def _parse_segment_predicates(self, segment: str) -> Tuple[str, List[str]]:
        cls = re.sub(r"\[.*$", "", segment).strip()
        predicates = re.findall(r"\[([^\]]+)\]", segment)
        return cls, predicates

    def _match_xml_predicate(
        self,
        xml_node: ET.Element,
        parent: ET.Element,
        predicate: str,
        class_name: str,
    ) -> bool:
        predicate = predicate.strip()
        if not predicate:
            return True

        if predicate.isdigit():
            same_class = [child for child in list(parent) if self._xml_short_class(child) == class_name]
            try:
                return same_class.index(xml_node) + 1 == int(predicate)
            except ValueError:
                return False

        position_equals = re.fullmatch(r"position\(\)\s*=\s*\d+(?:\s+or\s+position\(\)\s*=\s*\d+)*", predicate)
        if position_equals:
            indexes = [int(value) for value in re.findall(r"position\(\)\s*=\s*(\d+)", predicate)]
            same_class = [child for child in list(parent) if self._xml_short_class(child) == class_name]
            try:
                return (same_class.index(xml_node) + 1) in indexes
            except ValueError:
                return False

        position_range = re.fullmatch(r"position\(\)\s*>=\s*(\d+)\s+and\s+position\(\)\s*<=\s*(\d+)", predicate)
        if position_range:
            lower = int(position_range.group(1))
            upper = int(position_range.group(2))
            same_class = [child for child in list(parent) if self._xml_short_class(child) == class_name]
            try:
                index = same_class.index(xml_node) + 1
            except ValueError:
                return False
            return lower <= index <= upper

        attr_equals = re.fullmatch(r"@([A-Za-z0-9:_-]+)\s*=\s*(['\"])(.*)\2", predicate)
        if attr_equals:
            attr_name = attr_equals.group(1)
            attr_value = attr_equals.group(3)
            attr_aliases = {
                "contentDescription": "content-desc",
                "resourceId": "resource-id",
            }
            normalized = attr_aliases.get(attr_name, attr_name)
            return (xml_node.attrib.get(normalized, "") or "") == attr_value

        attr_or_equals = re.fullmatch(
            r"@([A-Za-z0-9:_-]+)\s*=\s*(['\"])(.*)\2\s+or\s+@([A-Za-z0-9:_-]+)\s*=\s*(['\"])(.*)\5",
            predicate,
        )
        if attr_or_equals:
            left_attr = attr_or_equals.group(1)
            left_value = attr_or_equals.group(3)
            right_attr = attr_or_equals.group(4)
            right_value = attr_or_equals.group(6)
            attr_aliases = {
                "contentDescription": "content-desc",
                "resourceId": "resource-id",
            }
            left_norm = attr_aliases.get(left_attr, left_attr)
            right_norm = attr_aliases.get(right_attr, right_attr)
            actual_left = (xml_node.attrib.get(left_norm, "") or "") == left_value
            actual_right = (xml_node.attrib.get(right_norm, "") or "") == right_value
            return actual_left or actual_right

        return False

    def _find_xml_nodes_for_runtime_xpath(self, xpath: str, root: ET.Element) -> List[ET.Element]:
        segments = self._split_xpath_segments_runtime(xpath)
        if not segments:
            return []

        current_nodes: List[ET.Element] = [root]
        for segment in segments:
            class_name, predicates = self._parse_segment_predicates(segment)
            next_nodes: List[ET.Element] = []
            for parent in current_nodes:
                children = [child for child in list(parent) if child.tag == "node"]
                for child in children:
                    if class_name and self._xml_short_class(child) != class_name:
                        continue
                    if all(self._match_xml_predicate(child, parent, predicate, class_name) for predicate in predicates):
                        next_nodes.append(child)
            current_nodes = next_nodes
            if not current_nodes:
                break
        return current_nodes

    def _match_runtime_summary_to_xml_node(self, summary: Dict[str, str], xml_node: ET.Element) -> bool:
        class_name = (summary.get("className") or "").strip()
        runtime_text = (summary.get("text") or "").strip()
        xml_class = (xml_node.attrib.get("class", "") or "").strip()
        if class_name and xml_class != class_name:
            return False
        if runtime_text:
            xml_text = (xml_node.attrib.get("text", "") or "").strip()
            xml_desc = (xml_node.attrib.get("content-desc", "") or "").strip()
            return runtime_text == xml_text or runtime_text == xml_desc
        return True

    def _get_xml_node_index(self, node: ET.Element, parent: Optional[ET.Element]) -> int:
        if parent is None:
            return 1
        node_cls = node.attrib.get('class', '') or ''
        siblings = [child for child in list(parent) if (child.attrib.get('class', '') or '') == node_cls]
        try:
            return siblings.index(node) + 1
        except ValueError:
            return 1

    def _find_matching_xml_node(self, elem: Dict, root: ET.Element) -> Optional[ET.Element]:
        best_node: Optional[ET.Element] = None
        best_score = -1
        tie = False

        for node in root.iter('node'):
            score = self._score_xml_node_match(elem, node)
            if score > best_score:
                best_score = score
                best_node = node
                tie = False
            elif score == best_score and score >= 0:
                tie = True

        if best_score < 0 or tie:
            return None
        return best_node

    def get_node_snippet_for_element(self, elem: Dict[str, Any], visible_only: bool = True) -> Optional[str]:
        root = self._get_ui_tree_root(force_refresh=True, visible_only=visible_only)
        if root is None:
            return None
        xml_node = self._find_matching_xml_node(elem, root)
        if xml_node is None:
            return None
        return self._format_xml_node_snippet(xml_node)

    def get_node_snippets_for_xpath(self, xpath: str, visible_only: bool = True) -> List[str]:
        root = self._get_ui_tree_root(force_refresh=True, visible_only=visible_only)
        if root is None:
            return []
        summaries = self._get_xpath_runtime_summaries(xpath)
        if summaries:
            snippets: List[str] = []
            used: set[int] = set()
            xml_nodes = list(root.iter("node"))
            for summary in summaries:
                for xml_node in xml_nodes:
                    if id(xml_node) in used:
                        continue
                    if not self._match_runtime_summary_to_xml_node(summary, xml_node):
                        continue
                    used.add(id(xml_node))
                    snippets.append(self._format_xml_node_snippet(xml_node))
                    break
            if snippets:
                return snippets
        tree = self.get_ui_elements(force_refresh=True, visible_only=visible_only)
        if not tree:
            return []
        matches = self.find_by_xpath_all(tree, xpath)
        if not matches:
            return []
        snippets: List[str] = []
        seen: set[int] = set()
        for elem in matches:
            xml_node = self._find_matching_xml_node(elem, root)
            if xml_node is None or id(xml_node) in seen:
                continue
            seen.add(id(xml_node))
            snippets.append(self._format_xml_node_snippet(xml_node))
        return snippets

    def build_ui_tree_absolute_xpath(self, tree: List[Dict], elem: Dict) -> Optional[str]:
        xml_text = self.get_ui_tree_xml(force_refresh=True)
        if xml_text:
            try:
                root = ET.fromstring(xml_text)
                node = self._find_matching_xml_node(elem, root)
                if node is not None:
                    parent_map = self._build_xml_parent_map(root)
                    segments: List[str] = []
                    current: Optional[ET.Element] = node
                    while current is not None and current.tag == 'node':
                        parent = parent_map.get(id(current))
                        index = self._get_xml_node_index(current, parent)
                        if current is node:
                            segments.append(self._make_target_segment_from_xml(current, index, parent))
                        else:
                            full_cls = current.attrib.get('class', '') or 'node'
                            cls = full_cls.split('.')[-1] if '.' in full_cls else full_cls
                            segments.append(f"{cls}[{index}]")
                        current = parent if isinstance(parent, ET.Element) else None
                    if segments:
                        segments.reverse()
                        return '/' + '/'.join(segments)
            except ET.ParseError:
                pass

        debug_xpath = elem.get('xpath', '') or ''
        segments = self._split_debug_xpath(debug_xpath)
        if not segments:
            return None

        runtime_absolute = self._make_absolute_xpath(tree, elem.get('refId'))
        runtime_segments = [s for s in (runtime_absolute or '').lstrip('/').split('/') if s]
        runtime_target_segment = runtime_segments[-1] if runtime_segments else ''
        runtime_index = self._extract_path_index(runtime_target_segment)

        segments[-1] = self._make_target_segment(elem, segments[-1], runtime_index)
        return '/' + '/'.join(segments)

    def build_runtime_absolute_xpath(self, tree: List[Dict], elem: Dict) -> Optional[str]:
        ui_tree_absolute = self.build_ui_tree_absolute_xpath(tree, elem)
        if not ui_tree_absolute:
            return None

        segments = [s for s in ui_tree_absolute.lstrip('/').split('/') if s]
        if not segments:
            return None

        return '/hierarchy/' + '/'.join(segments)

    def _ancestor_to_target_path(
        self, tree: List[Dict], target_ref_id: int
    ) -> Optional[str]:
        """
        Build an ancestor-relative XPath.

        Walk upward from the target and find the nearest ancestor that can be
        uniquely identified without refId, then connect that ancestor to the
        target with `//` plus the intermediate class+position path.

        Example: //LinearLayout[@text='Search']//EditText[1]
        """
        nodes = self._build_tree_structure(tree)
        if target_ref_id not in nodes:
            return None

        path_ids: List[int] = []
        cur = target_ref_id
        while cur is not None:
            path_ids.append(cur)
            cur = nodes[cur]['parent_ref_id']
        path_ids.reverse()  # Order from root to target

        for i in range(len(path_ids) - 2, -1, -1):
            ancestor_id = path_ids[i]
            ancestor_node = nodes[ancestor_id]
            ancestor_elem = ancestor_node['elem']
            a_cls = ancestor_elem.get('simpleClassName', '')
            a_text = ancestor_elem.get('text', '') or ''
            a_desc = ancestor_elem.get('contentDesc', '') or ''
            a_rid = ancestor_elem.get('resourceId', '') or ''

            if a_text:
                xp = f'//{a_cls}[@text={self._escape_xpath_value(a_text)}]'
                if len(self.find_by_xpath_all(tree, xp)) == 1:
                    return self._build_descendant_path(
                        tree, nodes, ancestor_id, target_ref_id, xp
                    )

            if a_desc:
                xp = f'//{a_cls}[@contentDescription={self._escape_xpath_value(a_desc)}]'
                if len(self.find_by_xpath_all(tree, xp)) == 1:
                    return self._build_descendant_path(
                        tree, nodes, ancestor_id, target_ref_id, xp
                    )

            if a_rid:
                xp = f'//{a_cls}[@resourceId={self._escape_xpath_value(a_rid)}]'
                if len(self.find_by_xpath_all(tree, xp)) == 1:
                    return self._build_descendant_path(
                        tree, nodes, ancestor_id, target_ref_id, xp
                    )

            if a_text and a_rid:
                xp = f'//{a_cls}[@text={self._escape_xpath_value(a_text)}][@resourceId={self._escape_xpath_value(a_rid)}]'
                if len(self.find_by_xpath_all(tree, xp)) == 1:
                    return self._build_descendant_path(
                        tree, nodes, ancestor_id, target_ref_id, xp
                    )

            if a_text and ancestor_elem.get('clickable'):
                xp = f'//{a_cls}[@text={self._escape_xpath_value(a_text)}][clickable]'
                if len(self.find_by_xpath_all(tree, xp)) == 1:
                    return self._build_descendant_path(
                        tree, nodes, ancestor_id, target_ref_id, xp
                    )

        return None

    def _build_descendant_path(
        self, tree: List[Dict], nodes: Dict[int, Dict],
        ancestor_id: int, target_ref_id: int, ancestor_xp: str
    ) -> str:
        """
        Build the descendant path from an ancestor XPath to the target.

        Uses className + sibling index to distinguish repeated intermediate
        nodes of the same class.
        """
        path_ids: List[int] = []
        cur = target_ref_id
        while cur != ancestor_id:
            path_ids.insert(0, cur)  # Insert at the front so the path starts at the ancestor
            cur = nodes[cur]['parent_ref_id']
            if cur is None:
                break

        parts: List[str] = []
        for ref_id in path_ids:
            node = nodes[ref_id]
            elem = node['elem']
            cls = elem.get('simpleClassName', '')
            if not cls:
                continue

            parent_ref = node['parent_ref_id']
            parent_node = nodes.get(parent_ref)
            siblings = parent_node['children_ref_ids'] if parent_node else []
            same_cls = [sid for sid in siblings
                        if sid in nodes and nodes[sid]['elem'].get('simpleClassName') == cls]
            try:
                idx = same_cls.index(ref_id) + 1
            except ValueError:
                idx = 1

            parts.append(f'{cls}[{idx}]')

        if not parts:
            return ancestor_xp

        return ancestor_xp + '//' + '/'.join(parts)

    def generate_xpath_candidates(
        self, elem: Dict, tree: List[Dict]
    ) -> List[Tuple[str, int, str]]:
        """
        Generate multiple XPath candidates for an element and sort them by match count.

        The emitted XPaths never include refId directly; refId is only used for
        internal tree structure calculations.

        Returns: List[(xpath_string, match_count, strategy_description)]
        Strategy priority:
          1. text (directly match the element text)
          2. contentDesc (use the icon/content description)
          3. ancestor-relative (ancestor node + descendant path)
          4. className+position (sibling index when the ancestor is unique)
          5. className + resourceId
          6. className + text + resourceId (combined)
          7. className + text + contentDesc (combined)
          8. className-only fallback
        """
        candidates: List[Tuple[str, int, str]] = []
        seen_xpaths: set = set()

        def add(xp: str, strategy: str) -> None:
            if xp in seen_xpaths:
                return
            seen_xpaths.add(xp)
            matches = self.find_by_xpath_all(tree, xp)
            candidates.append((xp, len(matches), strategy))

        cls = elem.get('simpleClassName', '')
        if not cls:
            return candidates

        ref_id = elem.get('refId')
        text = elem.get('text', '') or ''
        desc = elem.get('contentDesc', '') or ''
        rid = elem.get('resourceId', '') or ''


        if text:
            xp = f'//{cls}[@text={self._escape_xpath_value(text)}]'
            add(xp, 'text')
            if elem.get('clickable'):
                add(f'//{cls}[@text={self._escape_xpath_value(text)}][clickable]', 'text+clickable')

        if desc:
            xp = f'//{cls}[@contentDescription={self._escape_xpath_value(desc)}]'
            add(xp, 'contentDescription')

        if ref_id is not None:
            ar_path = self._ancestor_to_target_path(tree, ref_id)
            if ar_path:
                add(ar_path, 'ancestor-relative')

        if rid:
            add(f'//{cls}[@resourceId={self._escape_xpath_value(rid)}]', 'className+resourceId')

        if text and rid:
            add(f'//{cls}[@text={self._escape_xpath_value(text)}][@resourceId={self._escape_xpath_value(rid)}]',
                'className+text+resourceId')

        if text and desc:
            add(f'//{cls}[@text={self._escape_xpath_value(text)}][@contentDescription={self._escape_xpath_value(desc)}]',
                'className+text+contentDescription')

        if ref_id is not None:
            pos_path = self._ancestor_to_target_path(tree, ref_id)
            if pos_path and '[@refId=' not in pos_path:
                add(pos_path, 'className+position')

        add(f'//{cls}', 'className-only')

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
        candidates.sort(key=lambda c: (
            0 if c[1] == 1 else 1,  # unique first
            strategy_order.get(c[2], 99),  # then by strategy
            c[1]  # then by match count
        ))
        return candidates

    def generate_multi_xpath_candidates(
        self, elems: List[Dict[str, Any]], tree: List[Dict[str, Any]]
    ) -> List[Tuple[str, int, str]]:
        """Generate XPath candidates that match multiple selected elements."""
        if not elems:
            return []

        selected = [elem for elem in elems if elem.get("refId") is not None]
        if not selected:
            return []

        absolute_paths: List[str] = []
        path_segments: List[List[str]] = []
        for elem in selected:
            runtime_xpath = self.build_runtime_absolute_xpath(tree, elem)
            if not runtime_xpath:
                continue
            absolute_paths.append(runtime_xpath)
            path_segments.append([segment for segment in runtime_xpath.split("/") if segment])

        if len(absolute_paths) != len(selected):
            return []

        nodes = self._build_tree_structure(tree)

        candidates: List[Tuple[str, int, str]] = []
        seen: set[str] = set()

        def add(xpath: str, strategy: str) -> None:
            if not xpath or xpath in seen:
                return
            seen.add(xpath)
            count = self._get_xpath_match_count(xpath)
            candidates.append((xpath, count if count is not None else -1, strategy))

        if len(absolute_paths) > 1:
            add(" | ".join(absolute_paths), "absolute-union")
        else:
            add(absolute_paths[0], "absolute-single")

        parent_segments = self._common_path_segments([segments[:-1] for segments in path_segments])
        target_segments = [segments[-1] for segments in path_segments if segments]
        target_classes = [self._extract_segment_class(segment) for segment in target_segments]
        target_indexes: List[Optional[int]] = []
        for elem, segment in zip(selected, target_segments):
            ref_id = elem.get("refId")
            node = nodes.get(ref_id) if ref_id is not None else None
            parent_ref_id = node.get("parent_ref_id") if node else None
            parent_node = nodes.get(parent_ref_id) if parent_ref_id is not None else None
            cls = self._extract_segment_class(segment)
            if not parent_node or not cls:
                target_indexes.append(self._extract_path_index(segment))
                continue
            siblings = parent_node.get("children_ref_ids", [])
            same_class_siblings = [
                sid for sid in siblings
                if sid in nodes and nodes[sid]["elem"].get("simpleClassName") == cls
            ]
            try:
                target_indexes.append(same_class_siblings.index(ref_id) + 1)
            except ValueError:
                target_indexes.append(self._extract_path_index(segment))

        if parent_segments and len(set(target_classes)) == 1 and target_classes[0]:
            parent_xpath = "/" + "/".join(parent_segments)
            cls = target_classes[0]
            class_xpath = f"{parent_xpath}/{cls}"
            add(class_xpath, "same-parent class")

            if all(index is not None for index in target_indexes):
                indexes = [int(index) for index in target_indexes if index is not None]
                position_predicate = " or ".join(f"position()={index}" for index in indexes)
                add(f"{class_xpath}[{position_predicate}]", "same-parent positions")

                ordered = sorted(indexes)
                if ordered == list(range(ordered[0], ordered[-1] + 1)):
                    add(
                        f"{class_xpath}[position()>={ordered[0]} and position()<={ordered[-1]}]",
                        "same-parent contiguous-range",
                    )

        target_count = len(selected)
        exact_order = {
            "same-parent positions": 0,
            "same-parent contiguous-range": 1,
            "same-parent class": 2,
            "absolute-union": 3,
            "absolute-single": 4,
        }
        superset_order = {
            "same-parent class": 0,
            "same-parent positions": 1,
            "same-parent contiguous-range": 2,
            "absolute-union": 3,
            "absolute-single": 4,
        }
        candidates.sort(
            key=lambda candidate: (
                0 if candidate[1] == target_count else 1 if candidate[1] > target_count else 2 if candidate[1] >= 0 else 3,
                exact_order.get(candidate[2], 99) if candidate[1] == target_count else
                superset_order.get(candidate[2], 99) if candidate[1] > target_count else
                exact_order.get(candidate[2], 99),
                abs(candidate[1] - target_count) if candidate[1] >= 0 else 999,
                candidate[1] if candidate[1] >= 0 else 999,
            )
        )
        return candidates

    def tap_by_xpath(self, xpath: str) -> bool:
        """Tap an element by XPath using Android runtime locator mode."""
        return self._run_single_operation(
            template_id="tap-xpath",
            operation_type="android.touch.tap",
            parameters={"mode": "locator", "xpath": xpath},
            success_message=f"Tapped XPath [{xpath}]",
            failure_prefix="Tap failed"
        )

    def input_by_xpath(self, xpath: str, text: str) -> bool:
        """Input text by XPath using Android runtime locator mode."""
        _target, detail, reason = self._resolve_xpath_input_target(xpath)
        if reason == "tree_unavailable":
            print("FAILED: could not refresh the current UI tree before XPath input", file=sys.stderr)
            return False
        if reason == "not_found":
            print(f"FAILED: XPath matched no elements: {xpath}", file=sys.stderr)
            return False
        if reason == "multiple_matches":
            count = self._get_xpath_match_count(xpath)
            if count is None:
                count = -1
            print(
                f"FAILED: XPath matched {count if count >= 0 else 'multiple'} elements; "
                "refine it to one input target.",
                file=sys.stderr,
            )
            return False
        if reason == "not_input":
            cls = (detail or {}).get("className") or "unknown"
            print(
                f"FAILED: XPath resolved to non-input element class={cls}. "
                "Refusing to guess a nearby input field.",
                file=sys.stderr,
            )
            return False

        return self._run_single_operation(
            template_id="input-xpath",
            operation_type="android.element.input",
            parameters={
                "xpath": xpath,
                "value": text,
                "clearFirst": True
            },
            success_message=(
                f"Cleared XPath [{xpath}]"
                if text == ""
                else f"Input '{text}' to XPath [{xpath}]"
            ),
            failure_prefix="FAILED"
        )

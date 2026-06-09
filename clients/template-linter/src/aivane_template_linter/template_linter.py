#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIVane Template Linter.

Static validation for AIVane template configuration files.
"""

import json
import os
import re
import sys
import copy
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml


JsonPath = Tuple[Any, ...]
TAB_WIDTH = 4


@dataclass(frozen=True)
class SourceLocation:
    """Source position for a JSON node."""
    file_path: str
    line: int
    column: int
    offset: int = -1


class JsonSourceMapBuilder:
    """Build a best-effort JSON path -> source location map.

    The linter already parses templates with Python's JSON decoder. This small
    scanner only records where each object key and array item starts so lint
    messages can point back to a useful line, even for tab-indented JSON files.
    """

    def __init__(self, text: str, file_path: str):
        self.text = text
        self.file_path = file_path
        self.index = 0
        self.line = 1
        self.column = 1
        self.locations: Dict[JsonPath, SourceLocation] = {}

    def build(self) -> Dict[JsonPath, SourceLocation]:
        try:
            self._parse_value(())
            return self.locations
        except ValueError:
            return {}

    def _set_location(self, path: JsonPath, line: int, column: int) -> None:
        self.locations.setdefault(path, SourceLocation(self.file_path, line, column, self.index))

    def _peek(self) -> str:
        if self.index >= len(self.text):
            return ""
        return self.text[self.index]

    def _advance(self) -> str:
        ch = self._peek()
        if not ch:
            return ch
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        elif ch == "\t":
            self.column += TAB_WIDTH - ((self.column - 1) % TAB_WIDTH)
        else:
            self.column += 1
        return ch

    def _skip_ws(self) -> None:
        while self._peek() and self._peek() in " \t\r\n":
            self._advance()

    def _expect(self, expected: str) -> None:
        if self._peek() != expected:
            raise ValueError(f"Expected {expected!r}")
        self._advance()

    def _parse_value(self, path: JsonPath) -> None:
        self._skip_ws()
        line, column = self.line, self.column
        self._set_location(path, line, column)
        ch = self._peek()
        if ch == "{":
            self._parse_object(path)
        elif ch == "[":
            self._parse_array(path)
        elif ch == '"':
            self._parse_string()
        elif ch == "-" or ch.isdigit():
            self._parse_number()
        elif ch:
            self._parse_literal()
        else:
            raise ValueError("Unexpected end of JSON")

    def _parse_object(self, path: JsonPath) -> None:
        self._expect("{")
        self._skip_ws()
        if self._peek() == "}":
            self._advance()
            return

        while True:
            self._skip_ws()
            key_line, key_column = self.line, self.column
            key = self._parse_string()
            key_path = path + (key,)
            self._set_location(key_path, key_line, key_column)
            self._skip_ws()
            self._expect(":")
            self._parse_value(key_path)
            self._skip_ws()
            ch = self._peek()
            if ch == ",":
                self._advance()
                continue
            if ch == "}":
                self._advance()
                return
            raise ValueError("Expected ',' or '}'")

    def _parse_array(self, path: JsonPath) -> None:
        self._expect("[")
        self._skip_ws()
        if self._peek() == "]":
            self._advance()
            return

        item_index = 0
        while True:
            self._parse_value(path + (item_index,))
            self._skip_ws()
            ch = self._peek()
            if ch == ",":
                self._advance()
                item_index += 1
                continue
            if ch == "]":
                self._advance()
                return
            raise ValueError("Expected ',' or ']'")

    def _parse_string(self) -> str:
        self._expect('"')
        chars: List[str] = []
        while True:
            ch = self._peek()
            if not ch:
                raise ValueError("Unterminated string")
            if ch == '"':
                self._advance()
                return "".join(chars)
            if ch == "\\":
                self._advance()
                esc = self._peek()
                if not esc:
                    raise ValueError("Unterminated escape")
                self._advance()
                if esc == "u":
                    hex_digits = ""
                    for _ in range(4):
                        digit = self._peek()
                        if not digit:
                            raise ValueError("Unterminated unicode escape")
                        hex_digits += digit
                        self._advance()
                    try:
                        chars.append(chr(int(hex_digits, 16)))
                    except ValueError as exc:
                        raise ValueError("Invalid unicode escape") from exc
                else:
                    chars.append(esc)
                continue
            chars.append(ch)
            self._advance()

    def _parse_number(self) -> None:
        while self._peek() and self._peek() not in " \t\r\n,]}":
            self._advance()

    def _parse_literal(self) -> None:
        for literal in ("true", "false", "null"):
            if self.text.startswith(literal, self.index):
                for _ in literal:
                    self._advance()
                return
        raise ValueError("Invalid literal")


class ErrorLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class LintError:
    """Represents one lint error or warning."""
    level: ErrorLevel
    code: str
    message: str
    template_id: str = ""
    operation_index: int = -1
    operation_type: str = ""
    parameter_name: str = ""
    suggestion: str = ""
    source_file: str = ""
    line: int = -1
    column: int = -1
    operation_path: str = ""
    json_path: str = ""

    def __str__(self) -> str:
        location = []
        if self.source_file and self.line > 0:
            file_location = f"{self.source_file}:{self.line}"
            if self.column > 0:
                file_location += f":{self.column}"
            location.append(file_location)
        if self.template_id:
            location.append(f"template: {self.template_id}")
        if self.operation_index >= 0:
            location.append(f"operation[{self.operation_index}]")
        if self.operation_type:
            location.append(f"type: {self.operation_type}")
        if self.parameter_name:
            location.append(f"param: {self.parameter_name}")
        if self.operation_path:
            location.append(f"path: {self.operation_path}")
        if self.json_path and self.json_path != self.operation_path:
            location.append(f"json: {self.json_path}")

        loc_str = " | ".join(location) if location else "template"
        result = f"[{self.level.value}] {self.code}: {self.message}"
        if location:
            result = f"{loc_str} - {result}"
        if self.suggestion:
            result += f"\n  Suggestion: {self.suggestion}"
        return result


@dataclass
class LintResult:
    """Lint result collection."""
    errors: List[LintError] = field(default_factory=list)
    warnings: List[LintError] = field(default_factory=list)
    infos: List[LintError] = field(default_factory=list)

    @property
    def total_errors(self) -> int:
        return len(self.errors)

    @property
    def total_warnings(self) -> int:
        return len(self.warnings)

    @property
    def has_errors(self) -> bool:
        return self.total_errors > 0

    def add_error(self, error: LintError) -> None:
        self.errors.append(error)

    def add_warning(self, warning: LintError) -> None:
        self.warnings.append(warning)

    def add_info(self, info: LintError) -> None:
        self.infos.append(info)

    def merge(self, other: 'LintResult') -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.infos.extend(other.infos)


class VariableScope:
    """Variable scope for tracking defined variables."""

    def __init__(self, parent: Optional['VariableScope'] = None):
        self.parent = parent
        self.variables: Dict[str, int] = {}  # variable_name -> definition_index

    def define(self, name: str, index: int) -> None:
        self.variables[name] = index

    def is_defined(self, name: str) -> bool:
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.is_defined(name)
        return False

    def get_definition_index(self, name: str) -> Optional[int]:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get_definition_index(name)
        return None

    def clone(self) -> 'VariableScope':
        new_scope = VariableScope(self.parent)
        new_scope.variables = self.variables.copy()
        return new_scope


class OperationSpecRegistry:
    """Operation type specification registry."""

    def __init__(self, docs_dir: Optional[str] = None):
        self.specs: Dict[str, Dict[str, Any]] = {}
        self.aliases: Dict[str, str] = {}
        self.docs_dir = Path(docs_dir) if docs_dir else (
            Path(__file__).resolve().parent / "operationtypes"
        )
        self._load_specs(self.docs_dir)

    def _load_specs(self, docs_dir: Path) -> None:
        """Load specs from OperationType Markdown front matter."""
        if not docs_dir.exists():
            print(f"Warning: Operation docs directory not found: {docs_dir}", file=sys.stderr)
            return

        for md_file in docs_dir.rglob("*.md"):
            front_matter = self._extract_front_matter(md_file)
            if not front_matter:
                continue

            op_type, spec = self._normalize_doc_spec(front_matter)
            if not op_type or not spec:
                continue

            self.specs[op_type] = spec
            for alias in spec.get("aliases", []):
                self.aliases[alias] = op_type

        if not self.specs:
            print(f"Warning: No OperationType schemas found in docs directory: {docs_dir}", file=sys.stderr)

    def _extract_front_matter(self, md_file: Path) -> Optional[Dict[str, Any]]:
        """Extract YAML/JSON front matter from a Markdown file."""
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Warning: Failed to read doc file {md_file}: {exc}", file=sys.stderr)
            return None

        if not text.startswith("---"):
            return None

        match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
        if not match:
            return None

        front_matter_text = match.group(1)

        try:
            data = yaml.safe_load(front_matter_text) or {}
        except yaml.YAMLError:
            # Preserve compatibility with historical copied docs that contain JSON trailing commas.
            sanitized = re.sub(r",(\s*[}\]])", r"\1", front_matter_text)
            try:
                data = yaml.safe_load(sanitized) or {}
            except yaml.YAMLError as exc:
                print(f"Warning: Failed to parse YAML front matter in {md_file}: {exc}", file=sys.stderr)
                return None

        if not isinstance(data, dict):
            print(f"Warning: Invalid YAML front matter in {md_file}: expected object", file=sys.stderr)
            return None

        return data

    def _normalize_doc_spec(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Normalize front matter metadata into the linter's internal spec format."""
        op_type = data.get("operationType")
        if not isinstance(op_type, str) or not op_type.strip():
            return None, None

        required_params: List[str] = []
        optional_params: List[str] = []
        param_types: Dict[str, Any] = {}
        param_enums: Dict[str, List[str]] = {}
        param_deprecated: Dict[str, bool] = {}
        param_deprecated_messages: Dict[str, str] = {}
        param_allow_empty: Dict[str, bool] = {}

        parameters = self._normalize_parameters(data)
        if parameters is None:
            return None, None

        for param_name, param_spec in parameters.items():
            param_type = self._merge_param_types(
                param_spec.get("type", "any"),
                param_spec.get("allowedTypes"),
            )
            param_types[param_name] = param_type

            if bool(param_spec.get("required", False)):
                required_params.append(param_name)
            else:
                optional_params.append(param_name)

            enum_values = param_spec.get("enumValues", param_spec.get("enum", []))
            if isinstance(enum_values, list) and enum_values:
                param_enums[param_name] = [str(v) for v in enum_values]

            if bool(param_spec.get("deprecated", False)):
                param_deprecated[param_name] = True
                deprecated_message = param_spec.get("deprecatedMessage")
                if isinstance(deprecated_message, str) and deprecated_message.strip():
                    param_deprecated_messages[param_name] = deprecated_message.strip()

            param_allow_empty[param_name] = bool(param_spec.get("allowEmpty", False))

        constraints = data.get("constraints", {}) or {}
        if not isinstance(constraints, dict):
            constraints = {}

        platforms = data.get("platforms", [])
        if isinstance(platforms, str):
            platforms = [platforms]
        if not isinstance(platforms, list):
            platforms = []

        return op_type, {
            "category": data.get("category", ""),
            "displayName": data.get("displayName", ""),
            "description": data.get("description", data.get("summary", "")),
            "aliases": [str(alias) for alias in data.get("aliases", []) if isinstance(alias, str)],
            "platforms": [str(platform).lower() for platform in platforms],
            "requiredParams": required_params,
            "optionalParams": optional_params,
            "allowedParams": list(parameters.keys()),
            "paramTypes": param_types,
            "paramEnums": param_enums,
            "paramDeprecated": param_deprecated,
            "paramDeprecatedMessages": param_deprecated_messages,
            "paramAllowEmpty": param_allow_empty,
            "oneOf": constraints.get("oneOf", []) or [],
            "oneOfRequired": constraints.get("oneOfRequired", []) or [],
            "allOfRequired": constraints.get("allOfRequired", []) or [],
            "conditionalRequired": constraints.get("conditionalRequired", []) or [],
            "conditionalOneOfRequired": constraints.get("conditionalOneOfRequired", []) or [],
            "nestedOperations": constraints.get("nestedOperations", []) or [],
            "requiresLoopContext": bool(constraints.get("requiresLoopContext", False)),
            "rejectUnknownParams": bool(constraints.get("rejectUnknownParams", True)),
        }

    def _normalize_parameters(self, data: Dict[str, Any]) -> Optional[Dict[str, Dict[str, Any]]]:
        parameters = data.get("parameters")
        if isinstance(parameters, list):
            normalized = {}
            for item in parameters:
                if not isinstance(item, dict):
                    continue
                param_name = item.get("name")
                if not isinstance(param_name, str) or not param_name.strip():
                    continue
                normalized[param_name] = dict(item)
            return normalized

        if "parameters" in data:
            return {}

        return None

    def _merge_param_types(self, raw_type: Any, allowed_types: Any) -> Any:
        types: List[str] = []

        def add_type(value: Any) -> None:
            if value is None:
                return
            if isinstance(value, list):
                for item in value:
                    add_type(item)
                return
            normalized = str(value).lower()
            if normalized not in types:
                types.append(normalized)

        add_type(raw_type)
        add_type(allowed_types)
        if not types:
            return "any"
        if len(types) == 1:
            return types[0]
        return types

    def resolve_alias(self, op_type: str) -> str:
        """Resolve an operation type alias."""
        return self.aliases.get(op_type, op_type)

    def get_spec(self, op_type: str) -> Optional[Dict[str, Any]]:
        """Get an operation type spec."""
        resolved = self.resolve_alias(op_type)
        return self.specs.get(resolved)

    def is_known_type(self, op_type: str) -> bool:
        """Return whether the operation type is known."""
        resolved = self.resolve_alias(op_type)
        return resolved in self.specs

    def get_all_types(self) -> Set[str]:
        """Get all known operation types."""
        return set(self.specs.keys()) | set(self.aliases.keys())


class TemplateSourcePreprocessor:
    """Template source preprocessor aligned with JsonTemplateLoader behavior."""

    OPERATION_CONTAINER_KEYS = {
        "operations",
        "tryBranch",
        "catchBranch",
        "finallyBranch",
        "recoveryBranch",
    }
    BRANCH_KEYS = {"ifBranch", "elseBranch"}
    FRAGMENT_ARGS_KEY = "$args"
    LOCATOR_KEYS = {
        "xpath",
        "id",
        "text",
        "className",
        "contentDescription",
        "elementName",
    }

    @classmethod
    def preprocess(cls, template: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(template, dict):
            return template

        expanded = copy.deepcopy(template)
        locators = expanded.get("locators")
        predicates = expanded.get("predicates")
        fragments = expanded.get("fragments")

        operations = expanded.get("operations")
        if isinstance(operations, list):
            expanded["operations"] = cls._expand_operation_array(
                operations, locators, predicates, fragments, []
            )

        return expanded

    @classmethod
    def _expand_operation_array(
        cls,
        operations: List[Any],
        locators: Any,
        predicates: Any,
        fragments: Any,
        fragment_stack: List[str],
    ) -> List[Any]:
        expanded: List[Any] = []
        for item in operations:
            if not isinstance(item, dict):
                expanded.append(item)
                continue

            if "$fragment" in item:
                expanded.extend(
                    cls._resolve_fragment_operations(
                        item["$fragment"],
                        item.get(cls.FRAGMENT_ARGS_KEY),
                        locators,
                        predicates,
                        fragments,
                        fragment_stack,
                    )
                )
                continue

            expanded.append(
                cls._expand_operation(item, locators, predicates, fragments, fragment_stack)
            )

        return expanded

    @classmethod
    def _expand_operation_node(
        cls,
        node: Any,
        locators: Any,
        predicates: Any,
        fragments: Any,
        fragment_stack: List[str],
    ) -> Any:
        if isinstance(node, list):
            return cls._expand_operation_array(node, locators, predicates, fragments, fragment_stack)
        if not isinstance(node, dict):
            return node
        if "$fragment" in node:
            return cls._resolve_fragment_operations(
                node["$fragment"], node.get(cls.FRAGMENT_ARGS_KEY), locators, predicates, fragments, fragment_stack
            )
        if "operationType" in node:
            return cls._expand_operation(node, locators, predicates, fragments, fragment_stack)
        return copy.deepcopy(node)

    @classmethod
    def _expand_operation(
        cls,
        operation: Dict[str, Any],
        locators: Any,
        predicates: Any,
        fragments: Any,
        fragment_stack: List[str],
    ) -> Dict[str, Any]:
        expanded = copy.deepcopy(operation)

        params = expanded.get("parameters")
        if isinstance(params, dict):
            expanded["parameters"] = cls._expand_parameters(
                params, locators, predicates, fragments, fragment_stack
            )

        guards = expanded.get("guards")
        if isinstance(guards, dict):
            expanded["guards"] = cls._expand_guards(
                guards, locators, predicates, fragments, fragment_stack
            )

        return expanded

    @classmethod
    def _expand_parameters(
        cls,
        params: Dict[str, Any],
        locators: Any,
        predicates: Any,
        fragments: Any,
        fragment_stack: List[str],
    ) -> Dict[str, Any]:
        expanded = cls._merge_locator_ref(copy.deepcopy(params), locators)
        expanded = cls._merge_predicate_ref(expanded, locators, predicates)
        for key in cls.OPERATION_CONTAINER_KEYS | cls.BRANCH_KEYS:
            if key in expanded:
                expanded[key] = cls._expand_operation_node(
                    expanded[key], locators, predicates, fragments, fragment_stack
                )
        return expanded

    @classmethod
    def _expand_guards(
        cls,
        guards: Dict[str, Any],
        locators: Any,
        predicates: Any,
        fragments: Any,
        fragment_stack: List[str],
    ) -> Dict[str, Any]:
        expanded = copy.deepcopy(guards)

        for phase_key in ("preconditions", "postconditions"):
            if phase_key in expanded and isinstance(expanded[phase_key], list):
                expanded[phase_key] = cls._expand_guard_conditions(
                    expanded[phase_key], locators, predicates
                )

        if "recoveryBranch" in expanded and isinstance(expanded["recoveryBranch"], list):
            expanded["recoveryBranch"] = cls._expand_operation_array(
                expanded["recoveryBranch"], locators, predicates, fragments, fragment_stack
            )

        return expanded

    @classmethod
    def _expand_guard_conditions(
        cls,
        conditions: List[Any],
        locators: Any,
        predicates: Any,
    ) -> List[Any]:
        expanded: List[Any] = []
        for condition in conditions:
            if not isinstance(condition, dict):
                expanded.append(condition)
                continue

            if "predicateRef" in condition:
                expanded.extend(
                    cls._resolve_predicate_conditions(condition["predicateRef"], locators, predicates)
                )
                continue

            expanded.append(cls._merge_locator_ref(copy.deepcopy(condition), locators))
        return expanded

    @classmethod
    def _resolve_predicate_conditions(
        cls,
        predicate_name: str,
        locators: Any,
        predicates: Any,
    ) -> List[Dict[str, Any]]:
        if not isinstance(predicates, dict) or predicate_name not in predicates:
            raise ValueError(f"Unknown predicateRef: {predicate_name}")

        predicate_value = predicates[predicate_name]
        if isinstance(predicate_value, list):
            raw_conditions = predicate_value
        elif isinstance(predicate_value, dict):
            if "allOf" in predicate_value and isinstance(predicate_value["allOf"], list):
                raw_conditions = predicate_value["allOf"]
            elif "conditions" in predicate_value and isinstance(predicate_value["conditions"], list):
                raw_conditions = predicate_value["conditions"]
            elif "anyOf" in predicate_value:
                raise ValueError(f"predicate anyOf is not supported yet: {predicate_name}")
            else:
                raise ValueError(f"Predicate is missing allOf/conditions: {predicate_name}")
        else:
            raise ValueError(f"Invalid predicate definition: {predicate_name}")

        result: List[Dict[str, Any]] = []
        for item in raw_conditions:
            if not isinstance(item, dict):
                raise ValueError(f"Predicate condition must be an object: {predicate_name}")
            result.append(cls._merge_locator_ref(copy.deepcopy(item), locators))
        return result

    @classmethod
    def _resolve_fragment_operations(
        cls,
        fragment_name: str,
        invocation_args: Any,
        locators: Any,
        predicates: Any,
        fragments: Any,
        fragment_stack: List[str],
    ) -> List[Dict[str, Any]]:
        if not isinstance(fragments, dict) or fragment_name not in fragments:
            raise ValueError(f"Unknown fragment: {fragment_name}")
        if fragment_name in fragment_stack:
            cycle = " -> ".join([*fragment_stack, fragment_name])
            raise ValueError(f"Fragment cycle detected: {cycle}")

        fragment_value = fragments[fragment_name]
        default_args: Dict[str, Any] = {}
        if isinstance(fragment_value, list):
            raw_operations = fragment_value
        elif isinstance(fragment_value, dict) and isinstance(fragment_value.get("operations"), list):
            raw_operations = fragment_value["operations"]
            if isinstance(fragment_value.get("parameters"), dict):
                default_args = copy.deepcopy(fragment_value["parameters"])
        else:
            raise ValueError(f"Invalid fragment definition: {fragment_name}")

        merged_args = default_args
        if isinstance(invocation_args, dict):
            merged_args.update(copy.deepcopy(invocation_args))

        substituted = cls._apply_fragment_args_to_value(raw_operations, merged_args)

        return cls._expand_operation_array(
            substituted,
            locators,
            predicates,
            fragments,
            [*fragment_stack, fragment_name],
        )

    @classmethod
    def _merge_locator_ref(cls, target: Dict[str, Any], locators: Any) -> Dict[str, Any]:
        locator_name = target.pop("locatorRef", None)
        if locator_name is None:
            return target

        if not isinstance(locators, dict) or locator_name not in locators:
            raise ValueError(f"Unknown locatorRef: {locator_name}")
        locator_value = locators[locator_name]
        if not isinstance(locator_value, dict):
            raise ValueError(f"Invalid locator definition: {locator_name}")

        merged: Dict[str, Any] = {}
        for key, value in locator_value.items():
            if key in cls.LOCATOR_KEYS:
                merged[key] = copy.deepcopy(value)
        merged.update(target)
        return merged

    @classmethod
    def _merge_predicate_ref(cls, target: Dict[str, Any], locators: Any, predicates: Any) -> Dict[str, Any]:
        predicate_name = target.pop("predicateRef", None)
        if predicate_name is None:
            return target

        conditions = cls._resolve_predicate_conditions(predicate_name, locators, predicates)
        if len(conditions) != 1:
            raise ValueError(f"predicateRef used as params must resolve to exactly one condition: {predicate_name}")

        merged: Dict[str, Any] = {}
        for key, value in conditions[0].items():
            if key in cls.LOCATOR_KEYS:
                merged[key] = copy.deepcopy(value)
        merged.update(target)
        return merged

    @classmethod
    def _apply_fragment_args_to_value(cls, value: Any, args: Dict[str, Any]) -> Any:
        if isinstance(value, list):
            return [cls._apply_fragment_args_to_value(item, args) for item in value]
        if isinstance(value, dict):
            return {
                key: cls._apply_fragment_args_to_value(item, args)
                for key, item in value.items()
            }
        if isinstance(value, str):
            return cls._apply_fragment_args_to_string(value, args)
        return copy.deepcopy(value)

    @classmethod
    def _apply_fragment_args_to_string(cls, template: str, args: Dict[str, Any]) -> Any:
        if not args:
            return template

        match = re.fullmatch(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}", template)
        if match:
            key = match.group(1)
            if key not in args:
                raise ValueError(f"Missing fragment argument: {key}")
            return copy.deepcopy(args[key])

        resolved = template
        for key, value in args.items():
            resolved = resolved.replace(f"{{{{{key}}}}}", "" if value is None else str(value))
        return resolved


class TemplateLinter:
    """Static linter for templates."""

    # Error code definitions.
    ERR_INVALID_JSON = "T001"
    ERR_MISSING_REQUIRED_FIELD = "T002"
    ERR_INVALID_OPERATION_TYPE = "T003"
    ERR_MISSING_REQUIRED_PARAM = "T004"
    ERR_INVALID_PARAM_TYPE = "T005"
    ERR_ONE_OF_REQUIRED = "T006"
    ERR_UNDEFINED_VARIABLE = "T007"
    ERR_INVALID_CONDITION_EXPR = "T008"
    ERR_BREAK_WITHOUT_LOOP = "T009"
    ERR_CONTINUE_WITHOUT_LOOP = "T010"
    ERR_INVALID_NESTED_OPERATION = "T011"
    ERR_UNKNOWN_PARAM = "T012"
    ERR_INVALID_ENUM_VALUE = "T013"
    ERR_EMPTY_PARAM_NOT_ALLOWED = "T014"
    ERR_INVALID_GUARDS = "T015"
    ERR_INVALID_GUARD_CONDITION = "T016"
    ERR_INVALID_GUARD_ACTION = "T017"
    ERR_INVALID_APP_JSON = "A001"
    ERR_MISSING_APP_FIELD = "A002"
    ERR_APP_HAS_NO_TEMPLATES = "A003"
    ERR_APP_MAIN_TEMPLATE_NOT_FOUND = "A004"
    ERR_APP_MAIN_TEMPLATE_AMBIGUOUS = "A005"
    ERR_DUPLICATE_TEMPLATE_ID = "A006"
    ERR_DUPLICATE_TEMPLATE_ALIAS = "A007"
    ERR_TEMPLATE_EXECUTE_TARGET_NOT_FOUND = "A008"
    ERR_TEMPLATE_EXECUTE_TARGET_AMBIGUOUS = "A009"
    ERR_TEMPLATE_EXECUTE_MISSING_REQUIRED_PARAM = "A010"
    WARN_EMPTY_OPERATIONS = "T101"
    WARN_UNUSED_VARIABLE = "T103"
    WARN_DEPRECATED_PARAM = "T104"
    WARN_APP_MAIN_TEMPLATE_ALIAS = "A101"
    WARN_TEMPLATE_EXECUTE_UNDECLARED_PARAM = "A102"

    NON_TEMPLATE_JSON_FILES = {"app.json", "elements.json", "package.json", "tsconfig.json"}

    def __init__(self, docs_dir: Optional[str] = None, platform: str = "all"):
        self.registry = OperationSpecRegistry(docs_dir)
        self.platform = platform.lower()
        self._current_source_file = ""
        self._current_source_text = ""
        self._current_source_map: Dict[JsonPath, SourceLocation] = {}

    def _build_source_map(self, text: str, file_path: str) -> Dict[JsonPath, SourceLocation]:
        return JsonSourceMapBuilder(text, file_path).build()

    def _format_json_path(self, path: Optional[JsonPath]) -> str:
        if not path:
            return ""
        result = ""
        for part in path:
            if isinstance(part, int):
                result += f"[{part}]"
            else:
                if result:
                    result += "."
                result += str(part)
        return result

    def _lookup_source_location(self, path: Optional[JsonPath]) -> Optional[SourceLocation]:
        if not path:
            return None
        current = path
        while current:
            location = self._current_source_map.get(current)
            if location:
                return location
            current = current[:-1]
        return self._current_source_map.get(())

    def _source_fields(
        self,
        operation_path: Optional[JsonPath] = None,
        json_path: Optional[JsonPath] = None,
        token: str = "",
    ) -> Dict[str, Any]:
        lookup_path = json_path or operation_path
        location = self._lookup_source_location(lookup_path)
        if token and location:
            token_location = self._find_token_location(location, token)
            if token_location:
                location = token_location
        fields: Dict[str, Any] = {
            "operation_path": self._format_json_path(operation_path),
            "json_path": self._format_json_path(lookup_path),
        }
        if location:
            fields.update({
                "source_file": location.file_path,
                "line": location.line,
                "column": location.column,
            })
        elif self._current_source_file:
            fields["source_file"] = self._current_source_file
        return fields

    def _find_token_location(self, start_location: SourceLocation, token: str) -> Optional[SourceLocation]:
        if not self._current_source_text or start_location.offset < 0 or not token:
            return None

        search_end = self._current_source_text.find("\n", start_location.offset)
        if search_end < 0:
            search_end = len(self._current_source_text)
        token_offset = self._current_source_text.find(token, start_location.offset, search_end)
        if token_offset < 0:
            token_offset = self._current_source_text.find(token, start_location.offset)
        if token_offset < 0:
            return None
        return self._source_location_from_offset(token_offset)

    def _source_location_from_offset(self, offset: int) -> SourceLocation:
        prefix = self._current_source_text[:offset]
        line = prefix.count("\n") + 1
        line_start = prefix.rfind("\n") + 1
        column = 1
        for ch in self._current_source_text[line_start:offset]:
            if ch == "\t":
                column += TAB_WIDTH - ((column - 1) % TAB_WIDTH)
            else:
                column += 1
        return SourceLocation(self._current_source_file, line, column, offset)

    def lint_file(self, file_path: str) -> LintResult:
        """Lint one template file."""
        path = Path(file_path)
        if path.name == "app.json":
            return self._lint_application_directory(path.parent)

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                template_text = f.read()
            template_data = json.loads(template_text)
            template_data = TemplateSourcePreprocessor.preprocess(template_data)
            previous_source_file = self._current_source_file
            previous_source_text = self._current_source_text
            previous_source_map = self._current_source_map
            self._current_source_file = str(path)
            self._current_source_text = template_text
            self._current_source_map = self._build_source_map(template_text, str(path))
            try:
                return self._lint_template(template_data, file_path)
            finally:
                self._current_source_file = previous_source_file
                self._current_source_text = previous_source_text
                self._current_source_map = previous_source_map
        except FileNotFoundError:
            result = LintResult()
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_JSON,
                message=f"File not found: {file_path}"
            ))
            return result
        except json.JSONDecodeError as e:
            result = LintResult()
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_JSON,
                message=f"Invalid JSON: {e}",
                template_id=file_path
            ))
            return result
        except ValueError as e:
            result = LintResult()
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_JSON,
                message=f"Template source preprocessing failed: {e}",
                template_id=file_path
            ))
            return result

    def lint_directory(self, directory: str, recursive: bool = True) -> LintResult:
        """Lint all template files under a directory."""
        result = LintResult()
        path = Path(directory)

        pattern = "**/*.json" if recursive else "*.json"
        for json_file in path.glob(pattern):
            if json_file.is_file():
                # Skip non-template JSON files.
                if json_file.name in self.NON_TEMPLATE_JSON_FILES:
                    continue
                file_result = self.lint_file(str(json_file))
                result.merge(file_result)

        result.merge(self._lint_application_directories(path, recursive))

        return result

    def _lint_application_directories(self, root: Path, recursive: bool) -> LintResult:
        """Validate every application directory discovered from app.json files."""
        result = LintResult()
        app_json_files: List[Path] = []

        direct_app_json = root / "app.json"
        if direct_app_json.is_file():
            app_json_files.append(direct_app_json)
        elif recursive:
            app_json_files.extend(sorted(p for p in root.glob("**/app.json") if p.is_file()))

        seen_dirs: Set[Path] = set()
        for app_json in app_json_files:
            app_dir = app_json.parent
            if app_dir in seen_dirs:
                continue
            seen_dirs.add(app_dir)
            result.merge(self._lint_application_directory(app_dir))

        return result

    def _lint_application_directory(self, app_dir: Path) -> LintResult:
        """Validate app.json and relationships across all templates in one application."""
        result = LintResult()
        app_json_path = app_dir / "app.json"
        app_scope = f"application: {app_dir}"

        try:
            with open(app_json_path, "r", encoding="utf-8-sig") as f:
                app_data = json.load(f)
        except FileNotFoundError:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_APP_JSON,
                message=f"app.json was not found in application directory: {app_dir}",
                template_id=app_scope,
            ))
            return result
        except json.JSONDecodeError as e:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_APP_JSON,
                message=f"Invalid app.json: {e}",
                template_id=app_scope,
            ))
            return result

        if not isinstance(app_data, dict):
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_APP_JSON,
                message="app.json must be a JSON object",
                template_id=app_scope,
            ))
            return result

        application_id = str(app_data.get("applicationId", "")).strip()
        if not application_id:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_MISSING_APP_FIELD,
                message="app.json is missing required field: applicationId",
                template_id=app_scope,
                parameter_name="applicationId",
            ))

        templates = self._collect_application_templates(app_dir)
        if not templates:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_APP_HAS_NO_TEMPLATES,
                message="Application directory does not contain any template JSON files",
                template_id=app_scope,
            ))
            return result

        result.merge(self._lint_duplicate_template_keys(templates, app_scope))

        main_template_id = str(app_data.get("mainTemplateId", "__main__")).strip() or "__main__"
        main_matches = self._resolve_application_template_reference(
            main_template_id,
            templates,
            application_id,
            allow_namespaced_main=True,
            case_insensitive_alias=True,
        )
        if not main_matches:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_APP_MAIN_TEMPLATE_NOT_FOUND,
                message=f"app.json mainTemplateId '{main_template_id}' does not match any templateId or file alias",
                template_id=app_scope,
                parameter_name="mainTemplateId",
            ))
        elif len(main_matches) > 1:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_APP_MAIN_TEMPLATE_AMBIGUOUS,
                message=(
                    f"app.json mainTemplateId '{main_template_id}' matches multiple templates: "
                    + ", ".join(self._template_label(match["template"]) for match in main_matches)
                ),
                template_id=app_scope,
                parameter_name="mainTemplateId",
            ))
        else:
            match = main_matches[0]
            target = match["template"]
            reasons = match["reasons"]
            if target["templateId"] != main_template_id and not ({"templateId", "namespacedTemplateId"} & reasons):
                result.add_warning(LintError(
                    level=ErrorLevel.WARNING,
                    code=self.WARN_APP_MAIN_TEMPLATE_ALIAS,
                    message=(
                        f"app.json mainTemplateId '{main_template_id}' resolves through file alias "
                        f"'{target['alias']}' to templateId '{target['templateId']}'. "
                        "Prefer making mainTemplateId match the target templateId."
                    ),
                    template_id=app_scope,
                    parameter_name="mainTemplateId",
                ))

        for template in templates:
            result.merge(self._lint_template_execute_relationships(template, templates))

        return result

    def _collect_application_templates(self, app_dir: Path) -> List[Dict[str, Any]]:
        templates: List[Dict[str, Any]] = []
        for json_file in sorted(app_dir.rglob("*.json")):
            if json_file.name in self.NON_TEMPLATE_JSON_FILES:
                continue
            try:
                with open(json_file, "r", encoding="utf-8-sig") as f:
                    raw_text = f.read()
                raw_data = json.loads(raw_text)
                data = TemplateSourcePreprocessor.preprocess(raw_data)
            except (json.JSONDecodeError, OSError, ValueError):
                continue

            if not isinstance(data, dict):
                continue

            template_id = str(data.get("templateId", "")).strip() or json_file.stem
            template_name = str(data.get("templateName", "")).strip()
            templates.append({
                "path": json_file,
                "relativePath": self._relative_to(json_file, app_dir),
                "alias": json_file.stem,
                "templateId": template_id,
                "templateName": template_name,
                "data": data,
                "parameters": self._template_parameter_map(data),
                "sourceText": raw_text,
                "sourceMap": self._build_source_map(raw_text, str(json_file)),
            })

        return templates

    def _lint_duplicate_template_keys(self, templates: List[Dict[str, Any]], app_scope: str) -> LintResult:
        result = LintResult()
        ids: Dict[str, List[Dict[str, Any]]] = {}
        aliases: Dict[str, List[Dict[str, Any]]] = {}

        for template in templates:
            ids.setdefault(template["templateId"], []).append(template)
            aliases.setdefault(template["alias"], []).append(template)

        for template_id, matches in ids.items():
            if len(matches) > 1:
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_DUPLICATE_TEMPLATE_ID,
                    message=(
                        f"Duplicate templateId '{template_id}' in application: "
                        + ", ".join(match["relativePath"] for match in matches)
                    ),
                    template_id=app_scope,
                ))

        for alias, matches in aliases.items():
            distinct_targets = {match["templateId"] for match in matches}
            if len(matches) > 1 and len(distinct_targets) > 1:
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_DUPLICATE_TEMPLATE_ALIAS,
                    message=(
                        f"Duplicate template file alias '{alias}' in application: "
                        + ", ".join(self._template_label(match) for match in matches)
                    ),
                    template_id=app_scope,
                ))

        return result

    def _lint_template_execute_relationships(
        self,
        source_template: Dict[str, Any],
        templates: List[Dict[str, Any]],
    ) -> LintResult:
        result = LintResult()
        previous_source_file = self._current_source_file
        previous_source_text = self._current_source_text
        previous_source_map = self._current_source_map
        self._current_source_file = str(source_template["path"])
        self._current_source_text = source_template.get("sourceText", "")
        self._current_source_map = source_template.get("sourceMap", {})
        try:
            calls = self._iter_template_execute_calls(
                source_template["data"].get("operations", []),
                path=("operations",),
            )
            for call in calls:
                source_fields = self._source_fields(
                    call.get("operationPath"),
                    call.get("parametersPath") or call.get("operationPath"),
                )
                target_id = call.get("targetId")
                if not isinstance(target_id, str) or not target_id.strip():
                    continue

                matches = self._resolve_application_template_reference(
                    target_id.strip(),
                    templates,
                    application_id="",
                    allow_namespaced_main=False,
                    case_insensitive_alias=False,
                )
                if not matches:
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_TEMPLATE_EXECUTE_TARGET_NOT_FOUND,
                        message=(
                            f"{source_template['relativePath']} {call['context']} calls missing templateId "
                            f"'{target_id}'"
                        ),
                        template_id=source_template["templateId"],
                        operation_index=call["operationIndex"],
                        operation_type="template.execute",
                        parameter_name="templateId",
                        **source_fields,
                    ))
                    continue

                if len(matches) > 1:
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_TEMPLATE_EXECUTE_TARGET_AMBIGUOUS,
                        message=(
                            f"{source_template['relativePath']} {call['context']} target '{target_id}' "
                            "matches multiple templates: "
                            + ", ".join(self._template_label(match["template"]) for match in matches)
                        ),
                        template_id=source_template["templateId"],
                        operation_index=call["operationIndex"],
                        operation_type="template.execute",
                        parameter_name="templateId",
                        **source_fields,
                    ))
                    continue

                target = matches[0]["template"]
                passed_params = call.get("parameters") if isinstance(call.get("parameters"), dict) else None
                if passed_params is None:
                    continue

                declared_params = target["parameters"]
                passed_names = set(passed_params.keys())
                declared_names = set(declared_params.keys())
                extra = sorted(passed_names - declared_names)
                if extra:
                    result.add_warning(LintError(
                        level=ErrorLevel.WARNING,
                        code=self.WARN_TEMPLATE_EXECUTE_UNDECLARED_PARAM,
                        message=(
                            f"{source_template['relativePath']} {call['context']} passes undeclared parameter(s) "
                            f"to '{target['templateId']}': {', '.join(extra)}"
                        ),
                        template_id=source_template["templateId"],
                        operation_index=call["operationIndex"],
                        operation_type="template.execute",
                        parameter_name="parameters",
                        **source_fields,
                    ))

                missing_required = sorted(
                    name
                    for name, param in declared_params.items()
                    if param["isInput"] and param["required"] and name not in passed_names
                )
                if missing_required:
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_TEMPLATE_EXECUTE_MISSING_REQUIRED_PARAM,
                        message=(
                            f"{source_template['relativePath']} {call['context']} does not pass required "
                            f"parameter(s) for '{target['templateId']}': {', '.join(missing_required)}"
                        ),
                        template_id=source_template["templateId"],
                        operation_index=call["operationIndex"],
                        operation_type="template.execute",
                        parameter_name="parameters",
                        **source_fields,
                    ))
        finally:
            self._current_source_file = previous_source_file
            self._current_source_text = previous_source_text
            self._current_source_map = previous_source_map

        return result

    def _resolve_application_template_reference(
        self,
        reference: str,
        templates: List[Dict[str, Any]],
        application_id: str,
        allow_namespaced_main: bool,
        case_insensitive_alias: bool,
    ) -> List[Dict[str, Any]]:
        matches: Dict[str, Dict[str, Any]] = {}
        normalized_reference = reference.lower()

        for template in templates:
            reasons: Set[str] = set()
            if template["templateId"] == reference:
                reasons.add("templateId")
            if allow_namespaced_main and application_id and template["templateId"] == f"{application_id}/{reference}":
                reasons.add("namespacedTemplateId")

            alias = template["alias"]
            alias_matches = alias.lower() == normalized_reference if case_insensitive_alias else alias == reference
            if alias_matches:
                reasons.add("fileAlias")

            if reasons:
                key = str(template["path"])
                existing = matches.setdefault(key, {"template": template, "reasons": set()})
                existing["reasons"].update(reasons)

        return list(matches.values())

    def _iter_template_execute_calls(
        self,
        value: Any,
        stack: Optional[List[str]] = None,
        top_level_index: int = -1,
        path: JsonPath = (),
    ):
        stack = stack or ["operations"]
        if isinstance(value, list):
            for index, item in enumerate(value):
                if not isinstance(item, dict):
                    continue
                op_type = item.get("operationType")
                current_top_index = index if top_level_index < 0 else top_level_index
                current_stack = stack + [f"{op_type or '<missing>'}[{index}]"]
                current_path = path + (index,)
                if op_type == "template.execute":
                    params = item.get("parameters") if isinstance(item.get("parameters"), dict) else {}
                    yield {
                        "targetId": params.get("templateId"),
                        "parameters": params.get("parameters"),
                        "operationIndex": current_top_index,
                        "context": " > ".join(current_stack),
                        "operationPath": current_path,
                        "parametersPath": current_path + ("parameters", "parameters"),
                    }

                for key, child in item.items():
                    if isinstance(child, (list, dict)):
                        yield from self._iter_template_execute_calls(
                            child,
                            current_stack,
                            current_top_index,
                            current_path + (key,),
                        )
        elif isinstance(value, dict):
            for key, child in value.items():
                if isinstance(child, (list, dict)):
                    yield from self._iter_template_execute_calls(
                        child,
                        stack + [str(key)],
                        top_level_index,
                        path + (key,),
                    )

    def _template_parameter_map(self, template: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        params: Dict[str, Dict[str, Any]] = {}
        raw_params = template.get("parameters", [])
        if not isinstance(raw_params, list):
            return params

        for raw_param in raw_params:
            if not isinstance(raw_param, dict):
                continue
            name = raw_param.get("name") or raw_param.get("parameterName")
            if not isinstance(name, str) or not name.strip():
                continue
            direction = str(raw_param.get("direction", "INPUT")).upper()
            params[name.strip()] = {
                "required": bool(raw_param.get("required", False)),
                "direction": direction,
                "isInput": direction in ("INPUT", "INOUT"),
                "isOutput": direction in ("OUTPUT", "INOUT"),
            }

        return params

    def _template_label(self, template: Dict[str, Any]) -> str:
        return f"{template['relativePath']} (templateId={template['templateId']})"

    def _relative_to(self, path: Path, root: Path) -> str:
        try:
            return str(path.relative_to(root)).replace("\\", "/")
        except ValueError:
            return str(path)

    def _lint_template(self, template: Dict[str, Any], source: str = "") -> LintResult:
        """Lint one template object."""
        result = LintResult()
        template_id = template.get("templateId", "<unknown>")

        # Required fields.
        if "templateId" not in template:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_MISSING_REQUIRED_FIELD,
                message="Missing required field: templateId",
                template_id=source
            ))

        if "templateName" not in template:
            result.add_warning(LintError(
                level=ErrorLevel.WARNING,
                code=self.ERR_MISSING_REQUIRED_FIELD,
                message="Missing recommended field: templateName",
                template_id=template_id
            ))

        # Initialize variable scope.
        scope = self._init_variable_scope(template)
        operations = template.get("operations", [])

        if not operations:
            result.add_warning(LintError(
                level=ErrorLevel.WARNING,
                code=self.WARN_EMPTY_OPERATIONS,
                message="Template has no operations",
                template_id=template_id
            ))
            return result

        # Lint operations.
        loop_stack: List[str] = []

        for i, op in enumerate(operations):
            op_result = self._lint_operation(
                op, i, template_id, scope, loop_stack, ("operations", i)
            )
            result.merge(op_result)

        return result

    def _init_variable_scope(self, template: Dict[str, Any]) -> VariableScope:
        """Initialize variable scope from template parameters and variables."""
        scope = VariableScope()
        built_in_variables = {
            "timestamp",
            "__trigger_id",
            "__trigger_type",
            "__trigger_name",
            "__trigger_source",
            "__error_occurred",
            "__error_code",
            "__error_message",
            "__error_operation_type",
            "__error_operation_index",
            "__error_step_index",
        }

        for name in built_in_variables:
            scope.define(name, -1)

        # Input parameters are defined before operations run.
        for param in template.get("parameters", []):
            if isinstance(param, dict):
                name = param.get("name")
                if name:
                    scope.define(name, -1)

        # Internal variables.
        for var in template.get("variables", []):
            if isinstance(var, dict):
                name = var.get("name")
                if name:
                    scope.define(name, -1)

        return scope

    def _lint_operation(
        self,
        operation: Dict[str, Any],
        index: int,
        template_id: str,
        scope: VariableScope,
        loop_stack: List[str],
        operation_path: Optional[JsonPath] = None
    ) -> LintResult:
        """Lint one operation."""
        result = LintResult()
        operation_path = operation_path or ("operations", index)

        # Operation type.
        op_type = operation.get("operationType", "")
        if not op_type:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_OPERATION_TYPE,
                message="Operation is missing the operationType field",
                template_id=template_id,
                operation_index=index,
                **self._source_fields(operation_path, operation_path)
            ))
            return result

        # Known operation type.
        resolved_type = self.registry.resolve_alias(op_type)
        if not self.registry.is_known_type(resolved_type):
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_OPERATION_TYPE,
                message=f"Unknown operation type: {op_type}",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type,
                suggestion=f"Known operation types: {', '.join(sorted(self.registry.get_all_types()))}",
                **self._source_fields(operation_path, operation_path + ("operationType",))
            ))
            return result

        # Operation spec.
        spec = self.registry.get_spec(resolved_type)

        # Platform compatibility.
        if spec and "platforms" in spec:
            platforms = [p.lower() for p in spec.get("platforms", [])]
            if (
                self.platform != "all"
                and platforms
                and self.platform not in platforms
                and "core" not in platforms
            ):
                result.add_warning(LintError(
                    level=ErrorLevel.WARNING,
                    code="T105",
                    message=f"Operation type '{op_type}' does not support target platform '{self.platform}'",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type
                ))

        # Parameters.
        params = operation.get("parameters", {})

        if spec:
            # Required parameters.
            for required in spec.get("requiredParams", []):
                if required not in params:
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_MISSING_REQUIRED_PARAM,
                        message=f"Missing required parameter: {required}",
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        parameter_name=required,
                        **self._source_fields(operation_path, operation_path + ("parameters", required))
                    ))

            # oneOfRequired: at least one parameter must be present.
            one_of_required = spec.get("oneOfRequired", [])
            if one_of_required:
                has_one = any(p in params for p in one_of_required)
                if not has_one:
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_ONE_OF_REQUIRED,
                        message=f"At least one of these parameters is required: {', '.join(one_of_required)}",
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        **self._source_fields(operation_path, operation_path + ("parameters",))
                    ))

            all_of_required = spec.get("allOfRequired", [])
            if all_of_required:
                present_all_of = [p for p in all_of_required if p in params]
                if present_all_of and len(present_all_of) != len(all_of_required):
                    missing_all_of = [p for p in all_of_required if p not in params]
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_MISSING_REQUIRED_PARAM,
                        message=(
                            f"Parameter group must appear together; provided: {', '.join(present_all_of)}; "
                            f"missing: {', '.join(missing_all_of)}"
                        ),
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        **self._source_fields(operation_path, operation_path + ("parameters",))
                    ))

            conditional_required = spec.get("conditionalRequired", [])
            for condition in conditional_required:
                if not isinstance(condition, dict):
                    continue
                condition_param = condition.get("conditionParam")
                condition_value = condition.get("conditionValue")
                required_params = condition.get("requiredParams", [])
                if params.get(condition_param) != condition_value:
                    continue
                for required in required_params:
                    if required not in params:
                        result.add_error(LintError(
                            level=ErrorLevel.ERROR,
                            code=self.ERR_MISSING_REQUIRED_PARAM,
                            message=(
                                f"Parameter '{required}' is required when '{condition_param}' is "
                                f"'{condition_value}'"
                            ),
                            template_id=template_id,
                            operation_index=index,
                            operation_type=op_type,
                            parameter_name=required,
                            **self._source_fields(operation_path, operation_path + ("parameters", required))
                        ))

            conditional_one_of_required = spec.get("conditionalOneOfRequired", [])
            for condition in conditional_one_of_required:
                if not isinstance(condition, dict):
                    continue
                condition_param = condition.get("conditionParam")
                condition_value = condition.get("conditionValue")
                required_params = condition.get("requiredParams", [])
                if params.get(condition_param) != condition_value:
                    continue
                has_any = any(required in params for required in required_params)
                if not has_any:
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_ONE_OF_REQUIRED,
                        message=(
                            f"At least one of these parameters is required when '{condition_param}' is "
                            f"'{condition_value}': {', '.join(required_params)}"
                        ),
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        **self._source_fields(operation_path, operation_path + ("parameters",))
                    ))

            # Parameter types and values.
            param_types = spec.get("paramTypes", {})
            param_enums = spec.get("paramEnums", {})
            param_deprecated = spec.get("paramDeprecated", {})
            param_deprecated_messages = spec.get("paramDeprecatedMessages", {})
            param_allow_empty = spec.get("paramAllowEmpty", {})
            allowed_params = set(spec.get("allowedParams", []))
            for param_name, param_value in params.items():
                if spec.get("rejectUnknownParams", True) and param_name not in allowed_params:
                    param_path = operation_path + ("parameters", param_name)
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_UNKNOWN_PARAM,
                        message=f"Parameter '{param_name}' is not defined for OperationType '{op_type}'",
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        parameter_name=param_name,
                        **self._source_fields(operation_path, param_path)
                    ))
                    continue

                if (
                    isinstance(param_value, str)
                    and not self._is_runtime_expression(param_value)
                    and param_value == ""
                    and not param_allow_empty.get(param_name, False)
                ):
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_EMPTY_PARAM_NOT_ALLOWED,
                        message=f"Parameter '{param_name}' does not allow an empty string",
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        parameter_name=param_name,
                        **self._source_fields(operation_path, operation_path + ("parameters", param_name))
                    ))

                expected_type = param_types.get(param_name)
                if expected_type and not self._check_param_type(param_value, expected_type):
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_INVALID_PARAM_TYPE,
                        message=(
                            f"Parameter '{param_name}' has invalid type: expected {expected_type}, "
                            f"got {type(param_value).__name__}"
                        ),
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        parameter_name=param_name,
                        **self._source_fields(operation_path, operation_path + ("parameters", param_name))
                    ))

                if param_deprecated.get(param_name):
                    result.add_warning(LintError(
                        level=ErrorLevel.WARNING,
                        code=self.WARN_DEPRECATED_PARAM,
                        message=f"Parameter '{param_name}' is deprecated",
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        parameter_name=param_name,
                        suggestion=param_deprecated_messages.get(param_name, ""),
                        **self._source_fields(operation_path, operation_path + ("parameters", param_name))
                    ))

                allowed_values = param_enums.get(param_name, [])
                if (
                    allowed_values
                    and not self._is_runtime_expression(param_value)
                    and str(param_value) not in allowed_values
                ):
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_INVALID_ENUM_VALUE,
                        message=(
                            f"Parameter '{param_name}' has invalid enum value: {param_value}; "
                            f"allowed values: {', '.join(allowed_values)}"
                        ),
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        parameter_name=param_name,
                        **self._source_fields(operation_path, operation_path + ("parameters", param_name))
                    ))

            # oneOf: parameters cannot appear together.
            one_of = spec.get("oneOf", [])
            if one_of and len([p for p in one_of if p in params]) > 1:
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code="T007",
                    message=f"These parameters cannot be used together: {', '.join(one_of)}",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type,
                    **self._source_fields(operation_path, operation_path + ("parameters",))
                ))

            # Nested operations.
            nested_ops = spec.get("nestedOperations", [])
            nested_loop_stack = loop_stack + [op_type] if op_type in ["while", "for"] else loop_stack
            for nested_param in nested_ops:
                if nested_param in params:
                    nested_result = self._lint_nested_operations(
                        params[nested_param],
                        template_id,
                        index,
                        op_type,
                        nested_param,
                        scope,
                        nested_loop_stack,
                        operation_path,
                        params
                    )
                    result.merge(nested_result)

            # Loop context.
            if spec.get("requiresLoopContext"):
                if not loop_stack:
                    result.add_error(LintError(
                        level=ErrorLevel.ERROR,
                        code=self.ERR_BREAK_WITHOUT_LOOP if op_type == "break" else self.ERR_CONTINUE_WITHOUT_LOOP,
                        message=f"{op_type} operation must be used inside a loop",
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type
                    ))
        else:
            nested_ops = []

        # Condition/expression syntax.
        for param_name, param_value in params.items():
            if param_name in ["condition", "expression"]:
                if isinstance(param_value, str):
                    expr_result = self._lint_expression(
                        param_value,
                        template_id,
                        index,
                        op_type,
                        param_name,
                        scope
                    )
                    result.merge(expr_result)

        # Variable references.
        params_for_ref_check = self._filter_nested_params(params, nested_ops)
        var_refs = self._extract_variable_references_with_paths(
            params_for_ref_check,
            operation_path + ("parameters",),
        )
        for ref, ref_path, ref_token in var_refs:
            if not scope.is_defined(ref):
                result.add_warning(LintError(
                    level=ErrorLevel.WARNING,
                    code=self.ERR_UNDEFINED_VARIABLE,
                    message=f"Undefined variable reference: ${{{ref}}}",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type,
                    parameter_name=self._parameter_name_from_path(ref_path),
                    **self._source_fields(operation_path, ref_path, ref_token)
                ))

        guards_result = self._lint_guards(
            operation.get("guards"),
            template_id,
            index,
            op_type,
            scope,
            operation_path
        )
        result.merge(guards_result)

        self._track_defined_variables(resolved_type, op_type, params, scope, index)

        return result

    def _lint_guards(
        self,
        guards: Any,
        template_id: str,
        index: int,
        op_type: str,
        scope: VariableScope,
        operation_path: Optional[JsonPath] = None
    ) -> LintResult:
        result = LintResult()
        operation_path = operation_path or ("operations", index)
        if guards is None:
            return result

        if not isinstance(guards, dict):
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_GUARDS,
                message="guards must be an object",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type
            ))
            return result

        allowed_keys = {
            "preconditions",
            "postconditions",
            "recoveryBranch",
            "onPreconditionFail",
            "onPostconditionFail",
            "errorCode",
        }
        for key in guards.keys():
            if key not in allowed_keys:
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_INVALID_GUARDS,
                    message=f"guards contains unknown field: {key}",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type
                ))

        for action_key in ("onPreconditionFail", "onPostconditionFail"):
            action_value = guards.get(action_key)
            if action_value is None:
                continue
            if not isinstance(action_value, str):
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_INVALID_GUARD_ACTION,
                    message=f"{action_key} must be a string",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type,
                    parameter_name=action_key
                ))
                continue
            if action_value != "raiseerror":
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_INVALID_GUARD_ACTION,
                    message=f"{action_key} only supports raiseerror; current value: {action_value}",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type,
                    parameter_name=action_key
                ))

        error_code = guards.get("errorCode")
        if error_code is not None and not isinstance(error_code, str):
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_GUARDS,
                message="guards.errorCode must be a string",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type,
                parameter_name="errorCode"
            ))

        for phase_key in ("preconditions", "postconditions"):
            phase_conditions = guards.get(phase_key)
            if phase_conditions is None:
                continue
            if not isinstance(phase_conditions, list):
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_INVALID_GUARDS,
                    message=f"guards.{phase_key} must be an array",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type,
                    parameter_name=phase_key
                ))
                continue

            for cond_index, condition in enumerate(phase_conditions):
                result.merge(self._lint_guard_condition(
                    condition,
                    phase_key,
                    cond_index,
                    template_id,
                    index,
                    op_type,
                    scope,
                    operation_path + ("guards", phase_key, cond_index)
                ))

        recovery_branch = guards.get("recoveryBranch")
        if recovery_branch is not None:
            nested_result = self._lint_nested_operations(
                recovery_branch,
                template_id,
                index,
                op_type,
                "guards.recoveryBranch",
                scope,
                [],
                operation_path + ("guards",),
            )
            result.merge(nested_result)

        return result

    def _lint_guard_condition(
        self,
        condition: Any,
        phase_key: str,
        cond_index: int,
        template_id: str,
        index: int,
        op_type: str,
        scope: VariableScope,
        condition_path: Optional[JsonPath] = None
    ) -> LintResult:
        result = LintResult()
        condition_path = condition_path or ("operations", index, "guards", phase_key, cond_index)
        if not isinstance(condition, dict):
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_GUARD_CONDITION,
                message=f"guards.{phase_key}[{cond_index}] must be an object",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type
            ))
            return result

        allowed_keys = {"name", "xpath", "exists"}
        for key in condition.keys():
            if key not in allowed_keys:
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_INVALID_GUARD_CONDITION,
                    message=f"guards.{phase_key}[{cond_index}] contains unknown field: {key}",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type
                ))

        xpath = condition.get("xpath")
        if not isinstance(xpath, str) or not xpath.strip():
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_GUARD_CONDITION,
                message=f"guards.{phase_key}[{cond_index}] is missing a valid xpath",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type,
                parameter_name="xpath"
            ))
        else:
            for ref, ref_path, ref_token in self._extract_variable_references_with_paths(
                {"xpath": xpath},
                condition_path,
            ):
                if not scope.is_defined(ref):
                    result.add_warning(LintError(
                        level=ErrorLevel.WARNING,
                        code=self.ERR_UNDEFINED_VARIABLE,
                        message=f"guards.{phase_key}[{cond_index}] references undefined variable: ${{{ref}}}",
                        template_id=template_id,
                        operation_index=index,
                        operation_type=op_type,
                        parameter_name="xpath",
                        **self._source_fields(condition_path[:-3], ref_path, ref_token)
                    ))

        exists = condition.get("exists")
        if exists is None:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_GUARD_CONDITION,
                message=f"guards.{phase_key}[{cond_index}] is missing exists",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type,
                parameter_name="exists"
            ))
        elif not isinstance(exists, bool):
            if not (isinstance(exists, str) and self._is_runtime_expression(exists)):
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_INVALID_GUARD_CONDITION,
                    message=f"guards.{phase_key}[{cond_index}].exists must be a boolean or runtime expression",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type,
                    parameter_name="exists"
                ))

        name = condition.get("name")
        if name is not None and not isinstance(name, str):
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_GUARD_CONDITION,
                message=f"guards.{phase_key}[{cond_index}].name must be a string",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type,
                parameter_name="name"
            ))

        return result

    def _track_defined_variables(
        self,
        resolved_type: str,
        op_type: str,
        params: Dict[str, Any],
        scope: VariableScope,
        index: int
    ) -> None:
        """Track variable definitions from common output parameter conventions."""
        output_param_names = {
            "variableName",
            "targetVariable",
            "output",
            "outputVariable",
            "matchedCountVariable",
            "backCountVariable",
        }

        if op_type == "variable.assign":
            self._define_variable_from_param(params.get("variableName"), scope, index)
            return

        for param_name in output_param_names:
            self._define_variable_from_param(params.get(param_name), scope, index)

        output_variables = params.get("outputVariables")
        if isinstance(output_variables, dict):
            for target_name in output_variables.values():
                self._define_variable_from_param(target_name, scope, index)

        if resolved_type == "android.app.current":
            self._define_variable_from_param(params.get("packageName"), scope, index)

        if resolved_type in {"android.device.info", "win.device.info"}:
            for param_name in [
                "manufacturer",
                "model",
                "platformVersion",
                "apiLevel",
                "deviceName",
                "androidId",
                "computerName",
                "userName",
                "osName",
                "osArch",
            ]:
                self._define_variable_from_param(params.get(param_name), scope, index)

    def _define_variable_from_param(self, value: Any, scope: VariableScope, index: int) -> None:
        if not isinstance(value, str):
            return
        name = value.strip()
        if not name or "${" in name:
            return
        scope.define(name, index)

    def _is_runtime_expression(self, value: Any) -> bool:
        return isinstance(value, str) and bool(re.match(r"^\$\{.+\}$", value.strip()))

    def _filter_nested_params(self, params: Dict[str, Any], nested_param_names: List[str]) -> Dict[str, Any]:
        if not nested_param_names:
            return params
        return {
            key: value
            for key, value in params.items()
            if key not in set(nested_param_names)
        }

    def _lint_nested_operations(
        self,
        nested_data: Any,
        template_id: str,
        parent_index: int,
        parent_type: str,
        nested_param: str,
        scope: VariableScope,
        loop_stack: List[str],
        parent_path: Optional[JsonPath] = None,
        parent_params: Optional[Dict[str, Any]] = None
    ) -> LintResult:
        """Lint nested operations."""
        result = LintResult()
        parent_path = parent_path or ("operations", parent_index)
        nested_base_path = parent_path + ("parameters", nested_param)

        if isinstance(nested_data, dict):
            nested_operations = [(nested_data, nested_base_path)]
        elif isinstance(nested_data, list):
            nested_operations = [
                (item, nested_base_path + (item_index,))
                for item_index, item in enumerate(nested_data)
            ]
        else:
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_NESTED_OPERATION,
                message=f"Nested operation '{nested_param}' must be an object or array",
                template_id=template_id,
                operation_index=parent_index,
                operation_type=parent_type,
                parameter_name=nested_param,
                **self._source_fields(parent_path, nested_base_path)
            ))
            return result

        # Create a nested scope.
        nested_scope = VariableScope(scope)
        if parent_type == "for" and nested_param == "operations" and parent_params:
            self._define_variable_from_param(parent_params.get("variable"), nested_scope, parent_index)
            self._define_variable_from_param(parent_params.get("indexVariable"), nested_scope, parent_index)

        for i, (op, op_path) in enumerate(nested_operations):
            if not isinstance(op, dict):
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_INVALID_NESTED_OPERATION,
                    message=f"Nested operation item {i} must be an object, got {type(op).__name__}",
                    template_id=template_id,
                    operation_index=parent_index,
                    operation_type=parent_type,
                    **self._source_fields(parent_path, op_path)
                ))
                continue

            op_result = self._lint_operation(
                op, i, template_id, nested_scope, loop_stack, op_path
            )
            result.merge(op_result)

        return result

    def _check_param_type(self, value: Any, expected_type: Any) -> bool:
        """Check whether a parameter value matches the expected type."""
        if self._is_runtime_expression(value):
            return True

        if isinstance(expected_type, str) and expected_type.lower() == "any":
            return True

        if isinstance(expected_type, list):
            # Allow any one of several types.
            return any(self._check_single_param_type(value, t) for t in expected_type)

        return self._check_single_param_type(value, expected_type)

    def _check_single_param_type(self, value: Any, expected_type: str) -> bool:
        """Check one expected type."""
        normalized = expected_type.lower()
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "double": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "map": dict,
            "enum": str,
            "any": object,
        }

        if normalized == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if normalized in ("number", "double"):
            return isinstance(value, (int, float)) and not isinstance(value, bool)

        expected_python_type = type_map.get(normalized)
        if expected_python_type:
            return isinstance(value, expected_python_type)

        return True  # Unknown types are treated as valid.

    def _extract_variable_references(self, params: Dict[str, Any]) -> Set[str]:
        """Extract variable references from parameters."""
        return {
            ref
            for ref, _, _ in self._extract_variable_references_with_paths(params)
        }

    def _extract_variable_references_with_paths(
        self,
        value: Any,
        base_path: JsonPath = (),
    ) -> List[Tuple[str, JsonPath, str]]:
        """Extract variable references with the JSON path of the containing value."""
        refs: List[Tuple[str, JsonPath, str]] = []
        var_pattern = re.compile(r'\$\{([^}]+)\}')

        def extract_from_value(current_value: Any, current_path: JsonPath) -> None:
            if isinstance(current_value, str):
                for match in var_pattern.finditer(current_value):
                    expression = match.group(1)
                    token = match.group(0)
                    for ref in self._extract_variable_names_from_expression(expression):
                        refs.append((ref, current_path, token))
            elif isinstance(current_value, dict):
                for key, child in current_value.items():
                    extract_from_value(child, current_path + (key,))
            elif isinstance(current_value, list):
                for item_index, item in enumerate(current_value):
                    extract_from_value(item, current_path + (item_index,))

        extract_from_value(value, base_path)
        return refs

    def _parameter_name_from_path(self, path: JsonPath) -> str:
        for part in reversed(path):
            if isinstance(part, str):
                return part
        return ""

    def _extract_variable_names_from_expression(self, expression: str) -> Set[str]:
        refs: Set[str] = set()
        expr = re.sub(r"'[^']*'|\"[^\"]*\"", " ", expression).strip()
        if not expr:
            return refs

        token_pattern = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
        ignored_names = {
            "and",
            "or",
            "not",
            "true",
            "false",
            "null",
            "nil",
        }

        for match in token_pattern.finditer(expr):
            token = match.group(0)
            if token in ignored_names:
                continue

            if match.start() > 0 and expr[match.start() - 1] == ".":
                continue

            next_pos = match.end()
            if re.match(r"\.[A-Za-z_][A-Za-z0-9_]*\(", expr[next_pos:]):
                continue
            if next_pos < len(expr) and expr[next_pos] == "(":
                continue

            refs.add(token)

        return refs

    def _lint_expression(
        self,
        expression: str,
        template_id: str,
        index: int,
        op_type: str,
        param_name: str,
        scope: VariableScope
    ) -> LintResult:
        """Lint expression syntax."""
        result = LintResult()

        # Basic syntax errors.
        if not expression or not expression.strip():
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_CONDITION_EXPR,
                message=f"{param_name} expression cannot be empty",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type,
                parameter_name=param_name
            ))
            return result

        # Parentheses matching.
        if expression.count('(') != expression.count(')'):
            result.add_error(LintError(
                level=ErrorLevel.ERROR,
                code=self.ERR_INVALID_CONDITION_EXPR,
                message=f"{param_name} expression has mismatched parentheses",
                template_id=template_id,
                operation_index=index,
                operation_type=op_type,
                parameter_name=param_name
            ))

        # Operator checks after replacing variable references to avoid false positives.
        clean_expr = re.sub(r'\$\{[^}]+\}', '""', expression)
        invalid_patterns = [
            (r'===+', "use '==' instead of '==='"),
            (r'!==+', "use '!=' instead of '!=='"),
            # Single & except &&.
            (r'(?<!&)&(?!&)', "use '&&' instead of a single '&'"),
            # Single | except ||.
            (r'(?<!\|)\|(?!\|)', "use '||' instead of a single '|'"),
        ]

        for pattern, msg in invalid_patterns:
            if re.search(pattern, clean_expr):
                result.add_error(LintError(
                    level=ErrorLevel.ERROR,
                    code=self.ERR_INVALID_CONDITION_EXPR,
                    message=f"{param_name} expression syntax error: {msg}",
                    template_id=template_id,
                    operation_index=index,
                    operation_type=op_type,
                    parameter_name=param_name
                ))

        return result


def print_result(result: LintResult, file_path: str = "") -> None:
    """Print lint results."""
    if file_path:
        print(f"\nLint target: {file_path}")
        print("=" * 60)

    # Errors.
    if result.errors:
        print(f"\nFound {result.total_errors} error(s):")
        for error in result.errors:
            print(f"  {error}")
    else:
        print("\nNo errors found")

    # Warnings.
    if result.warnings:
        print(f"\nFound {result.total_warnings} warning(s):")
        for warning in result.warnings:
            print(f"  {warning}")

    # Infos.
    if result.infos:
        print(f"\nInfo:")
        for info in result.infos:
            print(f"  {info}")

    print()


def main():
    """Command-line entry point."""
    import argparse

    # Windows encoding fix.
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="AIVane Template Linter - static validation for template files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s template.json              # Lint one template file
  %(prog)s templates/                 # Lint templates in a directory
  %(prog)s templates/ -r              # Lint templates recursively
  %(prog)s template.json --platform android  # Lint for the Android platform
  %(prog)s template.json --json       # Output JSON
  %(prog)s template.json --strict     # Treat warnings as errors

Error codes:
  T001  Invalid JSON
  T002  Missing required field
  T003  Invalid operation type
  T004  Missing required parameter
  T005  Invalid parameter type
  T006  Missing oneOf-required parameter
  T007  Undefined variable reference
  T008  Invalid condition/expression syntax
  T009  break outside loop
  T010  continue outside loop
  T011  Invalid nested operation
  T012  Unknown parameter
  T013  Invalid enum value
  T101  Template has no operations
  T103  Unused variable
  T104  Deprecated parameter
        """
    )

    parser.add_argument(
        "path",
        help="Template file or directory path"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively lint subdirectories"
    )
    parser.add_argument(
        "--platform",
        choices=["all", "android", "windows", "core"],
        default="all",
        help="Target platform (default: all)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--docs-dir",
        help="OperationType Markdown docs directory (default: bundled OperationTypes)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Create linter.
    linter = TemplateLinter(docs_dir=args.docs_dir, platform=args.platform)

    # Run lint.
    path = Path(args.path)
    if path.is_file():
        result = linter.lint_file(str(path))
    elif path.is_dir():
        result = linter.lint_directory(str(path), recursive=args.recursive)
    else:
        print(f"Error: path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)

    # Output results.
    if args.json:
        output = {
            "errors": [
                {
                    "level": e.level.value,
                    "code": e.code,
                    "message": e.message,
                    "template_id": e.template_id,
                    "operation_index": e.operation_index,
                    "operation_type": e.operation_type,
                    "parameter_name": e.parameter_name,
                    "suggestion": e.suggestion,
                    "source_file": e.source_file,
                    "line": e.line,
                    "column": e.column,
                    "operation_path": e.operation_path,
                    "json_path": e.json_path
                }
                for e in result.errors
            ],
            "warnings": [
                {
                    "level": w.level.value,
                    "code": w.code,
                    "message": w.message,
                    "template_id": w.template_id,
                    "operation_index": w.operation_index,
                    "operation_type": w.operation_type,
                    "parameter_name": w.parameter_name,
                    "suggestion": w.suggestion,
                    "source_file": w.source_file,
                    "line": w.line,
                    "column": w.column,
                    "operation_path": w.operation_path,
                    "json_path": w.json_path
                }
                for w in result.warnings
            ],
            "summary": {
                "total_errors": result.total_errors,
                "total_warnings": result.total_warnings,
                "has_errors": result.has_errors
            }
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        if result.has_errors or (args.strict and result.total_warnings > 0):
            sys.exit(1)
        sys.exit(0)
    else:
        print_result(result, str(path))

        # Print summary.
        total_issues = result.total_errors + result.total_warnings
        if args.strict:
            total_issues = result.total_errors + result.total_warnings

        if total_issues == 0:
            print("PASS: no issues found")
            sys.exit(0)
        elif result.has_errors or (args.strict and result.total_warnings > 0):
            print(f"FAIL: {result.total_errors} error(s), {result.total_warnings} warning(s)")
            sys.exit(1)
        else:
            print(f"PASS with {result.total_warnings} warning(s)")
            sys.exit(0)


if __name__ == "__main__":
    main()

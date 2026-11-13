"""Validate docs/req/requirements.yaml against its schema and cross-reference rules.

JSON Schema cannot check uniqueness of IDs or that references resolve, so this
script adds those checks on top of docs/req/req-schema.json. Used by the CI
schema gate and runnable locally with `uv run python scripts/validate_requirements.py`.
"""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import validators

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_PATH = ROOT / "docs/req/requirements.yaml"
SCHEMA_PATH = ROOT / "docs/req/req-schema.json"


def schema_errors(requirements: dict, schema: dict) -> list[str]:
    """Return schema violations, including date formats."""
    validator_class = validators.validator_for(schema)
    validator_class.check_schema(schema)
    validator = validator_class(schema, format_checker=validator_class.FORMAT_CHECKER)
    return [
        f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(
            validator.iter_errors(requirements),
            key=lambda e: list(map(str, e.absolute_path)),
        )
    ]


def duplicates(values: list[str]) -> list[str]:
    """Return the values that occur more than once, in first-seen order."""
    seen: set[str] = set()
    repeated: list[str] = []
    for value in values:
        if value in seen and value not in repeated:
            repeated.append(value)
        seen.add(value)
    return repeated


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    """Return one dependency cycle as a list of IDs, or None if the graph is acyclic."""
    visiting: list[str] = []
    done: set[str] = set()

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            return visiting[visiting.index(node) :] + [node]
        if node in done:
            return None
        visiting.append(node)
        for dependency in graph.get(node, []):
            if cycle := visit(dependency):
                return cycle
        visiting.pop()
        done.add(node)
        return None

    for node in graph:
        if cycle := visit(node):
            return cycle
    return None


def reference_errors(requirements: list[dict]) -> list[str]:
    """Return ID uniqueness and dependency errors that the schema cannot express."""
    errors = []
    ids = [req["id"] for req in requirements]
    errors += [f"duplicate requirement id {rid}" for rid in duplicates(ids)]

    for req in requirements:
        criterion = req["fit_criterion"]
        for key in ("checks", "metrics"):
            item_ids = [item["id"] for item in criterion.get(key, [])]
            errors += [
                f"{req['id']}: duplicate {key[:-1]} id {item_id}"
                for item_id in duplicates(item_ids)
            ]
        for dependency in req.get("depends_on", []):
            if dependency == req["id"]:
                errors.append(f"{req['id']}: depends on itself")
            elif dependency not in ids:
                errors.append(
                    f"{req['id']}: depends on unknown requirement {dependency}"
                )

    graph = {req["id"]: req.get("depends_on", []) for req in requirements}
    if cycle := find_cycle(graph):
        errors.append(f"dependency cycle: {' -> '.join(cycle)}")
    return errors


def main() -> int:
    """Validate the requirements file and report every error found."""
    for path in (REQUIREMENTS_PATH, SCHEMA_PATH):
        if not path.is_file():
            sys.stdout.write(f"FAIL: required file missing: {path.relative_to(ROOT)}\n")
            return 1

    requirements = yaml.safe_load(REQUIREMENTS_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    errors = schema_errors(requirements, schema)
    if not errors:
        errors = reference_errors(requirements["requirements"])

    for error in errors:
        sys.stdout.write(f"FAIL: {error}\n")
    if errors:
        return 1
    sys.stdout.write(f"PASS: {len(requirements['requirements'])} requirements valid\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

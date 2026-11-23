"""Load the versioned runtime research prompt catalog as package data."""

from importlib.resources import files

import yaml

_RESOURCE_PACKAGE = "open_deep_research_prompt_data"
_RESOURCE_NAME = "prompt_v1.0.yaml"


def _load_templates() -> dict:
    try:
        resource = files(_RESOURCE_PACKAGE).joinpath(_RESOURCE_NAME)
        catalog = yaml.safe_load(resource.read_text(encoding="utf-8"))
    except (ModuleNotFoundError, OSError, UnicodeError, yaml.YAMLError) as exc:
        raise RuntimeError(
            f"Cannot load runtime prompts from {_RESOURCE_NAME}: {exc}"
        ) from exc

    if not isinstance(catalog, dict) or catalog.get("version") != "1.0":
        raise ValueError(f"{_RESOURCE_NAME} must declare version '1.0'")
    templates = catalog.get("templates")
    if not isinstance(templates, dict):
        raise ValueError(f"{_RESOURCE_NAME} must contain a templates mapping")
    for name, value in templates.items():
        if not isinstance(name, str) or not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{_RESOURCE_NAME}: template {name!r} must be named and non-empty text"
            )
    return templates


_TEMPLATES = _load_templates()


def get_template(name: str) -> str:
    """Return a required runtime prompt by name from the loaded YAML catalog."""
    try:
        return _TEMPLATES[name]
    except KeyError as exc:
        raise ValueError(f"{_RESOURCE_NAME}: missing template {name!r}") from exc

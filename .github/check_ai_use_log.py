"""Check an explicit PR AI-use declaration against the AI-use log."""

import json
import os
import re
import subprocess
from pathlib import Path

import yaml

LOG_PATH = "docs/ai-use-log.yaml"
ENTRY_ID = re.compile(r"AIU-[0-9]{3}")
REQUIRED_TEXT = ("date", "member", "purpose", "prompt", "supervision")


def declaration(body: str, field: str) -> str | None:
    """Read one declaration line, rejecting ambiguous duplicates."""
    values = re.findall(rf"^[ \t]*{field}:[ \t]*([^\r\n]*)", body, re.I | re.M)
    if len(values) > 1:
        raise ValueError(f"Use only one '{field}:' line in the PR description.")
    return values[0].strip() if values else None


def is_text(value: object) -> bool:
    """Return whether a value is non-blank text."""
    return isinstance(value, str) and bool(value.strip())


def log_ids(text: str, revision: str) -> set[str]:
    """Validate the documented log fields and return the unique entry IDs."""
    try:
        log = yaml.safe_load(text)
    except yaml.YAMLError:
        raise ValueError(f"{revision} {LOG_PATH} is not valid YAML.") from None
    if not isinstance(log, dict) or not isinstance(log.get("entries"), list):
        raise ValueError(f"{revision} {LOG_PATH} must contain an 'entries' list.")

    ids: set[str] = set()
    for index, entry in enumerate(log["entries"], start=1):
        location = f"{revision} {LOG_PATH}, entry {index}"
        if not isinstance(entry, dict):
            raise ValueError(f"{location}: expected a mapping.")
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not ENTRY_ID.fullmatch(entry_id):
            raise ValueError(f"{location}: expected an ID like AIU-028.")
        if entry_id in ids:
            raise ValueError(f"{location}: duplicate ID {entry_id}.")
        ids.add(entry_id)
        for key in REQUIRED_TEXT:
            if not is_text(entry.get(key)):
                raise ValueError(f"{location}: '{key}' must be non-blank text.")
        for key in ("requirements", "artifacts"):
            values = entry.get(key)
            if not isinstance(values, list) or not all(
                is_text(item) for item in values
            ):
                raise ValueError(f"{location}: '{key}' must be a list of text values.")
            if key == "artifacts" and not values:
                raise ValueError(f"{location}: name at least one artifact.")
        if "transcript" not in entry or (
            entry["transcript"] is not None and not is_text(entry["transcript"])
        ):
            raise ValueError(f"{location}: 'transcript' must be text or null.")
    return ids


def check_pr(body: str, current_ids: set[str], base_ids: set[str]) -> None:
    """Require declared AI use to reference entries added by the PR."""
    use = (declaration(body, "AI use") or "").lower()
    if use not in {"yes", "no"}:
        raise ValueError("Add 'AI use: yes' or 'AI use: no' to the PR description.")
    entry_line = declaration(body, "AI-use log")
    if use == "no":
        if entry_line:
            raise ValueError(
                "Remove the AI-use log declaration or change 'AI use' to 'yes'."
            )
        return
    ids = [value.strip() for value in (entry_line or "").split(",")]
    if not all(ENTRY_ID.fullmatch(value) for value in ids):
        raise ValueError(
            f"Add a new entry to {LOG_PATH} and list its ID in the PR, e.g. 'AI-use log: AIU-028'."
        )
    if missing := set(ids) - (current_ids - base_ids):
        raise ValueError(
            f"Add new entries to {LOG_PATH} for these PR declarations: {', '.join(sorted(missing))}. "
            "Editing or citing an existing entry does not count."
        )


def main() -> int:
    """Read the GitHub event and annotate a failed check."""
    try:
        event = json.loads(
            Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8")
        )
        pr = event["pull_request"]
        current_ids = log_ids(Path(LOG_PATH).read_text(encoding="utf-8"), "PR")
        if pr.get("user", {}).get("login") == "dependabot[bot]":
            return 0
        # The default pull_request checkout is GitHub's test merge commit.
        base_log = subprocess.check_output(
            ["git", "show", f"HEAD^1:{LOG_PATH}"], text=True, encoding="utf-8"
        )
        check_pr(pr.get("body") or "", current_ids, log_ids(base_log, "Base"))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        message = str(exc).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::error title=AI-use log::{message}")  # noqa: T201
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

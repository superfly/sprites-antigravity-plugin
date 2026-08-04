#!/usr/bin/env python3
"""Antigravity hook helpers for the Sprites Plugin.

The hook contract is JSON on stdin and JSON on stdout. A pre-tool hook returns
a `decision` of "allow", "ask", or "deny" (Antigravity fails open when the
decision is missing or unknown, so the key name matters). Keep this script
dependency-free so the Sprites Plugin works immediately after installation.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

# Destructive or irreversible Sprite operations. Matched against the serialized
# tool call, so these fire whether the MCP tool name is bare (`destroy_sprite`)
# or server-prefixed (`sprites__destroy_sprite`).
DESTRUCTIVE_PATTERNS = [
    r"destroy[_-]?sprite",
    r"delete[_-]?sprite",
    r"checkpoint[_-]?restore",
    r"restore[_-]?(sprite|checkpoint)",
    r"delete[_-]?checkpoint",
    r"policy[_-]?network[_-]?(update|set)",
    r"update[_-]?network[_-]?policy",
    r"privilege[_-]?policy",
    r"resource[_-]?policy",
]

# Widening exposure is only worth confirming when it is actually being enabled.
# Requiring a truthy value avoids nagging when a service is created private
# (e.g. `public_url: false`).
EXPOSURE_PATTERNS = [
    r"make[_-]?public",
    r'"?(is[_-]?)?public(_?url)?"?\s*[:=]\s*"?true',
    r'"?expose[_-]?(service|port|url)"?\s*[:=]\s*"?true',
]

CHECKPOINT_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bdrop\s+database\b",
    r"\btruncate\s+table\b",
    r"\bdelete\s+from\b",
    r"\b(db:)?migrate\b",
    r"\bprisma\s+migrate\b",
    r"\balembic\s+upgrade\b",
    r"\brails\s+db:migrate\b",
    r"\bnpm\s+(install|update|audit\s+fix)\b",
    r"\bpnpm\s+(install|update|add|up)\b",
    r"\byarn\s+(install|upgrade|add)\b",
    r"\bpip\s+install\b",
    r"\buv\s+(pip\s+)?install\b",
    r"\bapt(-get)?\s+(install|upgrade|dist-upgrade)\b",
    r"\bdnf\s+(install|upgrade)\b",
    r"\bapk\s+add\b",
]

TEST_PATTERNS = [
    r"\bnpm\s+(run\s+)?test\b",
    r"\bpnpm\s+(run\s+)?test\b",
    r"\byarn\s+(run\s+)?test\b",
    r"\bpytest\b",
    r"\bpython\s+-m\s+pytest\b",
    r"\bgo\s+test\b",
    r"\bcargo\s+test\b",
    r"\bmix\s+test\b",
    r"\bbundle\s+exec\s+rspec\b",
    r"\brspec\b",
]


def read_payload() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def tool_name(payload: dict[str, Any]) -> str:
    return str((payload.get("toolCall") or {}).get("name", "")).lower()


def searchable_text(payload: dict[str, Any]) -> str:
    tool_call = payload.get("toolCall") or {}
    return json.dumps(
        {
            "name": tool_call.get("name", ""),
            "args": tool_call.get("args", {}),
        },
        sort_keys=True,
    ).lower()


def command_line(payload: dict[str, Any]) -> str:
    args = (payload.get("toolCall") or {}).get("args") or {}
    for key in ("CommandLine", "commandLine", "command", "cmd"):
        value = args.get(key)
        if isinstance(value, str):
            return value.lower()
    return searchable_text(payload)


def matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def is_sprite_exec(payload: dict[str, Any]) -> bool:
    # The Sprites MCP command-runner is exposed as `exec` (bare or prefixed).
    # Local shells (`run_command`) and read-only exec helpers (`exec_list`,
    # `exec_kill`) must not trigger the checkpoint nudge.
    return bool(re.search(r"exec$", tool_name(payload)))


def respond(obj: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj))


def allow() -> None:
    respond({"decision": "allow"})


def ask(reason: str) -> None:
    respond({"decision": "ask", "reason": reason})


def safety(payload: dict[str, Any]) -> None:
    text = searchable_text(payload)
    if matches_any(text, DESTRUCTIVE_PATTERNS):
        ask(
            "This Sprites action may destroy state, restore over newer work, or "
            "change network/access policy. Confirm the exact Sprite, scope, and "
            "rollback plan before continuing."
        )
        return
    if matches_any(text, EXPOSURE_PATTERNS):
        ask(
            "This looks like it widens Sprite exposure (public URL or network "
            "policy). Confirm the intended audience and auth before continuing."
        )
        return
    allow()


def checkpoint(payload: dict[str, Any]) -> None:
    if is_sprite_exec(payload) and matches_any(command_line(payload), CHECKPOINT_PATTERNS):
        ask(
            "This looks like a high-risk change inside a Sprite. Create or "
            "verify a recent checkpoint before proceeding."
        )
        return
    allow()


def remote_test(payload: dict[str, Any]) -> None:
    if matches_any(command_line(payload), TEST_PATTERNS):
        ask(
            "Remote Sprite test routing is enabled. Prefer running this test "
            "inside the selected Sprite with the Sprites MCP exec tool unless "
            "the user explicitly wants a local run."
        )
        return
    allow()


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "safety"
    payload = read_payload()

    if mode == "safety":
        safety(payload)
    elif mode == "checkpoint":
        checkpoint(payload)
    elif mode == "remote-test":
        remote_test(payload)
    else:
        allow()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

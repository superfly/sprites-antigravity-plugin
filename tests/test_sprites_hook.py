from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts/sprites_hook.py"


def run_hook(mode: str, payload: dict | None = None, raw_input: str | None = None) -> dict:
    if raw_input is None:
        raw_input = json.dumps(payload or {})
    result = subprocess.run(
        [sys.executable, str(HOOK), mode],
        input=raw_input,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def tool_call(tool_name: str, **args: object) -> dict:
    return {"toolCall": {"name": tool_name, "args": args}}


class SpritesHookTests(unittest.TestCase):
    def test_safety_asks_before_destroy(self) -> None:
        response = run_hook("safety", tool_call("sprites__destroy_sprite", name="mcp-test"))
        self.assertEqual(response["decision"], "ask")

    def test_safety_allows_private_service(self) -> None:
        response = run_hook(
            "safety",
            tool_call("sprites__service_create", public_url=False, name="web"),
        )
        self.assertEqual(response["decision"], "allow")

    def test_checkpoint_asks_before_high_risk_exec(self) -> None:
        response = run_hook("checkpoint", tool_call("sprites__exec", command="npm install"))
        self.assertEqual(response["decision"], "ask")

    def test_checkpoint_ignores_read_only_exec_helpers(self) -> None:
        response = run_hook("checkpoint", tool_call("sprites__exec_list", command="npm install"))
        self.assertEqual(response["decision"], "allow")

    def test_remote_test_detects_test_command(self) -> None:
        response = run_hook("remote-test", tool_call("run_command", command="python -m pytest"))
        self.assertEqual(response["decision"], "ask")

    def test_invalid_json_fails_open(self) -> None:
        response = run_hook("safety", raw_input="not-json")
        self.assertEqual(response["decision"], "allow")


if __name__ == "__main__":
    unittest.main()

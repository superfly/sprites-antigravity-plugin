from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class AntigravityPluginRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_json(ROOT / "plugin.json")
        self.hooks = load_json(ROOT / "hooks.json")

    def test_manifest_repository_matches_this_repository(self) -> None:
        self.assertEqual(
            self.manifest["repository"],
            "https://github.com/superfly/sprites-antigravity-plugin",
        )

    def test_mcp_server_uses_https(self) -> None:
        config = load_json(ROOT / "mcp_config.json")
        server = config["mcpServers"]["sprites"]
        parsed = urlparse(server["serverUrl"])
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "sprites.dev")
        self.assertEqual(parsed.path, "/mcp")

    def test_commands_have_matching_skills(self) -> None:
        command_names = {path.stem for path in (ROOT / "commands/sprites").glob("*.toml")}
        skill_names = {
            path.parent.name.removeprefix("sprites-")
            for path in (ROOT / "skills").glob("sprites-*/SKILL.md")
        }
        self.assertEqual(command_names, skill_names)

    def test_hooks_reference_existing_script_and_valid_modes(self) -> None:
        valid_modes = {"safety", "checkpoint", "remote-test"}
        for group in self.hooks.values():
            for event_name, entries in group.items():
                if event_name == "enabled":
                    continue
                for entry in entries:
                    re.compile(entry["matcher"])
                    for hook in entry["hooks"]:
                        command = hook["command"]
                        script_path, mode = command.split()[-2:]
                        self.assertTrue(script_path.endswith("scripts/sprites_hook.py"))
                        self.assertTrue((ROOT / "scripts/sprites_hook.py").is_file())
                        self.assertIn(mode, valid_modes)


if __name__ == "__main__":
    unittest.main()

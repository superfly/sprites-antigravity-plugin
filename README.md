# Sprites Plugin

Use Sprites from Antigravity CLI (`agy`) as persistent, isolated Linux development environments for building, testing, previewing, and debugging code. Sprites keep state between sessions, so Antigravity can work in a real project environment without crowding your laptop with packages, services, databases, or long-running processes.

The Sprites Plugin gives Antigravity reusable Sprites workflows, safety guardrails, and convenient commands for common development tasks.

## Usage attribution

The plugin adds two fixed [`client-signals`](https://github.com/superfly/client-signals)
headers to its hosted MCP requests so the traffic can be identified as
Antigravity plugin traffic:

- `Fly-Client-Agent: antigravity`
- `Fly-Client-Interactive: false`

Both are constants in the plugin config. They carry nothing about you, your
machine, or your repository. Fly uses them for aggregate traffic reporting only,
not for authentication, authorization, gating, or rate-limiting. See
[docs/attribution.md](docs/attribution.md) for what the values mean and what
they cannot measure.

## What You Can Do

- Create fresh, named Sprites for risky changes, experiments, or preview environments.
- Run commands and tests inside a Sprite instead of your local machine.
- Manage long-running services such as web servers, workers, and daemons.
- Create checkpoints before migrations, package upgrades, and other high-risk work.
- Inspect running Sprites, services, checkpoints, and likely stale environments.
- Clean up old Sprites safely with confirmation before destructive actions.

## Commands

- `/sprites:list`: See active Sprites, status, services, exposure, and stale candidates.
- `/sprites:new <purpose>`: Create a fresh Sprite for a task.
- `/sprites:run <command>`: Run a shell command inside a selected Sprite.
- `/sprites:checkpoint <reason>`: Create, list, inspect, or restore checkpoints.
- `/sprites:service <command>`: Start, restart, expose, inspect, or debug services.
- `/sprites:cleanup`: Find and safely remove idle Sprites and checkpoints.

## Install

Install from the repository:

```sh
agy plugin install https://github.com/superfly/sprites-antigravity-plugin
```

Then open Antigravity's MCP manager with `/mcp` and authenticate the `sprites` server. Use restricted access unless your workflow needs broader organization control.

## Safety

Sprites are stateful environments, so the Sprites Plugin nudges Antigravity to be careful around actions that can affect durable state. It asks for confirmation before destructive operations such as destroying Sprites, restoring checkpoints, deleting checkpoints, or widening service/network exposure. It also prompts for checkpoints before risky commands like migrations, package upgrades, and broad filesystem changes.

## Optional Hooks

One hook is disabled by default:

- `sprites-remote-test-routing`

Enable it for workspaces that want test commands routed into a Sprite instead of running locally.

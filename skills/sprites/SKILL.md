---
name: sprites
description: Use when working with Sprites from Antigravity, including creating persistent microVMs, running commands, managing services, using checkpoints, syncing files, or applying Sprites safety practices.
---

# Sprites

Use the hosted Fly MCP server (`https://mcp.fly.io`) configured as `sprites`. It can also expose non-Sprites Fly tools when the user granted them; stay with the Sprites tools unless the user asks for those explicitly. Do not build, scaffold, or run a local MCP server for Sprites.

## Core Principles

- Sprites are persistent, isolated Linux microVMs. Treat them as durable environments, not disposable one-shot shells.
- Use a restricted Sprites grant and a clear prefix such as `mcp-` unless the user explicitly needs broader organization access.
- Prefer fresh Sprites for experiments and risky generated code.
- Create or verify a recent checkpoint before package upgrades, migrations, bulk filesystem edits, service rewrites, network policy changes, or destructive cleanup.
- Ask before destroying Sprites, restoring checkpoints, widening network/resource/privilege policies, or making a service public.
- Use exact names and IDs from `list_sprites`, checkpoint lists, service lists, or exec-session lists. Do not guess resource identifiers.

## Common Workflow

1. Discover the current state with read-only tools first: list Sprites, inspect the selected Sprite, list services, list checkpoints, or read logs.
2. Select or create a Sprite with an `mcp-` style name when using restricted access.
3. For changes that may persist or break state, create a checkpoint with a clear reason.
4. Run commands through the Sprites MCP exec tools and summarize command, working directory, exit status, and important output.
5. For background processes, use Sprites services rather than leaving a foreground exec session running.
6. Verify the result with tests, service logs, health checks, or file reads.
7. End with the Sprite name, checkpoint/service identifiers, exposed URLs, and any cleanup the user should know about.

## References

- Read `references/safety.md` before destructive, public exposure, network policy, or checkpoint-restore workflows.
- Read `references/services.md` before creating or modifying long-running services.
- Read `references/deployment.md` before deployment or sync-oriented work.

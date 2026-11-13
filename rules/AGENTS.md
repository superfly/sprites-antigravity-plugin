# Sprites Rules

These rules apply when using Sprites from Antigravity.

- Prefer the hosted Fly MCP server (`https://mcp.fly.io`) configured as `sprites`; do not build or invoke a local Sprites MCP bridge.
- The `sprites` server can also expose non-Sprites Fly tools (apps, Machines, volumes, secrets, Managed Postgres) when the user granted them. Stay with the Sprites tools unless the user asks for those explicitly.
- Treat Sprites as persistent, stateful Linux microVMs. Changes to files, packages, databases, checkpoints, services, and network policy can outlive the current Antigravity session.
- Prefer restricted OAuth access and a clear name prefix such as `mcp-` for agent-created Sprites.
- Before destructive work, identify the Sprite by exact name and create or verify a recent checkpoint.
- Ask before destroying a Sprite, restoring a checkpoint, deleting checkpoints, widening network access, changing privilege/resource policies, or making services public.
- Use environment variables for configuration and secrets. Do not hard-code credentials or copy tokens into prompts, files, shell history, or service definitions.
- Keep SQLite and other filesystem-backed state in durable paths that are intentionally part of the Sprite environment.
- For long-running processes, prefer Sprites services over ad hoc foreground shells. Capture service names, ports, logs, and URL/auth settings in the task summary.
- When debugging, inspect service status and logs before restarting or changing code.
- For local-to-Sprite sync workflows, sync selected paths only. Avoid overwriting broad directories unless the user explicitly approves the path and direction.

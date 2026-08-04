# Client attribution

The hosted MCP entry in [`mcp_config.json`](../mcp_config.json) sends two fixed
[`client-signals`](https://github.com/superfly/client-signals) headers:

```json
"headers": {
  "Fly-Client-Interactive": "false",
  "Fly-Client-Agent": "antigravity"
}
```

Together they classify as `{operator: "agent", agent: "antigravity"}` under the
[server-side request-metric contract](https://github.com/superfly/client-signals/blob/main/spec/request-metrics.md).
See [docs/signals.md](https://github.com/superfly/client-signals/blob/main/docs/signals.md)
upstream for what each signal is worth.

## Why `Fly-Client-Interactive` is sent

`Fly-Client-Interactive` is the instrumentation sentinel. If it is missing or is
not a recognized boolean, the request classifies as `uninstrumented` and the
agent marker is discarded, so it has to be present for `Fly-Client-Agent` to
count for anything.

Its value here is a constant and does **not** reflect a real terminal check.
Upstream the field means "this process's stdout looks attached to a terminal,"
which a static config file cannot determine. Because operator precedence is
`ci > agent > interactive`, the agent marker wins and this value does not affect
classification while `Fly-Client-Agent` is present and valid. Do not read it as
a measurement.

## What this cannot measure

- **CI traffic counts as agent traffic.** Upstream expects `Fly-Client-CI` so CI
  runs can be subtracted out before the remaining automated traffic is
  attributed to agents. A static config cannot detect `CI`/`GITHUB_ACTIONS`, so
  `agy` runs inside CI land in the `agent` bucket and inflate it.
- **The agent name is unguarded.** `antigravity` has to match the normalized
  name in [`spec/markers.json`](https://github.com/superfly/client-signals/blob/main/spec/markers.json).
  Nothing in this repository checks that. If the marker table renames it, this
  traffic quietly reclassifies to `other` with no failure.

## This is a stopgap

`markers.json` already carries an `ANTIGRAVITY_AGENT` env marker, so an
Antigravity CLI that links `client-signals` would emit these headers itself from
real detection. If that lands, remove this block rather than leaving two sources
setting the same header names.

## Adding headers

Keep secrets out of `mcp_config.json`. Antigravity supports `${VAR_NAME}`
substitution in header values; use it instead of literal tokens.

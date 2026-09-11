# Environment setup

Two separate mechanisms are involved and they are easy to confuse. They have
different traffic paths, different persistence rules, and only one of them needs
the allowlist.

## 1. MCP servers vs MCP connectors

| | MCP connector | MCP server via `claude mcp add` |
|---|---|---|
| Where you enable it | claude.ai UI, per session or per routine | Command line, writes a config file |
| Traffic path | Through Anthropic's servers | Out through the session's own network |
| Needs the domain allowlisted | **No** | **Yes** |
| Persists to the repo | No, per session | Only at `--scope project` |

This is why the Eurostat server failed. `claude mcp add` runs it from inside the
session VM, so it goes through the egress proxy and hits the allowlist.

There is a second trap: `claude mcp add` at the default local scope writes to
`~/.claude.json` on the machine, which cloud sessions do not carry over. That
config is gone next session. Only `--scope project` writes the repo's
`.mcp.json`, which is part of the clone and therefore survives.

The server is now registered at project scope and `.mcp.json` is committed, so
it persists. It still needs the allowlist because of the traffic path above.

## 2. Adding the domains

Network access is a property of the **cloud environment**, not of the session or
the repo. Four levels:

| Level | Outbound |
|---|---|
| None | Nothing through the session network |
| **Trusted** (default) | Package registries, GitHub, cloud SDKs |
| Full | Any domain |
| **Custom** | Your own list, optionally plus the defaults |

To change it: open the environment for editing via the **cloud icon** on the
task or session surface, then use the **Network access** selector in the dialog.
Personal environments have no separate page in claude.ai settings, so the cloud
icon is the way in.

Select **Custom**, then put one domain per line in **Allowed domains**:

```
www.eurocontrol.int
ansperformance.eu
ec.europa.eu
data-api.ecb.europa.eu
www.ecb.europa.eu
sdmx.oecd.org
api.gdeltproject.org
eurostat.caseyjhand.com
```

**Check "Also include default list of common package managers."** Leaving it
unchecked allows *only* what is listed, which would cut off pip, npm, and
`raw.githubusercontent.com`. That breaks the session in ways that look unrelated
to this change and are annoying to diagnose.

A leading `*.` matches subdomains, so `*.europa.eu` would cover the Eurostat,
ECB and Commission hosts in one line. The explicit list above is narrower and
preferable.

Each environment has its own list. There is no organization-level allowlist an
admin can push, so this is set per environment by whoever owns it.

## 3. Which path to use for Eurostat

Either works:

- **Connector**, if the claude.ai UI accepts a custom HTTP MCP server. No
  allowlist entry needed, but it is per session and not captured in the repo.
- **Project-scoped server** (what is committed here). Reproducible for anyone
  who clones the repo, but requires `eurostat.caseyjhand.com` in the allowlist.

The committed `.mcp.json` is the better default for a shared project, since the
configuration travels with the code.

Note that neither changes the production recommendation in
`docs/sources/eurostat.md`: explore through the MCP server, ingest through
Eurostat's own API on `ec.europa.eu`. The pipeline should not depend on a
third-party wrapper.

## 4. Applying the change

Environment edits apply to sessions started afterwards. This session will not
pick up a new allowlist, so start a new session once the domains are saved. Tell
me when that is done and I will retest all eight.

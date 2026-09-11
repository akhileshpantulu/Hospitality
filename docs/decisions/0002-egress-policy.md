# ADR 0002: Egress policy blocks every data source domain

**Date:** 2026-09-11
**Status:** Open, needs a decision

## Finding

This session's network egress proxy enforces an allowlist. Tested directly:

| Domain | Purpose | Result |
|---|---|---|
| `github.com` | control | reachable |
| `www.eurocontrol.int` | EUROCONTROL daily traffic | **blocked** |
| `ansperformance.eu` | EUROCONTROL data portal | **blocked** |
| `ec.europa.eu` | Eurostat API | **blocked** |
| `data-api.ecb.europa.eu` | ECB Data Portal API | **blocked** |
| `www.ecb.europa.eu` | ECB reference rates | **blocked** |
| `sdmx.oecd.org` | OECD SDMX API | **blocked** |
| `api.gdeltproject.org` | GDELT news graph | **blocked** |

Web search still works, so a source can be researched and specced here. It
cannot be called, which means a connector cannot be tested against a live
endpoint in this environment.

## Scope of the problem

This constrains **development**, not the production design. A scheduled pipeline
running in GitHub Actions or on Highgate infrastructure has normal egress. The
cost of the block is that connectors would be written against documented API
contracts and first executed in CI, where failures are slower and noisier to
diagnose than they would be here.

The risk is concentrated in exactly the places that are hardest to get right
from documentation alone: SDMX query syntax for Eurostat and OECD, the actual
shape of EUROCONTROL's CSV exports, and GDELT's query grammar. These are not
things worth guessing at.

## Options

**A. Extend the environment allowlist.** Requires an environment configuration
change by the user or an administrator. See
https://code.claude.com/docs/en/claude-code-on-the-web for how network policy
is set. Minimum useful list:

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

`eurostat.caseyjhand.com` hosts the `eurostat-mcp-server` MCP connector
registered on 2026-09-11. It fails the same way: `403 Forbidden` on the CONNECT
tunnel. Note that `claude mcp list` reports this as "Needs authentication",
which is misleading and would send someone hunting for a credential that does
not exist.

Add later, per country, if national statistics connectors are built:
`www.ons.gov.uk`, `www.ine.es`, `esploradati.istat.it`, `www-genesis.destatis.de`.

**B. Develop blind, verify in CI.** Write connectors against published API docs
with recorded fixtures for tests, and let the first live run happen in GitHub
Actions. Workable, slower, and the SDMX endpoints in particular will take
several rounds to get right.

**C. Spec only here, build elsewhere.** This session produces the source specs,
schema and scoring design; someone else implements against live endpoints.

## Recommendation

A, falling back to B. The allowlist is seven domains and all of them are public
government or intergovernmental data services, so the policy case is
straightforward.

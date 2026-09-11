# European Hospitality Market Signal Dashboard

A daily-refreshed view of European lodging markets, ranked by the balance of
positive tailwinds against significant headwinds.

## What this is

Every market gets a composite signal built from independent, individually
sourced indicators: demand, supply, macro, cost, and risk. The dashboard shows
which markets are accelerating, which are deteriorating, and - critically -
*which indicator is driving the call*, so the output is auditable rather than a
black-box score.

## Design principles

1. **One normalized observation schema.** Every source, paid or public, lands in
   the same shape. Adding a source never changes the scoring engine.
2. **Point-in-time correctness.** Macro and tourism series get revised. Every
   observation carries a `retrieved_at` vintage so a historical score can be
   reproduced exactly as it was computed on the day.
3. **Cache-first.** The pipeline writes to `data/`; the dashboard only reads.
   Viewing the dashboard costs nothing and hits no API.
4. **Per-source cadence.** The scheduler runs daily, but each source declares
   its own refresh interval. Monthly series are not re-fetched 30 times.
5. **License-aware.** Licensed feeds (STR/CoStar) are flagged non-redistributable
   and surface as derived indices, never as raw ADR/RevPAR values.

## Status

Scaffolding only. **No indicator data has been ingested.** Sources are being
worked through one at a time - see `docs/sources/README.md` for the queue.

## Layout

```
config/     markets.yml, sources.yml, indicators.yml, scoring.yml
docs/       architecture, per-source specs, decision records
src/        schema, source connectors, scoring engine
data/       raw/ (as-fetched) and curated/ (normalized observations)
dashboard/  presentation layer
```

# ADR 0001: Market spine without STR

**Date:** 2026-09-11
**Status:** Accepted

## Context

The original design used STR market boundaries as the spine that every source
joins to. STR is deferred (see `docs/backlog.md`), so that spine is unavailable
and the 49-market universe needs a different anchor.

## Decision

Anchor each market on three public keys instead of one proprietary one:

| Key | Joins | Level |
|---|---|---|
| `nuts` (list) | Eurostat tourism, Eurostat regional macro | NUTS 2/3 |
| `airports` (IATA list) | EUROCONTROL, Eurostat aviation | Airport |
| `country` (ISO 3166-1 alpha-2) | ECB, OECD, FX, advisories | Country |

A market is defined as the union of its NUTS regions plus its airport
catchment. No single key is authoritative; each source uses whichever key it
supports, and the `Observation.geo_level` field records which was used.

## Consequences

**Positive.** Every key is public and stable, so the crosswalk is verifiable by
anyone and carries no licence restriction. It also decouples the universe from
any one vendor, so adding STR later is an additional key rather than a rebuild.

**Negative, and material.**

1. **Boundary mismatch.** A NUTS region is not a hotel market. NUTS2 Cataluña is
   far larger than the Barcelona hotel market; Greater London maps reasonably,
   the Algarve maps well, Île-de-France overstates Paris. Every market needs a
   per-market judgement on which NUTS codes to include, and the residual error
   recorded rather than ignored.

2. **Non-EU coverage is uneven.** Eurostat regional coverage does not extend to
   the UK post-Brexit, so UK markets need ONS ITL-coded data from a separate
   connector. Switzerland, Norway and Iceland appear in some Eurostat series and
   not others. Turkey is inconsistent. These are four separate exceptions, not
   one, and each is its own small connector.

3. **No validation target.** Without STR there is no series to test leading
   indicators against. Indicator weights in `config/scoring.yml` will be set by
   judgement, not fitted. This must be stated on the dashboard. When STR is
   added, the first task is to backtest and re-weight.

## Alternatives rejected

- **Country-level only.** Removes the boundary-mismatch problem entirely but
  discards the market-level resolution that makes the dashboard worth building.
- **Airport catchment only.** Clean and consistent, but leaves resort markets
  served by multiple distant airports (Algarve, Crete, Costa del Sol) badly
  represented and gives no macro or tourism join.

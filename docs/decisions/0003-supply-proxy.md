# ADR 0003: Accommodation capacity replaces building permits as the supply proxy

**Date:** 2026-09-11
**Status:** Accepted
**Supersedes:** the supply proxy choice recorded in `config/sources.yml` on 2026-09-11

## Context

STR Pipeline is not in the entitlement, so hotel rooms under construction has no
source. The initial fallback was Eurostat building permits and construction
output, accepted as weak and flagged with confidence below 1.0.

Researching Eurostat's tourism family surfaced a better option:
`tour_cap_nuts2d`, establishments and bed places by NUTS 2 region, annual from
2012.

## Decision

Use accommodation capacity (`tour_cap_nuts2d`) as the primary supply measure.
Retain building permits as a secondary directional hint only.

## Rationale

Bed places measure accommodation supply directly. Building permits measure all
construction, of which hotels are a small and variable share, so the permits
series moves for reasons that have nothing to do with lodging supply.

More importantly, bed places pair with `tour_occ_nin2m` on the same geography
and the same source. Year-over-year bed-place growth against nights-spent growth
is a genuine supply-demand balance measure for a market. Permits could never
produce that, because they do not share a denominator with anything on the
demand side.

## Costs

**Annual frequency.** Acceptable. Supply moves slowly, and a pipeline signal
that changed daily would be noise. It does mean new supply is visible only after
it opens, so this measures realised supply, not the forward pipeline. The
forward view remains genuinely missing and stays on the backlog.

**All accommodation, not hotels.** Bed places include campsites and holiday
dwellings, whose share varies enormously by market. It is a large share in the
Algarve and Crete, small in Frankfurt and Zurich. Comparing bed-place growth
across markets is therefore unsafe; comparing a market against its own history
is fine. The scoring engine must use the within-market time series, not a
cross-market level.

**Confidence stays below 1.0.** This is still a proxy. It is a better proxy.

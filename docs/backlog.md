# Deferred sources

Not rejected. Parked with the reason and what unblocks them.

## STR Destination Report

**Deferred:** 2026-09-11
**Spec:** `docs/sources/str_destination_report.md` (complete)

Retrieval needs a Power Automate flow, a Graph app registration, or a manual
save, and none is set up. Full spec is written, so picking this up later is a
retrieval decision plus a parser, not a fresh investigation.

**Why it matters when it returns.** It is the dependent variable. The first task
on adding it is to backtest the indicator weights in `config/scoring.yml`, which
are currently set by judgement because nothing exists to fit them against.

**Also unblocks:** reconciling `config/markets.yml` to a real hotel-market
geography, which would materially reduce the NUTS boundary error recorded in
ADR 0001.

## STR Pipeline / Lodging Econometrics

**Deferred:** 2026-09-11

Supply pipeline is proxied from public construction data for now, flagged low
confidence. Revisit if the proxy proves too weak to separate markets.

## OAG / Cirium forward seat capacity

Paid, no decision taken. With no Forward STAR and no STR, forward-looking
demand currently has no source at all beyond EUROCONTROL's short horizon. This
is the largest remaining hole in the design.

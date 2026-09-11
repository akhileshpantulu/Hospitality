# Sourcing queue

One source at a time. A source moves `proposed -> approved -> wired` only after
its spec doc is written and signed off. Nothing is ingested before that.

## Per-source spec template

Each source gets `docs/sources/<source_id>.md` answering, in order:

1. **What question does it answer?** If it does not change a tailwind/headwind
   call for at least one market, it does not belong in the dashboard.
2. **Access mechanics.** Endpoint, auth, rate limits, pagination, bulk vs
   incremental, who owns the credential.
3. **Coverage.** Which of the 49 markets it actually reaches, and what the
   gaps are. Partial coverage is fine; silent partial coverage is not.
4. **Geography join.** Which key it maps to on the market spine, and how lossy
   that mapping is.
5. **Frequency and lag.** Publication cadence, typical lag, revision behaviour.
6. **Indicator definitions.** Exact series, units, direction, transform.
7. **Licence.** Redistributable, attribution required, or derived-only.
8. **Cost.** Free, held subscription, or a buy decision.
9. **Failure modes.** What a bad day looks like, and what the connector does
   about it.
10. **Decision.** Approved, rejected, or deferred, with the reason.

## Queue

| # | Task | Source | Why this order | Status |
|---|------|--------|----------------|--------|
| 0 | Market crosswalk | NUTS + IATA + ISO country (ADR 0001) | Every other source joins to this spine. Blocks everything. | Pending |
| 1 | Lodging performance | `str_destination` | Specced. Deferred by decision, see docs/backlog.md. | Deferred |
| 2 | Supply pipeline | `construction_proxy` | Public proxy chosen over a paid feed. Low confidence by design. | Pending |
| 3 | Air connectivity, live | `eurocontrol` | Free, daily, no auth. Carries the live layer alone now that STR is deferred. | Approved, blocked on egress |
| 4 | Air connectivity, forward | `oag` | Best leading indicator, but a buy decision. | Pending |
| 5 | FX | `ecb_fx` | Free, daily, trivial to wire, real explanatory power for leisure markets. | Pending |
| 6 | Macro | `ecb_sdw`, `eurostat_macro`, `oecd` | Slow-moving; sets the baseline rather than the signal. | Pending |
| 7 | Tourism | `eurostat_tour`, `national_stats` | Cross-check on STR share, not a primary signal. | Pending |
| 8 | News and sentiment | `gdelt` | Needs a scored baseline before it is trustworthy. | Pending |
| 9 | Risk and disruption | `travel_advisories`, `disruption` | Event-driven overlay on top of a working scored base. | Pending |
| 10 | Cost and capital | `cost_inputs`, `transactions` | Turns a RevPAR call into a profit and value call. | Pending |
| 11 | Group and events | `event_calendar` | Highest maintenance cost per unit of signal. Last, and only for tier 1. | Pending |

## Sequencing rationale

The spine comes first because a market crosswalk error silently corrupts every
downstream join, and those errors are extremely hard to detect once scores are
being produced. STR performance data comes second because it is the series
every other indicator is ultimately trying to predict; without it we have no
way to test whether a proposed leading indicator actually leads anything.

Free daily sources (EUROCONTROL, ECB FX) come before paid and lagged ones so
there is a live, refreshing dashboard early, even if thin.

News and event sources come last deliberately. They are the easiest to add and
the easiest to get wrong: an unbaselined news-tone signal generates constant
false positives, and it is only diagnosable against a working scored base.

## Findings log

**2026-09-11, Source 1 (STR).** Entitlement is the Destination Report, not
Trend/STAR. Three consequences that change the design:

1. **Monthly, not daily.** Data arrives 17-18 days after month end, so effective
   staleness is 18-48 days. STR anchors the level; it cannot drive a live view.
   The dashboard is two-speed and must say so on its face.
2. **No pipeline entitlement.** Supply headwind has no source. Logged as an open
   gap rather than quietly dropped.
3. **The destination set defines the universe.** `config/markets.yml` was drafted
   independently and must be reconciled to whatever the report actually covers.
   Markets outside that set keep a place in the dashboard but carry no lodging
   data and must be flagged, not scored as merely missing.

**2026-09-11, environment.** The egress proxy allowlist blocks every data source
domain in the registry (ADR 0002). Sources can still be researched and specced
via web search, but no connector can be tested against a live endpoint here
until the allowlist is extended. This does not affect the production design; a
pipeline in GitHub Actions or on Highgate infrastructure has normal egress.

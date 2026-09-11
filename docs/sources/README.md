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
| 0 | Market crosswalk | `str_costar` market list | Every other source joins to this spine. Blocks everything. | **Next** |
| 1 | Lodging performance | `str_costar` | The dependent variable. Without it there is no way to validate any other signal. | Pending |
| 2 | Supply pipeline | `str_pipeline` | Same credential, same join, immediate headwind signal. | Pending |
| 3 | Air connectivity, live | `eurocontrol` | Free, daily, no auth. Highest frequency signal in the stack. | Pending |
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

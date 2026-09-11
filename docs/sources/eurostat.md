# Source 4: Eurostat

**Status:** dataset shortlist drafted, access blocked on egress (ADR 0002)
**Registry ids:** `eurostat_tour`, `eurostat_avia`, `eurostat_macro`, `eurostat_capacity`

## Access: two paths, and they are not interchangeable

**Exploration:** `eurostat-mcp-server` (`https://eurostat.caseyjhand.com/mcp`),
registered in project config on 2026-09-11. Currently unreachable: the egress
proxy returns `403 Forbidden` on the CONNECT tunnel. The `claude mcp list`
health check reports this as "Needs authentication", which is misleading; the
underlying cause is the allowlist, not a credential.

**Production:** Eurostat's own API on `ec.europa.eu`.

These should stay separate. The MCP server is a third-party wrapper on a
personal domain, which is fine for interactive exploration but a poor thing for
a scheduled pipeline to depend on: it introduces an availability dependency on
someone else's infrastructure and a provenance question about whether returned
values match Eurostat's. Anything it returns is untrusted input and should be
spot-checked against `ec.europa.eu` before it sets a scoring weight.

Recommendation: explore with the MCP, ingest with the official API.

## Candidate datasets

Codes marked **[v]** were verified to exist via search. Codes marked **[?]** are
from recall and must be confirmed before any connector references them. A wrong
dataset code is a silent failure, which is why they are separated here.

### Tourism demand - the STR stand-in

With STR deferred, this is the closest public proxy to lodging demand.

| Code | What | Geo | Freq | Value |
|---|---|---|---|---|
| `tour_occ_nin2m` **[v]** | Nights spent at tourist accommodation | NUTS 2 | Monthly | **Primary.** Regional and monthly is the best public match to the market spine. |
| `tour_occ_nin3` **[v]** | Nights spent | NUTS 3 | Annual | Better geography, worse frequency. Use to weight NUTS 2 down to market level. |
| `tour_occ_nim` **[v]** | Nights spent | Country | Monthly | National context and a cross-check on the regional series. |
| `tour_occ_arn2` **[v]** | Arrivals at accommodation | NUTS 2 | Monthly | Arrivals vs nights gives length of stay, which shifts when a market's mix moves between leisure and corporate. |
| `tour_occ_ninat` **[?]** | Nights by country of residence | Country | Monthly | Source-market mix. Needed to make FX weighting meaningful. |

Caveat that matters: these cover **all** tourist accommodation, not branded
hotels. A market where short-term rentals are taking share will look healthier
here than STR would show it. That is useful information in itself, but it means
this series is not a substitute for STR, and the dashboard should not present it
as one.

### Supply - upgrade to the building-permits proxy

| Code | What | Geo | Freq | Value |
|---|---|---|---|---|
| `tour_cap_nuts2d` **[v]** | Establishments and bed places | NUTS 2 | Annual | **Better than the building-permits proxy.** Measures actual accommodation supply rather than all construction. |
| `tgs00112` **[v]** | Establishments and bed places | NUTS 2 | Annual | Same family, pre-built table. |
| `sts_cobp_a` **[?]** | Building permits | Country | Annual | Keep as a leading indicator only. Bed places are the level; permits hint at direction. |

Annual frequency is acceptable here because supply moves slowly. Year-over-year
bed-place growth against nights-spent growth is a real supply-demand balance
measure, and it is the single most useful thing this source unlocks.

This supersedes the earlier decision to proxy supply from building permits
alone. See ADR 0003.

### Aviation

| Code | What | Geo | Freq | Value |
|---|---|---|---|---|
| `avia_par_<cc>` **[v]** | Passengers on airport-to-airport routes | Airport pair | Monthly | **High value.** Gives inbound passengers by origin, which yields a source-market mix per market. That mix is what makes FX weighting meaningful rather than decorative. |
| `avia_paoc` **[v]** | Air passengers by schedule and coverage | Country | Monthly | National aviation context, 1993 to 2026Q2. |

Lagged by roughly three months, so this is structural rather than live. It
complements EUROCONTROL rather than duplicating it: EUROCONTROL says how many
flights moved today, Eurostat says where the passengers actually came from.

### Regional macro

| Code | What | Geo | Freq |
|---|---|---|---|
| `nama_10r_2gdp` **[?]** | Regional GDP | NUTS 2 | Annual |
| `lfst_r_lfu3rt` **[?]** | Regional unemployment rate | NUTS 2 | Annual |
| `prc_hicp_midx` **[?]** | HICP price index | Country | Monthly |
| `ei_bsco_m` **[?]** | Consumer confidence | Country | Monthly |

Lowest priority of the four families. Macro sets the baseline rather than the
signal, and the country-level series overlap with ECB and OECD coverage.

## Coverage gap, unchanged from ADR 0001

Eurostat regional coverage does not extend to the UK post-Brexit. London,
Edinburgh and Manchester are three of the larger markets in the universe and
need ONS data from a separate connector. Switzerland, Norway, Iceland and
Turkey appear inconsistently by dataset and must be checked series by series,
not assumed.

## Priority

1. `tour_occ_nin2m` - the demand signal, and the main thing this source is for
2. `tour_cap_nuts2d` - the supply signal, better than what it replaces
3. `avia_par_<cc>` - source-market mix, which unlocks meaningful FX weighting
4. Regional macro - baseline only

## Next step

Once egress opens: confirm the **[?]** codes, check the real NUTS coverage per
market rather than assuming it, and establish how each series handles revisions
before writing a connector.

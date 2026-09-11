# Source 1: STR Destination Report

**Status:** specced, blocked on file inspection
**Registry id:** `str_destination`

## 1. What question does it answer?

Actual lodging performance by destination: occupancy, ADR, RevPAR and their
year-over-year change. This is the dependent variable. Every other indicator in
the dashboard is ultimately a claim about where these numbers are heading, so
without it there is no way to test whether a proposed leading indicator leads
anything at all.

## 2. Access mechanics

Confirmed by inspection of the mailbox:

| Property | Finding |
|---|---|
| Sender | `destin@str.com` |
| Subject | `Highgate Hotels Intl Ltd Monthly Report - <Mon YYYY>` |
| Attachment | `HighgateHotelsIntlLtd_<YYYYMM>.xls`, ~145 KB |
| Format | Legacy `.xls`, served as `application/octet-stream` |
| Cadence | Monthly |
| Arrival | ~17th-18th of the month following the data month |
| History in mailbox | Dec 2025 through Jul 2026 confirmed, more beyond |
| Archived elsewhere | No. Not in SharePoint, not in Box. |

The subject line and filename are both deterministic, which makes identification
trivial. Retrieval is the problem, not identification.

**Blocking constraint:** the Microsoft 365 connector returns binary attachments
as a stub, not as content. The file cannot be read programmatically through the
current tooling, and no copy exists in any document store.

### Retrieval options

| | Approach | Setup | Ongoing | Notes |
|---|---|---|---|---|
| A | Power Automate flow saves the attachment to a SharePoint library on arrival | One-time, no new app registration, uses existing M365 | None | Pipeline then reads the library. Recommended. |
| B | Dedicated Graph app registration with `Mail.Read`, pipeline pulls the attachment directly | Needs IT approval | None | Cleanest technically, slowest to get approved. |
| C | Outlook rule flags it, someone saves the file manually | None | ~2 min/month | Viable given monthly cadence. Fails silently if the person is on holiday. |
| D | Backfill: save the existing back issues once | ~20 min | N/A | Needed regardless of which of A-C is chosen, to build history. |

D is required in all cases. Without backfill there is no baseline, and without a
baseline every indicator's z-score is undefined.

## 3. Coverage

**Unknown and material.** The Destination Report covers the destination set
attached to Highgate's subscription, not all European markets. The 49-market
draft universe in `config/markets.yml` was written independently and almost
certainly does not match. Until one file is opened we do not know:

- which destinations are included
- whether they are STR market boundaries or custom-defined tracts
- whether competitive sets or only aggregate destination data are present

This is the single unknown that gates the market universe, and therefore gates
every other source's crosswalk.

## 4. Geography join

Destination names in the report become the spine. `config/markets.yml` must be
reconciled to that list, not the other way round. Markets in the draft universe
with no Destination Report coverage stay in the dashboard but carry no lodging
performance data, and must be visibly flagged as such rather than scored as if
the data were merely missing.

## 5. Frequency and lag

Monthly, arriving 17-18 days after month end. Effective staleness at any given
moment is 18 to 48 days.

**Consequence for the design:** STR cannot be the live layer. The dashboard is
two-speed. STR is the slow authoritative base that anchors the level; the daily
movement has to come from EUROCONTROL flights, ECB FX and news. This should be
explicit in the UI, because a user looking at a "live" dashboard will otherwise
assume the RevPAR figure is current.

STR restates prior months as more properties report. The connector must treat
every month in each file as potentially revised, not append-only. The `vintage`
field on `Observation` exists for exactly this.

## 6. Indicator definitions

To be confirmed against the file. Expected:

| indicator_id | unit | direction | transform |
|---|---|---|---|
| `occupancy` | % | higher_is_tailwind | yoy |
| `adr` | local ccy | higher_is_tailwind | yoy |
| `revpar` | local ccy | higher_is_tailwind | yoy |
| `supply_roomnights` | count | higher_is_headwind | yoy |
| `demand_roomnights` | count | higher_is_tailwind | yoy |

ADR in local currency needs an FX view for cross-market comparison, which is why
`ecb_fx` is sequenced early rather than as a nice-to-have.

## 7. Licence

Restricted. STR terms do not permit redistribution of raw benchmarking values.
The dashboard shows indexed or YoY-delta form only. Raw ADR and RevPAR stay in
`data/` and never reach a published surface.

## 8. Cost

Held subscription, no incremental cost.

## 9. Failure modes

- Report does not arrive, or arrives late. Pipeline must surface staleness on
  the dashboard rather than silently showing last month's figure as current.
- STR changes the file layout. Legacy `.xls` exports are fragile. The parser
  must validate expected columns and fail loudly rather than mis-map.
- A destination is added to or dropped from the subscription. Coverage must be
  diffed against the prior month every run.

## 10. Gaps this source does not fill

**No pipeline data.** The entitlement is Destination Report only, so rooms under
construction and rooms in final planning are unavailable. Supply is one of the
strongest medium-term headwind signals in any hotel market and there is
currently no source for it. Options: buy Lodging Econometrics or an STR Pipeline
add-on, proxy weakly from Eurostat building permits, or track manually for tier-1
markets only. Needs a decision, tracked as its own queue item.

**No forward-looking data.** No Forward STAR, so no on-the-books view. Forward
demand has to come from air capacity instead, which raises the value of the OAG
buy decision.

## Decision

Deferred pending inspection of one report file.

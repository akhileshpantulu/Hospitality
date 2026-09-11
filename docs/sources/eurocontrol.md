# Source 3: EUROCONTROL daily traffic

**Status:** partially specced, mechanics blocked on egress (ADR 0002)
**Registry id:** `eurocontrol`

## 1. What question does it answer?

How much air traffic is actually moving into a market right now, versus the
same day last year. With STR deferred, this is the only genuinely daily signal
in the design, so it carries the live layer alone.

Flights are a coarse proxy for demand: a flight count says nothing about load
factor, aircraft size, or whether passengers are inbound tourists or connecting.
It is directional, not quantitative, and the scoring engine should treat it that
way. It earns its place on frequency and freshness, not precision.

## 2. Access mechanics

**BLOCKED.** `www.eurocontrol.int` and `ansperformance.eu` are both denied by
the egress allowlist. Confirmed to exist via search:

- Daily Traffic Variation - Airports: `eurocontrol.int/Economics/DailyTrafficVariation-Airports.html`
- Airport Traffic Dataset reference: `ansperformance.eu/reference/dataset/airport-traffic/`
- Portal data index: `ansperformance.eu/data/`

Unresolved until access opens, and **not worth guessing at**:

- exact download URL and whether it is stable or date-stamped
- file format and whether the daily file is a full history or an increment
- column names and units
- whether the series is flights or passengers
- publication time of day and typical lag
- rate limits or terms of use

## 3. Coverage

Airport-level across the EUROCONTROL member area. Expected to cover every
airport in `config/markets.yml` with two caveats to verify: Turkish airports
(IST, SAW, AYT) may be partially covered since Turkey's participation differs
by dataset, and small resort airports (JTR, JMK) may be absent or noisy.

## 4. Geography join

Joins on the `airports` IATA list in `config/markets.yml`. EUROCONTROL works in
ICAO codes, so the crosswalk needs an IATA-to-ICAO mapping as an extra step.

Join quality varies sharply by market type. It is good for single-airport city
markets (VIE, PRG, CPH). It is poor for multi-airport markets where catchments
overlap (London's five, Milan's three) and for resort markets served by distant
airports where a large share of arrivals come by road or ferry (Algarve, Costa
del Sol, Dalmatia). Those markets need a lower confidence value, not exclusion.

## 5. Frequency and lag

Daily, with a lag expected in days rather than weeks. To be confirmed.

## 6. Indicator definitions

| indicator_id | unit | direction | transform | notes |
|---|---|---|---|---|
| `daily_flights` | count | context_only | level | raw level is not comparable across markets |
| `flights_yoy` | % | higher_is_tailwind | yoy | the actual signal |
| `flights_yoy_7dma` | % | higher_is_tailwind | yoy | smoothed; daily is too noisy to score directly |

Scoring should use the smoothed series. Day-of-week effects and single-day
disruptions (a strike, a storm) otherwise produce constant false signals, which
is the same failure mode that puts news sources last in the queue.

## 7. Licence

Attribution. Public EUROCONTROL data, redistributable with credit. Exact wording
to confirm against the portal terms once reachable.

## 8. Cost

Free.

## 9. Failure modes

- Publication skips a day or is late. Must surface staleness, not carry forward.
- Airport closure or ATC strike collapses the count. This is a real headwind
  signal, not bad data, and must not be smoothed away entirely. The 7-day mean
  handles noise; a sustained drop should still reach the score.
- A market's airports change coverage between releases. Diff the airport set
  each run.

## 10. Decision

Approved in principle. Implementation blocked until egress opens, at which point
sections 2 and 5 get completed from the live endpoint rather than from guesses.

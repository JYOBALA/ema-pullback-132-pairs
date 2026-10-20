# The tuning phase: 14 variants on one asset

Before the 132-pair sweep there was a single-asset tuning phase on **BINANCE.F:HYPEUSDT**, run 2026-10-18. Its purpose was to find the best configuration of the strategy and freeze it. It also produced the cost analysis that explains *why* the configuration ended up where it did — and one hypothesis that later turned out to be wrong, documented here rather than quietly dropped.

Full Indonesian original: [`raw/backtest_log.md`](../raw/backtest_log.md).

> **Naming note.** The chart legend says "Hyperliquid" because HYPE is the Hyperliquid exchange token. The *data source* for this phase was Binance Futures, not Hyperliquid. The venue gap was closed later — batch 1 of the sweep ran natively on `HYPERLIQUID.F`.

---

## Engine facts that determine how to read everything

| Fact | Consequence |
|---|---|
| Limit entry and limit TP are **maker**, no slippage | The cheap path |
| A limit is treated as filled the moment price **touches** the level — no queue model | Limit-entry results are **optimistic**; live, many would not fill |
| Stop / market / `closeAll` are **taker + slippage** | The expensive path |
| Bracket exits activate only from the bar *after* the entry fills | The first bar is unprotected |
| The tester only evaluates bars already loaded into the chart | Bar count must be panned in and recorded every run |

## Costs, measured rather than assumed

Taken directly from the `FEES` column of the Trades tab, on $10,000 notional:

| Exit path | Round-trip fee | Composition |
|---|---|---|
| `limit` (take-profit) | **$3.94** | maker in + maker out |
| `stop` | **~$6.45** | maker in + taker out + slippage |
| `closeAll` (time stop) | ~$6.45 | market out — the most expensive exit |

On the 15m default baseline: $2,413.6 of fees ÷ 459 trades = **$5.26 per trade**.

That average decomposes. Solving `x·3.94 + (1−x)·6.45 = 5.26` gives **x ≈ 47% limit exits / 53% stop exits** — which matches the 47.7% win rate almost exactly. In other words: **practically every win exits as a take-profit limit and every loss exits as a stop.** The cost structure is therefore not an average to be smoothed over; it is determined by the win rate.

## The cost/R framework

Expectancy per trade decomposes as:

```
expectancy_R  =  raw_edge_R  −  cost_per_trade / R
```

With a tight stop, `R` (the dollar risk per trade) is small, so `cost/R` is large and dominates. This is what drove the three parameter changes that define the final configuration:

| Change | From → To | Reasoning |
|---|---|---|
| `min_risk_pct` | 0.3 → **1.5** | Wider stop ⇒ larger R ⇒ smaller `cost/R`. Fees are a % of notional and do not grow with R. |
| `max_hold` | 24 → **96** | A 24-bar time stop forced exits through `closeAll` (market, taker + slippage — the dearest path). At 96 bars, exits migrate to the take-profit limit, which pays maker. |
| `be_trigger_r` | 1.0 → **8.0** | Disables the breakeven lock. At wide R the lock was cutting winners short: payoff ratio rose 0.86 → 1.35 once it was off. |

## Results: 5-minute bars

Window ≈ 3,652–3,655 bars (12.7 days). "Zero" means all three cost parameters set to 0 — a cost ablation to isolate the signal itself.

| # | Variant | Costs | Change (one at a time) | Trades | Win% | Net % | PF |
|---|---|---|---|---|---|---|---|
| 1 | V0 baseline | real | defaults | 396 | 45.2% | **−30.23%** | 0.58 |
| 2 | E1 | **zero** | defaults | 396 | 49.0% | **−6.65%** | **0.90** |
| 3 | E2 | zero | `be_trigger_r` 1 → 8 | 344 | 40% | −2.69% | — |
| 4 | E3 | zero | + `min_risk_pct` 0.3 → 0.8 | 155 | 47.7% | +4.42% | 1.09 |
| 5 | E4 | zero | `min_risk_pct` 0.8 → 1.5 | 131 | 47% | +2.37% | — |
| 6 | E5 | **real** | E3 configuration | 155 | 44.5% | **−7.57%** | 0.86 |

**The decisive line is E1.** At *zero cost* — no fees, no slippage — the 5m signal still loses, PF 0.90, roughly −0.05R per trade. Costs are not what breaks 5m. The signal is negative before it pays anything.

The best 5m configuration produced an average trade of **+$2.8** against a cost of **$6.3** — a 2.75× gap. 5m was abandoned.

## Results: 15-minute bars

Window ≈ 3,539–3,540 bars (36.9 days).

| # | Variant | Costs | Change | Trades | Win% | Net % | PF |
|---|---|---|---|---|---|---|---|
| 7 | V0-15m baseline | real | defaults | 459 | 47.7% | **−26.78%** | 0.77 |
| 8 | E6 | zero | defaults | 459 | 51% | +2.08% | — |
| 9 | E7 | zero | `be_trigger_r` 1 → 8 | 403 | 41% | −0.92% | — |
| 10 | E8 | zero | + `min_risk_pct` 0.3 → 0.8 | 290 | 53% | +5.70% | — |
| 11 | E9 | zero | `min_risk_pct` 0.8 → 1.5 | 158 | — | +5.97% | — |
| 12 | **E10** | zero | + `max_hold` 24 → 96 | 114 | 54.4% | **+10.73%** | **1.125** |
| 13 | E11 | **real** | E10 configuration | 114 | 54.4% | +2.20% | 1.025 |
| 14 | **E12** | **real** | + `be_trigger_r` 1 → 8 | 98 | 43.9% | **+5.47%** | **1.058** |

**E10 is the ceiling.** It is the best the signal achieves on 15m **with all costs removed**, and it reaches PF **1.125** — below the 1.25 acceptance threshold *before paying a single basis point*. Everything after that is about how much of a sub-threshold edge survives costs.

E12 became the frozen "wide-R" configuration used for all 132 pairs.

## Validation split and stress test on E12

Window split at the UTC-day midpoint (`floor(epoch/86400)`: 2026-09-11 = day 20707, 2026-10-18 = day 20744, midpoint 20725/20726).

| Run | Gating | Trades | Win% | Net % | PF | Max DD |
|---|---|---|---|---|---|---|
| Tuning half | `end_day 20725` | 53 | 47.2% | **+10.87%** | **1.229** | 15.0% |
| **Validation half** | `start_day 20726` | 47 | 38.3% | **−7.87%** | **0.820** | 13.2% |
| **Stress test** | maker 0.05 / slip 5 bps | 98 | 43.9% | **−0.55%** | 0.994 | 18.3% |

Both fail. The validation half is negative and the stress test turns the whole result negative — the edge is thinner than the uncertainty in the cost assumption.

> **Methodological honesty note, recorded at the time:** E6–E12 were tuned on the **full window**, and only then was the split run. The validation half is therefore **not genuinely out-of-sample** — the parameters were chosen with knowledge of all the data. That makes −7.87% an **optimistic** estimate, not a pessimistic one. True out-of-sample would likely be worse.
>
> This is also precisely why the 132-pair sweep matters: for every pair other than HYPE, the configuration was frozen beforehand, so the whole window is genuinely out-of-sample.

## A result that moved because one bar arrived

After the stress test, costs were restored to their real values — making the run **identical to E12**. It did not reproduce:

| | E12 (03:38 UTC) | Re-run (03:45 UTC) |
|---|---|---|
| Bars | 3,540 | 3,541 |
| Trades | 98 | 98 |
| Net | **+$546.9 · +5.47%** | **+$368.2 · +3.68%** |
| Fees | $573.1 | $568.4 |

The trade count is **identical** — no new trade appeared. One new live bar and some minor price revision moved net profit by **−$178.7, about a third of the total result**.

A strategy whose headline figure moves 1.8 percentage points because a single bar arrived does not have a dependable edge. This is the same conclusion the stress test reached, arrived at by accident.

## Timeframe sweep — and a hypothesis that was wrong

All four runs use the identical wide-R configuration and real costs.

| TF | Bars | Span | Trades | Win% | Net % | PF | Avg trade |
|---|---|---|---|---|---|---|---|
| 5m | 3,655 | 12.7 d | 155 | 44.5% | −7.57% | 0.86 | −$4.9 |
| **15m** | 3,540 | 36.9 d | 98 | 43.9% | **+5.47%** | 1.058 | +$5.6 |
| 1h | 2,461 | 102 d | 195 | 41.5% | −0.53% | **0.997** | −$0.3 |
| 4h | 1,316 | 219 d | 149 | 38.3% | −24.89% | 0.883 | −$16.7 |

597 trades across four timeframes; only 15m is positive. 1h has the strongest sample — 195 trades over 102 days — and returns **PF 0.997, which is exactly nothing**.

**This refutes the cost/R hypothesis that guided the tuning.** The reasoning had been: higher timeframe ⇒ larger R ⇒ less cost drag ⇒ better expectancy. But raw edge per trade *fell* going up in timeframe, from roughly $12.7 (15m) to $6.3 (1h). Widening R reduces cost drag; it does not create edge — and at higher timeframes the EMA-pullback signal is weaker still.

The 15m result of +5.47% is best read as an outlier consistent with noise, which is what the validation split and stress test independently indicated.

## What carried into the sweep

- The frozen configuration: `min_risk_pct 1.5`, `max_hold 96`, `be_trigger_r 8.0`, everything else at defaults.
- **1h as the sweep timeframe** — the strongest sample per pair (~2,900+ bars ≈ 120+ days, 100–470 trades), despite 15m being the only positive timeframe on HYPE. Choosing the timeframe with the best single-asset result would have been selecting on the outcome.
- The knowledge that the ceiling at zero cost was 1.125, so a PF of 1.25 after costs was always going to be a demanding bar — which is the right way round for a threshold to be set.

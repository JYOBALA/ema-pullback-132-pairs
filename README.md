# Does an EMA maker-pullback scalper have an edge on crypto perpetuals?

**A pre-registered sweep of one fixed strategy across 132 perpetual-futures pairs on two venues. Zero pairs passed.**

[Bahasa Indonesia →](README.id.md)

---

## Summary

A trend-following maker-pullback scalper — rest a limit order a fraction of an ATR inside an EMA trend, bracket it with a stop and a take-profit — was tested unchanged across **132 perpetual-futures pairs**: 93 on Hyperliquid and 39 on Binance, all on 1-hour bars, all with the same parameters and the same cost assumptions.

**No pair met the acceptance criteria.** The criteria were written down before any pair was opened.

| Metric | Value |
|---|---|
| Pairs tested | **132** (+ 5 preliminary) |
| **Pairs passing the screen** | **0** |
| Profit factor — mean / median | **0.919** / 0.929 |
| Profit factor — max / min | 1.300 (CYS) / 0.567 (Q) |
| Pairs with PF ≥ 1.25 (the threshold) | **1** |
| Net positive after costs | 35 of 132 |
| Beat buy-and-hold | 21 — of which only **10** actually made money |

The interesting result is not that the strategy lost. It is **the shape of how it lost**, and the fact that three separate things which looked like discoveries each dissolved when tested properly. Those three are the substance of this report.

![Profit factor distribution across 132 pairs](figures/fig1-pf-distribution.svg)

The distribution is centred at 0.919 with a thin tail above 1.0. That is the shape you expect from a signal with **no edge that is paying transaction costs**: the centre sits below breakeven by roughly the cost per trade, and everything around it is noise. A strategy that had an edge but needed the right market would produce a *cluster* above the threshold — not one outlier that collapses under examination.

---

## Contents

- [The question](#the-question)
- [The strategy under test](#the-strategy-under-test)
- [Method](#method)
- [Results](#results)
- [Three things that looked like findings](#three-things-that-looked-like-findings)
- [Case studies: the two best candidates](#case-studies-the-two-best-candidates)
- [What would change the conclusion](#what-would-change-the-conclusion)
- [Limitations](#limitations)
- [Reproducing this](#reproducing-this)
- [Repository layout](#repository-layout)
- [Corrections](#corrections)

---

## The question

Not "can this strategy be tuned until it is profitable?" — anything can, on one asset, in hindsight. The question is:

> Holding one parameter set fixed, does this signal produce a positive expectancy that survives costs, on enough instruments that the result cannot be explained by having searched until something looked good?

That framing matters because the obvious way to run a sweep — test many pairs, keep the best — **guarantees** a winner whether or not an edge exists. With 95 independent tests at a 5% false-positive rate you should expect roughly five spurious "winners" purely from noise. Any protocol that does not account for this is not measuring edge; it is measuring how many pairs were tested.

---

## The strategy under test

`HYPE Scalp v4 — maker pullback`, written in wrun-ts for [openmarket.xyz](https://openmarket.xyz). Source: [`strategy/hype_scalp_v4_maker.ts`](strategy/hype_scalp_v4_maker.ts).

**Logic.** When price is above a slow EMA and a fast EMA is above the slow one, rest a **limit buy** a fraction of an ATR below the close; mirrored for shorts. The resting order is cancelled if unfilled after `entry_ttl` bars. Once filled, the position carries a stop and a take-profit limit at a fixed multiple of the risk unit, plus a time stop.

The design point is **cost structure, not prediction**: a resting limit entry pays the maker fee and takes no slippage, and exiting through a take-profit limit does the same. Only the stop crosses the spread.

**Parameters, held constant across all 132 pairs:**

| Parameter | Value | Role |
|---|---|---|
| `fast_len` / `slow_len` | 20 / 100 | EMA trend gate |
| `atr_len` | 14 | volatility unit |
| `pull_atr` | 0.5 | limit entry distance from close, in ATR |
| `stop_atr` | 1.0 | stop distance, in ATR |
| `min_risk_pct` | 1.5 | floor on stop distance, % of entry price |
| `rr` | 1.5 | take-profit as a multiple of risk |
| `be_trigger_r` | 8.0 | breakeven lock, set high enough to disable it |
| `entry_ttl` | 3 | bars a resting entry stays alive |
| `max_hold` | 96 | bars before the time stop |

This is the "wide-R" configuration — the best of 14 variants found during an earlier single-asset tuning phase, documented in [`docs/02-tuning-phase.md`](docs/02-tuning-phase.md). **It was frozen before the sweep began and never re-tuned per pair**, which is what makes every one of the 132 pairs a genuine out-of-sample test of that configuration.

### Why the parameters are what they are

The tuning phase produced one insight worth stating, because it explains the configuration and it generalises.

Round-trip cost was measured directly from the fills, not assumed: **≈ $5.26 per trade on $10,000 notional — about 0.053% of notional**. Expectancy per trade is then:

```
expectancy_R  =  raw_edge_R  −  cost_per_trade / R
```

With a tight stop, `R` is small and `cost/R` is large — the cost term dominates and the strategy cannot win no matter how good the signal is. Widening the stop (`min_risk_pct` 0.3 → 1.5) and letting winners run to a limit exit (`max_hold` 24 → 96, which moves exits off the taker-priced `closeAll`) shrinks the cost drag.

**But widening R reduces cost drag; it does not create edge.** At *zero* assumed cost, the ceiling observed in the tuning phase was PF 1.125 — below the acceptance threshold before paying a single basis point. That is the whole result in miniature, and the 132-pair sweep is its confirmation at scale.

---

## Method

### Engine and cost model

| | |
|---|---|
| Platform | openmarket.xyz Strategy Tester (wrun-ts) |
| Instrument | `perps`, leverage 5, `qtyType: percentOfEquity` 20% → **$10,000 notional** on $10,000 capital |
| Fill model | `pessimistic` |
| Maker fee | 0.02% of notional |
| Taker fee | 0.045% of notional |
| Slippage | 2 bps on market-crossing fills |
| Funding | off |
| Timeframe | 1h |

Costs are strategy **parameters**, not constants, so a stress test is a settings change rather than a recompile.

Two honest caveats about the engine, both of which make results *optimistic*:

1. **Limit orders fill on touch.** There is no queue-position model. A real resting order at the touch price frequently does not fill. This inflates the fill rate of exactly the entries the strategy depends on.
2. **Funding is off.** Perpetual funding is a real recurring cost for held positions. Exposure averaged ~55–60%, so this is not negligible.

Both biases favour the strategy. The conclusion is negative *despite* them.

### The pre-registered protocol

Written into the tracker **before the first pair was opened** and not altered afterwards. Full text: [`docs/01-protocol.md`](docs/01-protocol.md).

A pair passes screening only if **all** of these hold:

| # | Criterion | Rationale |
|---|---|---|
| 1 | **Profit factor ≥ 1.25** | Raised from 1.2 as a multiple-testing correction, *before* seeing data |
| 2 | **Max drawdown < 10%** | |
| 3 | **≥ 60 trades** | So a half-sample split still has ≥ 30 |
| 4 | **Net > 0 after costs** | |
| 5 | **Neither side bleeding** | Losing side must not exceed 50% of the winning side's profit |
| 6 | **Beats buy-and-hold risk-adjusted** | `net% / maxDD` > `B&H% / maxDD_B&H` |

Plus three standing rules:

- **Record every result**, not only the positive ones. The table is filled in order with no exceptions.
- **Judge PF and the comparison to buy-and-hold — not net %.** A high net % in a market that rose 130% is not a finding.
- **Never re-tune per pair.** Every pair is an out-of-sample test of one frozen configuration.

Anything clearing the screen then goes to the full protocol: **tuning/validation split, cost stress test, ±20% parameter neighbours, largest-trade removal.**

### The data-depth rule — added mid-sweep, and why

At pair #11 the sweep hit a methodological flaw serious enough to invalidate everything measured before it.

**DOGE** read **+30.30% with PF 1.301** at 1,715 bars — clearing the threshold, beating buy-and-hold, both sides positive. After loading more history to 3,215 bars, the same configuration read **−15.80% with PF 0.884**. Not weakened. Reversed.

Bar counts had not been standardised. The rule added in response, and applied for the rest of the sweep:

> **Minimum 2,900 bars, and the bar count is recorded on every row.**
> A pair that **passes** at a sub-standard bar count must be **deepened before being recorded**.
> A pair that **fails** is recorded as-is with its bar count flagged.

The asymmetry is deliberate. Deepening is expensive, and a failing pair is not going to be rescued by more data in a way that changes the verdict — but a *passing* pair at a short window is exactly the case where noise masquerades as signal. This rule turned out to be the single most important methodological decision in the project. It caught six false positives.

---

## Results

### The screen, applied in order

![Screening funnel: 132 to 0](figures/fig6-screening-funnel.svg)

132 → 127 (≥ 60 trades) → 34 (net positive) → **1** (PF ≥ 1.25) → **0** (DD < 10%).

The last two criteria — both sides non-bleeding, and beating buy-and-hold risk-adjusted — never became binding, because nothing survived long enough to be tested against them.

### Profit factor against drawdown

![Profit factor vs max drawdown](figures/fig5-dd-vs-pf.svg)

The pass region is empty. Exactly one pair of 132 had a drawdown under 10% — **ASTER at 9.4%** — and it fired just 25 trades on 494 bars of history, far too small to screen. The best-behaved pair with a usable sample was **PAXG** (gold): DD 11.2%, both sides positive, Sharpe +0.91, beat buy-and-hold. It failed on PF (1.158) and trade count (48).

PAXG is worth a sentence on its own, because it is the one qualitative hint in the dataset: if this signal has a natural home, it is in **low-volatility, smoothly-trending instruments**, not altcoins.

### Against simply holding the asset

![Strategy return vs buy-and-hold](figures/fig4-vs-buyhold.svg)

| Outcome | Pairs |
|---|---|
| Beat buy-and-hold | 21 |
| Exact tie | 1 (PENGU) |
| **Lost to buy-and-hold** | **110** |

---

## Three things that looked like findings

### 1. High net % — the AKE trap

**AKE** returned **+319.40%**. In isolation that reads as a major discovery.

Its profit factor was **1.061**, and buy-and-hold over the same window returned **+8,225.6%**.

The strategy captured roughly **4% of what doing nothing would have returned**, while carrying a 69.9% drawdown. Net % in a market that rose 82× measures leverage applied to a trend, not skill. This is why the protocol fixed PF — which is scale-invariant — as the primary criterion, and treats net % as uninformative on its own.

### 2. "Beating buy-and-hold" — mostly not alpha

21 pairs beat buy-and-hold. **11 of them still lost money.**

| Pair | Strategy | Buy-and-hold |
|---|---|---|
| kBONK | −2.48% | −50.80% |
| BLUR | −4.68% | −48.90% |
| USELESS | −31.87% | −53.10% |
| SOPH | −38.57% | −58.50% |
| APR | −69.69% | −85.80% |

They "won" by losing less than an asset that was falling. With average exposure around 55–60%, that is a **low-beta effect from partial market exposure** — mechanical, not alpha. You would get the same effect by holding 55% of the position and nothing else.

Only 10 of 132 pairs beat buy-and-hold *while also making money*, and none of them passed the screen.

### 3. The shallow-window winners — the central finding

This is the result that settles the question.

![Profit factor decay when history is extended](figures/fig2-depth-decay.svg)

Seven pairs reached or approached the threshold on their first reading. **Every one of them declined when more history was loaded. None improved.**

| Pair | Shallow | Deep | Δ | Landed |
|---|---|---|---|---|
| DOGE | 1.301 @ 1,715 bars | 0.884 @ 3,215 | −0.417 | below |
| kBONK | 1.253 @ 1,995 | 0.992 @ 3,495 | −0.261 | below |
| MINA | 1.368 @ 2,744 | 1.220 @ 3,994 | −0.148 | below |
| MAGIC | 1.2428 @ 2,757 | 1.109 @ 4,507 | −0.134 | below |
| RLC | 1.2435 @ 2,757 | 1.109 @ 4,257 | −0.134 | below |
| ZIL | 1.2065 @ 2,507 | 1.140 @ 4,007 | −0.066 | below |
| **CYS** | **1.370 @ 2,758** | **1.300 @ 4,508** | **−0.070** | **above** |

**Why one-directional decay is the diagnostic.** If a strategy has a real edge and the short window merely measures it imprecisely, then extending the sample should move the estimate **in both directions** — sometimes up, sometimes down — converging on the true value. Seven out of seven moving the same way is not imprecision. It is the signature of an estimate that was **biased optimistic** because the short window was selected, implicitly, for looking good.

Magnitude of the bias: **PF measured below ~3,000 bars ran 0.07 to 0.42 too high.**

Two of these deserve a note on process. RLC (1.2435) and MAGIC (1.2428) each landed roughly **0.007 below** the threshold. The rule only *required* deepening for pairs that passed. Both were deepened anyway — letting a rounding margin decide a verdict is precisely the self-deception the protocol exists to prevent. Both fell to 1.109.

---

## Case studies: the two best candidates

![MINA and CYS regime splits](figures/fig3-regime-split.svg)

Two pairs out of 132 reached the full protocol. They failed **identically**.

### MINA — Hyperliquid, 3,994 bars

Full window: **+86.43%, PF 1.220**, DD 30.8%, 360 trades, both sides positive, Sharpe 2.23.

Failed PF at depth (1.220 < 1.25) and DD (30.8% > 10%). The split:

| Period | Trades | Net | PF |
|---|---|---|---|
| First half (~98 days) | 184 | **−17.07%** | 0.897 |
| Second half (~68 days) | 176 | +124.80% | 1.456 |

Methodologically important: **no tuning was ever done on MINA** — the parameters came wholesale from a different asset. So both halves are out-of-sample. The split is therefore not measuring parameter overfitting; it is measuring **stability across time**. And the strategy is not stable.

### CYS — Binance, 4,508 bars

The strongest result in the project, and the only pair whose PF stayed above the threshold at full depth.

| Test | Result | |
|---|---|---|
| PF @ 4,508 bars | **1.300** | pass |
| Cost stress test (maker 0.05%, slippage 5 bps) | PF **1.2503** | pass by 0.0003 |
| Max drawdown | 18.4% | **fail** (> 10%) |
| First half (231 trades) | **−23.95%**, PF 0.918 | **fail** |
| Second half (243 trades) | +677.10%, PF 1.379 | |

Full window net: **+500.54%** against buy-and-hold of **−68.7%**.

That +500% needs three qualifications before it means anything:

1. **Compounding.** `percentOfEquity` sizing means position size grows with equity. Largest win $4,978 and largest loss $4,754 against $10,000 of starting capital show that by the end, single trades were moving half the initial account. The headline figure is dominated by the final trades, not by consistency.
2. **The asset fell 68.7%.** Nearly all the profit came from the short side (+$30,799 vs +$19,255 long), concentrated in one collapse. That is one favourable regime, not a repeatable edge.
3. **The first half lost 24%.** Running this from day one of the available data means losing a quarter of the account across ~94 days before the profitable regime arrived — with nothing guaranteeing it arrives again.

**The decisive observation:** MINA and CYS are unrelated assets on different venues, found in separate batches months apart in the search order. They are the two best results from 132 tests. And they fail in **exactly the same structural way** — first half negative, entire result from the second half. One such case is an anecdote. Two, arrived at independently, is a property of the strategy.

---

## What would change the conclusion

Stated in advance, so the conclusion is falsifiable rather than merely asserted:

- **A cluster of pairs above PF 1.25 at full data depth** — not one, but enough that the count exceeds what multiple testing predicts (~5 of 95 by chance).
- **A candidate whose two halves are both positive**, or at least both above PF 1.0.
- **PF estimates that move in both directions when history is extended.** The current 7-for-7 one-directional decay is the strongest single piece of evidence against the strategy; breaking that pattern would materially weaken this report's conclusion.
- **A positive result at zero assumed cost exceeding PF 1.25.** The tuning phase ceiling was 1.125 before any costs. If that ceiling can be lifted, the cost analysis becomes relevant again; until then it is moot.

---

## Limitations

What this report does **not** establish:

- **It does not show that EMA-pullback logic is worthless in general.** It tests one parameterisation, on 1h bars, on crypto perpetuals, over roughly 4–7 months ending October 2026. Other timeframes beyond 5m/15m/1h/4h, other regimes, and other markets are untested.
- **Funding costs are excluded.** Including them would make the results worse, not better, so this does not threaten a negative conclusion — but the precise numbers would shift.
- **Fills are optimistic.** Limit orders fill on touch with no queue model. Same direction of bias.
- **Both venues' symbol lists were capped at the 100 most active pairs.** Less liquid perps were not tested. Their real spreads and slippage would exceed the 2 bps assumed here, so including them would likely worsen the aggregate.
- **Drawdown scales with position size.** The 10% DD criterion is the one screening rule that is a function of sizing rather than of the signal. A reader who rejects that criterion should note that the conclusion does not depend on it: **at full data depth only one pair of 132 reached PF 1.25, and it failed the time-stability test.**
- **Per-pair figures come from reading the platform's Strategy Tester UI**, transcribed by hand into the tracker. Transcription was done immediately at measurement time, before any verdict was formed, but the figures are not machine-exported.

---

## Reproducing this

```bash
# 1. Parse the raw sweep tracker into a clean dataset
python scripts/parse_tracker.py raw/pair_sweep.md data/results.csv

# 2. Regenerate every figure in this README
python scripts/make_figures.py
```

Requires Python 3.11+ and matplotlib. Both scripts are deterministic — re-running them reproduces `data/results.csv` and the six SVGs exactly.

To re-run the backtests themselves you need an openmarket.xyz account, the strategy from [`strategy/`](strategy/), and the parameters listed above. [`docs/04-operational-notes.md`](docs/04-operational-notes.md) documents the platform behaviours that will otherwise cost you hours — including the one that can silently produce wrong numbers.

---

## Repository layout

```
├── README.md                      this report
├── README.id.md                   Bahasa Indonesia version
├── data/
│   └── results.csv                all 138 rows, machine-readable
├── figures/                       six SVGs, generated from data/
├── scripts/
│   ├── parse_tracker.py           raw tracker  → results.csv
│   └── make_figures.py            results.csv  → figures/
├── strategy/
│   ├── hype_scalp_v4_maker.ts     the strategy under test
│   └── hype_scalp_v5_wide_r.ts    frozen config, marked NOT FOR LIVE USE
├── docs/
│   ├── 01-protocol.md             the pre-registered protocol, verbatim
│   ├── 02-tuning-phase.md         the 14-variant single-asset phase
│   ├── 03-case-studies.md         MINA and CYS in full
│   └── 04-operational-notes.md    platform pitfalls and how results were read
└── raw/
    ├── pair_sweep.md              the working tracker (Indonesian)
    └── backtest_log.md            the experiment log (Indonesian)
```

### Data dictionary — `data/results.csv`

| Column | Meaning |
|---|---|
| `id` | Position in the test queue. `B`-prefixed = batch 2. `—` = preliminary. |
| `batch` | `1` (Hyperliquid), `2` (Binance), or `preliminary` |
| `pair` | Ticker as listed by the venue |
| `venue` | `HYPERLIQUID.F` or `BINANCE.F` |
| `bars` | 1h bars loaded at the time of measurement |
| `trades` | Closed trades in the window |
| `win_rate_pct`, `net_pct`, `profit_factor`, `max_dd_pct`, `buy_hold_pct` | As reported by the Strategy Tester |
| `status` | `tested`, `tested_pf_unrecorded`, `untestable`, `duplicate` |

Only rows with `status == tested` and `batch in (1, 2)` are included in the 132. The others are retained so the file reconciles with the raw tracker by eye.

---

## Corrections

Kept visible rather than silently fixed, because a report about not fooling yourself should show its own errors.

- **Running PF averages in the raw Indonesian tracker were hand-maintained and drifted.** The tracker states a batch-1 mean of 0.911; recomputing from all 93 recorded values gives **0.9216**. Combined mean is **0.9192**, not the 0.912 stated mid-sweep. `data/results.csv` is authoritative; every figure in this README is computed from it.
- **A claim made mid-sweep that ">240 trades almost always means a sharply negative result" was wrong** and was retracted in the tracker at the time. Listing every pair above 280 trades gave 6 negative against 4 positive.
- **The count of pairs beating buy-and-hold was undercounted** in verbal summaries during the sweep (reported as 20 with 7 profitable). The correct figures from the dataset are **21 beating, 1 exact tie, 110 losing**, with **10** of the 21 profitable.

---

## Verdict

Stop developing this signal.

The evidence is not "no good configuration was found yet". It is four independent things pointing the same way: a profit-factor ceiling of 1.125 **at zero cost**, a 132-pair distribution centred below breakeven, seven-for-seven one-directional decay when samples were enlarged, and the two best candidates failing with identical time-instability on different venues.

The honest reading of 132 out-of-sample tests is that an EMA trend gate plus an ATR pullback — the most over-fitted signal family in retail crypto — contains no exploitable edge at these costs. Reducing cost drag by widening R, which is what the tuning phase achieved, makes the strategy lose more slowly. It does not make it win.

---

## License

Code and data in this repository are released under the [MIT License](LICENSE).

**This is research, not financial advice.** No configuration documented here passed its own acceptance criteria, and none should be traded.

# Case studies: the two candidates that reached the full protocol

Of 132 pairs, two cleared enough of the screen to justify the full protocol. **MINA** (Hyperliquid, batch 1) and **CYS** (Binance, batch 2). They were found weeks apart in the search order, on different venues, in completely unrelated assets.

They failed in the same way.

![MINA and CYS regime splits](../figures/fig3-regime-split.svg)

---

## MINA — HYPERLIQUID.F

### How it was found, and what nearly went wrong

MINA was first measured at **2,744 bars**: net +127.20%, **PF 1.368**, 247 trades. That was the highest profit factor seen in 65 pairs and comfortably above the 1.25 threshold.

The data-depth rule required deepening before recording. Deepened to **3,244 bars**: PF **1.293** — still passing. Deepened again during the split work to **3,994 bars**: PF **1.220** — now failing.

| Bars | Trades | Net % | PF | Max DD |
|---|---|---|---|---|
| 2,744 | 247 | +127.20% | **1.368** | 25.8% |
| 3,244 | 297 | +107.09% | **1.293** | 25.8% |
| **3,994** | **360** | **+86.43%** | **1.220** | **30.8%** |

Had the first reading been recorded and the pair moved on from, this report would contain a false discovery.

Full-window figures at 3,994 bars: GP/GL $47,884.9 / $39,242.3 · fees $1,903.8 · win rate 45.0% · Sharpe 2.23 · exposure 59.9% · Long +$2,116.9 (184 trades) / Short +$6,525.8 (176) · buy-and-hold +16.1%.

### The split

| Period | Trades | Net % | PF | Max DD | Long | Short |
|---|---|---|---|---|---|---|
| First half (≤ day 20677, ~98 days) | 184 | **−17.07%** | **0.897** | 25.8% | −$1,903.0 | +$196.0 |
| Second half (≥ day 20678, ~68 days) | 176 | **+124.80%** | **1.456** | 23.0% | +$4,847.3 | +$7,632.7 |

The strategy loses 17% over the first 98 days, then produces its entire result in the last 68.

**What this split does and does not measure.** No tuning was ever performed on MINA — the parameters came wholesale from a different asset on a different venue. Both halves are therefore out-of-sample. The split is not detecting parameter overfitting; it is detecting **instability across time**. The strategy is not stable.

### Verdict

Failed on three pre-registered counts: PF 1.220 < 1.25 at full depth, max drawdown 30.8% > 10%, and time-instability. Not advanced to stress test or parameter neighbours — the split had settled it.

---

## CYS — BINANCE.F

The strongest result in the project, and **the only pair of 132 whose profit factor stayed above the threshold once data was deepened**.

### Depth

| Bars | Trades | Net % | PF | Max DD |
|---|---|---|---|---|
| 2,758 | 279 | +652.18% | **1.370** | 18.4% |
| **4,508** | **473** | **+500.54%** | **1.300** | **18.4%** |

PF fell 0.070 — the same one-directional decay as every other candidate — but unlike the other six it landed *above* 1.25. Drawdown did not worsen.

Full-window figures at 4,508 bars: GP/GL $216,942.3 / $166,888.4 · fees $5,557.9 · win rate 44.8% · Sharpe 3.19 · exposure 55.2% · Long +$19,254.5 (225 trades) / Short +$30,799.4 (248) · buy-and-hold **−68.7%**.

### Cost stress test

Re-run at `maker_fee_pct 0.05` and `slippage_bps 5`:

| | Baseline | Stressed |
|---|---|---|
| Net | +500.54% | **+352.39%** |
| PF | 1.300 | **1.2503** |
| Max DD | 18.4% | 18.9% |
| Fees | $5,557.9 | $8,345.9 |

**It survives — by 0.0003.** Practically, that says the edge is about as thick as the uncertainty in the cost assumption itself. One more basis point of slippage and it fails.

### The split

| Period | Trades | Net % | PF | Long | Short |
|---|---|---|---|---|---|
| First half (≤ day 20652) | 231 | **−23.95%** | **0.918** | −$2,117.9 | −$276.7 |
| Second half (≥ day 20653) | 243 | **+677.10%** | **1.379** | +$27,656.0 | +$40,054.0 |

Loses 24% in the first half. Produces everything in the second.

### Why +500% means less than it looks

Three things inflate that headline, none of which are edge:

1. **Compounding.** `qtyType: percentOfEquity` means position size tracks equity. Largest win $4,978 and largest loss $4,754 against $10,000 of starting capital show that by the end of the window, single trades were moving roughly half the initial account. The final figure is dominated by the last trades, not by consistency across the window.
2. **The asset fell 68.7%.** Most of the profit is short-side (+$30,799 against +$19,255 long), concentrated in one collapse. That is one favourable regime, not a repeatable mechanism.
3. **The first half lost 24%.** Starting this on day one of available data means drawing down a quarter of the account over ~94 days before the profitable regime arrives — with nothing guaranteeing a next one.

### Verdict

Failed on two pre-registered counts: max drawdown 18.4% > 10%, and time-instability (first half PF 0.918). The stress test passed by 0.0003, which is not a margin anyone should trade on. Not advanced to parameter neighbours or largest-trade removal.

**Stated plainly:** CYS is the closest thing to a pass in 132 tests. If the drawdown criterion were dropped and the split ignored, it would look like a discovery. Neither should be dropped — a candidate like this is precisely why both were fixed in advance.

---

## Why two identical failures matter more than one

MINA and CYS have nothing in common. Different venues. Unrelated assets. Found in separate batches, with dozens of pairs tested between them. One rose into its profitable regime while the market was flat; the other profited from a 69% collapse.

Both show: **first half negative, entire result from the second half.**

One case like that is an anecdote — any strategy can catch a favourable stretch. Two, arrived at independently as the two best results from 132 out-of-sample tests, is a property of the strategy rather than of the assets. What this signal captures is **regime**, not edge. When trend conditions suit an EMA-pullback entry it makes money; when they do not it loses. Over a full window those average out to roughly breakeven minus costs — which is exactly what the 132-pair distribution shows, centred at PF 0.919.

---

## Honourable mention: PAXG

Not a candidate — it failed PF (1.158) and trade count (48) — but worth recording as the only qualitative hint in the dataset.

| | |
|---|---|
| Bars / trades | 2,994 / 48 |
| Net | +5.68% |
| PF | 1.158 |
| **Max drawdown** | **11.2%** — the lowest of any pair with a usable sample |
| Long / Short | +$167 / +$401 — both sides positive |
| Sharpe | +0.91 |
| Buy-and-hold | −3.8% (strategy beat it) |

PAXG is tokenised gold: low volatility, smooth trends, no overnight 40% collapses. It is the only instrument in the sweep where the strategy behaved the way its design intends — modest drawdown, both sides contributing, beating the asset.

It still did not pass, and 48 trades is far too small a sample to conclude anything. But if there is a direction worth exploring after this work, the hint points at **low-volatility, smoothly-trending instruments** rather than at more altcoins.

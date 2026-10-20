# The pre-registered protocol

This is the protocol as written into the sweep tracker **before the first pair was opened**, translated from the Indonesian original in [`raw/pair_sweep.md`](../raw/pair_sweep.md). Nothing in it was changed after results started arriving. One rule was *added* mid-sweep — the data-depth rule in §4 — and the circumstances of that addition are documented rather than hidden.

---

## 1. Why a protocol was needed at all

Testing 95 pairs and then keeping the best one **guarantees** a winner, whether or not an edge exists.

With 95 independent tests at a 5% chance of looking good by accident, the expected number of spurious "winners" is about **five**. A sweep without a pre-committed rule is not measuring edge — it is measuring how many instruments were searched.

This had already been demonstrated once before the sweep began. In the preliminary cross-pair check, **ZEC** returned **+20.22%**. Stopping there, the conclusion would have been "found one". But its profit factor was 1.053, its drawdown 23.9%, and buy-and-hold over the same window returned **+131.8%** — the strategy was riding a trend and losing to it by 112 percentage points.

## 2. Acceptance criteria

Assessed on the full window first, as a screen. A pair passes only if **every** condition holds:

| # | Criterion | Why |
|---|---|---|
| 1 | **Profit factor ≥ 1.25** | Raised from 1.2 as an explicit multiple-testing correction. Fixed before any data was seen. |
| 2 | **Max drawdown < 10%** | |
| 3 | **≥ 60 trades in the full window** | So that a half-sample split still leaves ≥ 30 per half. |
| 4 | **Net > 0 after costs** | |
| 5 | **Neither side bleeding** | The losing side must not exceed 50% of the winning side's profit. Guards against a result that is one directional bet in disguise. |
| 6 | **Beats buy-and-hold risk-adjusted** | `net% / maxDD` must exceed `B&H% / maxDD_B&H`. |

### Why profit factor is the primary criterion

Profit factor is **scale-invariant**: halving position size halves both gross profit and gross loss, leaving PF unchanged. Net % and drawdown both scale with sizing. For comparing a single configuration across 132 instruments of wildly different volatility, PF is the only one of the three that measures the signal rather than the bet size.

This is also why criterion 2 is the weakest link in the set, and it is flagged as such in the main report: a reader who rejects a drawdown threshold on sizing grounds should note that **the conclusion does not depend on it** — at full data depth only one pair of 132 reached PF 1.25 at all.

## 3. Standing rules

1. **Record every result**, not only the positive ones. The tracker table is filled in queue order with no exceptions and no deletions.
2. **Never re-tune per pair.** All 132 pairs use the configuration frozen at the end of the single-asset tuning phase. This is what makes each pair a genuine out-of-sample test.
3. **Judge PF and the comparison against buy-and-hold — not net %.** A high net % in a market that rose 130% is not a finding.
4. **Write the raw numbers down first, form the verdict second.** Transcribe what the tester reports, then decide what it means — never the reverse.

## 4. The data-depth rule (added at pair #11)

Added mid-sweep in response to a flaw that invalidated the comparability of everything measured before it.

**What happened.** DOGE read **+30.30% with PF 1.301** at 1,715 bars — clearing the threshold, beating buy-and-hold, both sides positive. Loading more history to 3,215 bars, the identical configuration read **−15.80% with PF 0.884**. Not weakened: reversed. SUI behaved the same way, falling 1.121 → 1.069 when deepened.

Bar counts had never been standardised, so pairs were not comparable with each other.

**The rule:**

> Minimum **2,900 bars**, and the bar count is recorded on every row.
>
> - A pair that **passes** the PF threshold at a sub-standard bar count **must be deepened before its result is recorded**.
> - A pair that **fails** is recorded as-is, with its bar count flagged `⚠`.

**Why the asymmetry.** Deepening a chart is slow, and a failing pair will not be rescued into a passing verdict by more data. A *passing* pair at a short window is exactly the case where noise is masquerading as signal — so that is where the expensive check is spent.

This rule caught **six false positives** (DOGE, kBONK, MINA, RLC, ZIL, MAGIC). Without it, this report would have announced six discoveries.

### Applying it more strictly than written

RLC (PF 1.2435) and MAGIC (PF 1.2428) each landed about **0.007 below** the threshold. The rule as written only required deepening for pairs that *passed*. Both were deepened anyway, because letting a rounding margin decide a verdict is exactly the self-deception the protocol exists to prevent. Both fell to 1.109.

## 5. Full protocol for anything that clears the screen

1. **Tuning / validation split.** Gate entries by UTC day using `start_day` / `end_day`, splitting the window at its midpoint. Both halves assessed on PF and net.
2. **Cost stress test.** Re-run at `maker_fee_pct 0.05` and `slippage_bps 5` — roughly 2.5× the assumed maker fee — to see whether the edge survives cost uncertainty.
3. **Parameter neighbours.** ±20% on the principal parameters; none may turn the result negative.
4. **Largest-trade removal.** The result must survive deleting the single biggest winner.

Two pairs reached this stage: **MINA** and **CYS**. Both failed at step 1. Details in [`03-case-studies.md`](03-case-studies.md).

## 6. Batch 2 addendum

The 39 Binance-only pairs were added after batch 1 finished, at the user's explicit request. Because they constitute a **new set of independent tests**, their multiple-testing burden was written down separately before the first one was opened:

> With 39 tests at a ~5% chance of looking good by accident, the expected number of spurious winners is **about 2**. Finding 1–2 pairs above PF 1.25 in this batch is therefore **the null expectation** — the outcome you would get if the strategy had no edge at all. It would not be a finding. A finding would be *more* than that, or one that survives the full protocol.

The threshold was **not** raised for batch 2. Moving a goalpost after seeing the first batch's results — in either direction — would invalidate the comparison between batches.

**Venue note:** batch 1 ran on `HYPERLIQUID.F`, batch 2 on `BINANCE.F`. A direct cross-check on STX, which trades on both, gave PF 1.193 (Binance) against 1.058 (Hyperliquid). Venue shifts the number by roughly 0.13, so the two batches' profit factors are reported separately as well as pooled, and neither batch's mean is presented as interchangeable with the other's.

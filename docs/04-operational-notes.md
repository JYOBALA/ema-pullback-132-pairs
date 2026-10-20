# Operational notes

How the 132 measurements were actually taken, and the platform behaviours that can silently corrupt a result. Recorded because a sweep of this size is mostly an exercise in not making the same mistake 132 times.

---

## The per-pair procedure

1. Collapse the Strategy Tester (the price pane must be tall, or the pan drag misses).
2. Open the symbol box, type the ticker, and **verify the venue row** before clicking.
3. Pan left ~10× to load history; record the bar count from the chart's `N bars · to <date>` chip.
4. Expand the tester, select the **v4** tab, open **Performance**.
5. Transcribe the raw numbers into the tracker, then form the verdict.

Roughly 3–4 minutes per pair when nothing goes wrong.

## The one that silently produces wrong numbers

**Settings changes do not apply while a strategy is paused — and the tester keeps displaying the previous run's figures.**

The chart auto-pauses indicators it considers slow (`FE_EXECUTION_PAUSED`, surfaced as a "Paused by the chart" chip in the legend). If a symbol is switched or a parameter edited while paused, the Performance tab still shows stale output. There is no error state. The numbers simply belong to a different run.

Every measurement in this sweep therefore ends with an explicit resume step: click the legend's error chip, then **Resume**, then wait for the recompute before reading anything.

A related failure: on one pair the v4 strategy stopped computing entirely (empty pane, no tester chip) while v3 was still attached and showing `+1.08% / 1 trade`. Without checking which strategy the tester was displaying, v3's result would have been recorded as that pair's result.

## Verify the symbol, every time

Two distinct ways to get the wrong instrument, both of which happened:

- **Wrong leveraged token.** Searching `WLD` via the command palette landed on GATE.IO `WLD5L_USDT` / `WLD5S_USDT` — 5× leveraged tokens, not the perp. Those readings were discarded, not recorded.
- **Compare mode instead of symbol switch.** A coordinate click added CHIP as an *overlay* on the existing chart rather than switching to it. Caught before any number was taken.

The guard used for the rest of the sweep: after switching, read the symbol back programmatically and confirm it reports the expected `VENUE | TICKER` before touching the tester.

Also note that several tickers collide with equities — `QNT`, `A`, `WAL`, `DASH`, `OGN`, `CT` all return a stock as the first search hit. The crypto row must be selected explicitly.

## Venue filter resets

The symbol panel's saved-view filter (Hyperliquid / All / …) resets to **All** on some searches. When it does, the first venue row is whatever the platform ranks highest — not necessarily the venue being swept. Batch 2 had to re-assert the filter, or pick the `BINANCE.F PERP` row by position, on every pair.

## Data depth "follows chart"

The tester only evaluates bars that are loaded into the chart, so history must be panned in before reading. Two consequences:

- **Bar count is part of the result** and is recorded on every row. A PF without a bar count is not interpretable — see [`01-protocol.md §4`](01-protocol.md).
- **Depth can grow mid-session.** During the MINA split the window expanded from 3,244 to 3,994 bars between runs, which invalidated the comparison in progress. The full window had to be re-measured at the new depth so that both halves and the whole were on one dataset.

## Re-attaching the strategy resets nothing — but check anyway

After a browser restart the strategy had to be re-attached via the editor's Run button. Parameter overrides turned out to persist in the workspace, so the frozen configuration survived. That was verified rather than assumed: all four key parameters (`min_risk_pct 1.5`, `max_hold 96`, `be_trigger_r 8`, `start_day 0` / `end_day 100000`) were read back from the settings panel before any further measurement.

Had they silently reverted to the source defaults (`min_risk_pct 0.3`, `max_hold 24`, `be_trigger_r 1.0`), the subsequent pairs would have been measured with a different strategy and entered into the same table.

## Always restore after a split or stress test

`start_day` / `end_day` gating and the stressed cost settings are global to the strategy, not scoped to one pair. Both were restored and re-verified immediately after each case study, because leaving `start_day` at a mid-window value would have quietly truncated every subsequent pair's window.

## Browser automation specifics

For anyone reproducing this with automated browsing rather than by hand:

- **Focus inputs by reference, not coordinates.** `ctrl+a` with no focused input selects the whole page.
- **Layout shifts ~32 px** when the "Paused, not applied to the chart" bar appears, invalidating cached coordinates. A slippage value was once left at 2 instead of 5 because of this.
- **Numeric settings fields are not `<input>` elements** until clicked — they are custom spinners. A triple-click turns one into an editable field; only then does typing work.
- **Legend icons shift position** as text truncates, so the detach `×` and the settings gear swap places between states. Use the Strategy Tester's own gear, which has no detach control near it.
- **The renderer can freeze** on heavy charts (several thousand bars with two strategies attached). Recovery is reopening the tab; the chart returns with a small range and must be re-panned.

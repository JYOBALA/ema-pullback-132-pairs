#!/usr/bin/env python3
"""
Parse the raw Indonesian-language sweep tracker (pair_sweep.md) into a clean CSV.

The tracker is the primary record: every pair tested was written into it at the
moment it was measured, before any verdict was formed. This script does nothing
but transcribe it — no filtering, no rounding, no reinterpretation. Rows the
tracker marks as untestable or duplicate are carried through with a status flag
rather than dropped, so the CSV row count reconciles with the tracker by eye.

Indonesian number format: "1.234,56" means 1234.56 (dot = thousands, comma =
decimal). Percentages use U+2212 MINUS SIGN, not ASCII hyphen.

Usage:
    python scripts/parse_tracker.py ../strategies/pair_sweep.md data/results.csv
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

# Rows look like: | 65 | **MINA** | **3.994** | 360 | 45,0% | **+86,43%** | ... |
ROW = re.compile(r"^\|\s*(B?\d+|—)\s*\|(.+)\|\s*$")

# Batch 1 ran on Hyperliquid perps, batch 2 on Binance perps. The five
# preliminary pairs predate the numbered queues and ran on Binance.
PRELIMINARY = {"HYPE", "BTC", "ETH", "SOL", "ZEC"}


def clean(cell: str) -> str:
    """Strip markdown emphasis, strikethrough and footnote marks from a cell."""
    cell = cell.replace("**", "").replace("~~", "")
    cell = cell.replace("⚠", "").replace("⬜", "").replace("❌", "").replace("✓", "")
    return cell.strip()


def num(cell: str) -> float | None:
    """Indonesian decimal -> float. Returns None for '—' and other blanks."""
    cell = clean(cell).replace("%", "").replace("~", "").strip()
    if cell in {"", "—", "-"}:
        return None
    # U+2212 minus sign and en-dash both appear in the tracker.
    cell = cell.replace("−", "-").replace("–", "-")
    # 1.234,56 -> 1234.56
    cell = cell.replace(".", "").replace(",", ".")
    try:
        return float(cell)
    except ValueError:
        return None


def parse(md_path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        idx = m.group(1).strip()
        cells = [c for c in m.group(2).split("|")]
        if len(cells) < 9:
            continue

        pair = clean(cells[0])
        # Drop parenthetical glosses: "A (Vaulta)" -> "A"
        pair_key = re.sub(r"\s*\(.*\)$", "", pair).strip()
        if not pair_key:
            continue

        bars = num(cells[1])
        trades = num(cells[2])
        win = num(cells[3])
        net = num(cells[4])
        pf = num(cells[5])
        dd = num(cells[6])
        bh = num(cells[7])
        note = clean(cells[8]) if len(cells) > 8 else ""

        # Classify the row.
        if idx == "—":
            batch, venue = "preliminary", "BINANCE.F"
        elif idx.startswith("B"):
            batch, venue = "2", "BINANCE.F"
        else:
            batch, venue = "1", "HYPERLIQUID.F"

        if "DUPLIKAT" in note.upper():
            status = "duplicate"
        elif trades in (None, 0):
            # No trades fired — the venue had too little history to test at all.
            status = "untestable"
        elif pf is None:
            # Ran, but profit factor was not written down. Two of the five
            # preliminary pairs are like this; they are excluded from PF
            # statistics but kept so the record stays complete.
            status = "tested_pf_unrecorded"
        else:
            status = "tested"

        rows.append(
            {
                "id": idx,
                "batch": batch,
                "pair": pair_key,
                "venue": venue,
                "bars": int(bars) if bars else "",
                "trades": int(trades) if trades else "",
                "win_rate_pct": win if win is not None else "",
                "net_pct": net if net is not None else "",
                "profit_factor": pf if pf is not None else "",
                "max_dd_pct": dd if dd is not None else "",
                "buy_hold_pct": bh if bh is not None else "",
                "status": status,
            }
        )
    return rows


def main() -> int:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "../strategies/pair_sweep.md")
    dst = Path(sys.argv[2] if len(sys.argv) > 2 else "data/results.csv")

    rows = parse(src)
    # Deduplicate: the tracker repeats a handful of pairs inside running-stat
    # recap tables. The numbered queue rows are authoritative, so keep the first
    # occurrence of each (batch, pair) and discard later restatements.
    seen: set[tuple[str, str]] = set()
    unique = []
    for r in rows:
        key = (r["batch"], r["pair"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(unique[0].keys()))
        w.writeheader()
        w.writerows(unique)

    tested = [r for r in unique if r["status"] == "tested"]
    by_batch: dict[str, int] = {}
    for r in tested:
        by_batch[r["batch"]] = by_batch.get(r["batch"], 0) + 1

    print(f"wrote {dst} — {len(unique)} rows, {len(tested)} tested")
    for b in sorted(by_batch):
        print(f"  batch {b}: {by_batch[b]} tested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Generate every figure in the README from data/results.csv and the hand-entered
constants below. Re-running this script reproduces the figures byte-for-byte
(matplotlib SVG output is deterministic once the hash seed is fixed).

    python scripts/make_figures.py

Design notes: figures use a light background so they stay legible in GitHub's
dark mode as well as light. The palette is deliberately flat — one accent for
the thing being argued, grey for everything else — because most of these charts
make a point about a *distribution*, not about individual pairs.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

# Deterministic SVG ids so re-runs produce identical files.
os.environ.setdefault("SOURCE_DATE_EPOCH", "1760918400")
matplotlib.rcParams["svg.hashsalt"] = "hype-scalp-research"

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

INK = "#1b1f24"
MUTED = "#6b7280"
GRID = "#e5e7eb"
FAIL = "#9aa3ae"
ACCENT = "#c2410c"      # the argument
ACCENT2 = "#1d4ed8"     # the comparison
GOOD = "#15803d"
WARN = "#b45309"

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.edgecolor": "#c9ced6",
        "axes.labelcolor": INK,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "legend.frameon": False,
        "figure.dpi": 110,
    }
)

PF_THRESHOLD = 1.25
BREAKEVEN = 1.0


# ---------------------------------------------------------------- data loading
def load() -> list[dict]:
    with (ROOT / "data" / "results.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        if r["status"] != "tested" or r["batch"] not in ("1", "2"):
            continue
        out.append(
            {
                "pair": r["pair"],
                "batch": r["batch"],
                "bars": int(r["bars"]),
                "trades": int(r["trades"]),
                "net": float(r["net_pct"]),
                "pf": float(r["profit_factor"]),
                "dd": float(r["max_dd_pct"]),
                "bh": float(r["buy_hold_pct"]) if r["buy_hold_pct"] else None,
            }
        )
    return out


def finish(fig, name: str, caption: str | None = None, caption_y: float = -0.035) -> None:
    # The caption sits *below* the figure box (negative y in figure coords).
    # bbox_inches="tight" grows the canvas to include it, so it never collides
    # with the x-axis label the way an inside-the-axes caption does. Figures
    # that park their legend under the axes pass a lower caption_y.
    if caption:
        fig.text(0.0, caption_y, caption, fontsize=8, color=MUTED, va="top", ha="left")
    fig.savefig(FIG / name, format="svg", bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print(f"  figures/{name}")


def spread(values: list[float], min_gap: float) -> list[float]:
    """Nudge near-identical label positions apart, preserving their order.

    Several pairs land within 0.01 PF of each other, which makes their text
    labels overlap into mush. This walks them bottom-up and pushes any label
    that is too close to its neighbour, then recentres the whole run so the
    group stays visually anchored to the data.
    """
    out = list(values)
    order = sorted(range(len(values)), key=lambda i: values[i])
    for k in range(1, len(order)):
        prev, cur = order[k - 1], order[k]
        if out[cur] - out[prev] < min_gap:
            out[cur] = out[prev] + min_gap
    shift = (sum(values) - sum(out)) / len(values)
    return [v + shift for v in out]


# ------------------------------------------------------- fig 1: PF distribution
def fig_pf_distribution(rows: list[dict]) -> None:
    pf = sorted(r["pf"] for r in rows)
    mean = sum(pf) / len(pf)

    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    bins = [0.50 + 0.05 * i for i in range(19)]
    n, _, patches = ax.hist(pf, bins=bins, color=FAIL, edgecolor="white", linewidth=1.1)

    # Colour the bars that clear breakeven, and the one that clears threshold.
    for patch, left in zip(patches, bins[:-1]):
        if left >= PF_THRESHOLD:
            patch.set_facecolor(ACCENT)
        elif left >= BREAKEVEN:
            patch.set_facecolor("#c8ccd2")

    ax.axvline(BREAKEVEN, color=INK, lw=1.4, ls="-")
    ax.axvline(mean, color=ACCENT2, lw=1.6, ls="--")
    ax.axvline(PF_THRESHOLD, color=ACCENT, lw=1.6, ls=":")

    top = max(n)
    ax.annotate(
        f"mean {mean:.3f}",
        xy=(mean, top * 0.97),
        xytext=(mean - 0.175, top * 0.97),
        color=ACCENT2,
        fontsize=9.5,
        fontweight="bold",
        ha="right",
        va="top",
    )
    ax.annotate(
        "breakeven 1.00",
        xy=(BREAKEVEN, top * 0.62),
        xytext=(BREAKEVEN + 0.018, top * 0.62),
        color=INK,
        fontsize=9,
        va="top",
    )
    ax.annotate(
        "pass threshold 1.25\n1 of 132 pairs",
        xy=(PF_THRESHOLD, top * 0.40),
        xytext=(PF_THRESHOLD + 0.02, top * 0.40),
        color=ACCENT,
        fontsize=9,
        fontweight="bold",
        va="top",
    )

    ax.set_xlabel("Profit factor (gross profit / gross loss)")
    ax.set_ylabel("Number of pairs")
    ax.set_title("Profit factor across 132 perpetual-futures pairs")
    ax.set_xlim(0.50, 1.42)
    ax.margins(y=0.12)

    finish(
        fig,
        "fig1-pf-distribution.svg",
        "One strategy, one fixed parameter set, 132 pairs on 1h bars. Costs: maker 0.02% / taker 0.045% / 2 bps slippage.",
    )


# ------------------------------------------------------------ fig 2: depth decay
DECAY = [
    # pair,   shallow_bars, shallow_pf, deep_bars, deep_pf
    ("DOGE", 1715, 1.301, 3215, 0.884),
    ("kBONK", 1995, 1.253, 3495, 0.992),
    ("MAGIC", 2757, 1.2428, 4507, 1.109),
    ("RLC", 2757, 1.2435, 4257, 1.109),
    ("ZIL", 2507, 1.2065, 4007, 1.140),
    ("MINA", 2744, 1.368, 3994, 1.220),
    ("CYS", 2758, 1.370, 4508, 1.300),
]


def fig_depth_decay() -> None:
    fig, ax = plt.subplots(figsize=(9.4, 5.4))

    left_y = spread([d[2] for d in DECAY], 0.030)
    right_y = spread([d[4] for d in DECAY], 0.030)

    for (pair, sb, spf, db, dpf), ly, ry in zip(DECAY, left_y, right_y):
        landed_above = dpf >= PF_THRESHOLD
        colour = ACCENT if landed_above else FAIL
        weight = "bold" if landed_above else "normal"
        ax.plot([0, 1], [spf, dpf], color=colour, lw=2.6 if landed_above else 1.6,
                zorder=4 if landed_above else 2, solid_capstyle="round")
        ax.scatter([0, 1], [spf, dpf], color=colour, s=36,
                   zorder=5 if landed_above else 3)
        # Leader line from the nudged label back to the true data point.
        ax.plot([-0.045, -0.012], [ly, spf], color=colour, lw=0.7, alpha=0.55, zorder=1)
        ax.plot([1.012, 1.045], [dpf, ry], color=colour, lw=0.7, alpha=0.55, zorder=1)
        ax.text(-0.055, ly, f"{pair}  {spf:.3f}", ha="right", va="center",
                fontsize=9.5, color=colour, fontweight=weight)
        ax.text(1.055, ry, f"{dpf:.3f}   {db:,} bars", ha="left", va="center",
                fontsize=9.5, color=colour, fontweight=weight)

    ax.axhline(PF_THRESHOLD, color=ACCENT, lw=1.4, ls=":", zorder=1)
    ax.text(0.72, PF_THRESHOLD + 0.010, "pass threshold 1.25", ha="left",
            fontsize=9, color=ACCENT, fontweight="bold")
    ax.axhline(BREAKEVEN, color=INK, lw=1.2, zorder=1)
    ax.text(0.30, BREAKEVEN + 0.010, "breakeven", ha="left", fontsize=9, color=INK)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["shallow window\n(as first measured)", "deepened window\n(history extended)"])
    ax.set_xlim(-0.46, 1.52)
    ax.set_ylim(0.84, 1.45)
    ax.set_ylabel("Profit factor")
    ax.set_title("Every pair that looked promising decayed when more history was loaded")
    ax.grid(axis="x", visible=False)

    finish(
        fig,
        "fig2-depth-decay.svg",
        "7 of 7 moved down; 0 moved up. A correct estimate would scatter in both directions as the sample grows.",
    )


# ----------------------------------------------------------- fig 3: regime split
SPLITS = {
    "MINA": {"venue": "HYPERLIQUID.F", "first": (-17.07, 0.897, 184), "second": (124.80, 1.456, 176), "full": (86.43, 1.220, 360)},
    "CYS": {"venue": "BINANCE.F", "first": (-23.95, 0.918, 231), "second": (677.10, 1.379, 243), "full": (500.54, 1.300, 473)},
}


def fig_regime_split() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4))

    for ax, (pair, d) in zip(axes, SPLITS.items()):
        labels = ["first half", "second half", "full window"]
        pfs = [d["first"][1], d["second"][1], d["full"][1]]
        nets = [d["first"][0], d["second"][0], d["full"][0]]
        trades = [d["first"][2], d["second"][2], d["full"][2]]
        colours = [ACCENT, GOOD, MUTED]

        bars = ax.bar(labels, pfs, color=colours, width=0.6, zorder=3)
        ax.axhline(BREAKEVEN, color=INK, lw=1.3, zorder=4)
        ax.axhline(PF_THRESHOLD, color=ACCENT, lw=1.2, ls=":", zorder=4)

        for b, pf, net, tr in zip(bars, pfs, nets, trades):
            # Lift the value label clear of the dotted 1.25 line when a bar
            # happens to top out right next to it (MINA's full window does).
            offset = 0.048 if abs(pf - PF_THRESHOLD) < 0.05 else 0.022
            ax.text(b.get_x() + b.get_width() / 2, pf + offset,
                    f"PF {pf:.3f}", ha="center", fontsize=9.5, fontweight="bold",
                    zorder=6)
            ax.text(b.get_x() + b.get_width() / 2, pf - 0.055,
                    f"{net:+.2f}%\n{tr} trades", ha="center", fontsize=8.5,
                    color="white", va="top", zorder=6)

        ax.set_ylim(0, 1.66)
        ax.set_title(f"{pair}  ·  {d['venue']}")
        ax.set_ylabel("Profit factor" if pair == "MINA" else "")
        ax.grid(axis="x", visible=False)

    fig.suptitle("The two best candidates from 132 failed in exactly the same way",
                 fontsize=12.5, fontweight="bold", y=1.0)
    fig.tight_layout()
    finish(
        fig,
        "fig3-regime-split.svg",
        "Unrelated assets on different venues. In both, the first half loses and the whole result comes from the second.",
    )


# --------------------------------------------------- fig 4: strategy vs buy&hold
def fig_vs_buyhold(rows: list[dict]) -> None:
    pts = [r for r in rows if r["bh"] is not None]
    fig, ax = plt.subplots(figsize=(8.0, 6.4))

    lim_lo, lim_hi = -110, 420
    ax.fill_between([lim_lo, lim_hi], [lim_lo, lim_hi], lim_hi,
                    color="#eef2f7", zorder=0)
    ax.plot([lim_lo, lim_hi], [lim_lo, lim_hi], color=MUTED, lw=1.2, ls="--", zorder=2)
    ax.axhline(0, color=INK, lw=1.0, zorder=2)
    ax.axvline(0, color=INK, lw=1.0, zorder=2)

    for r in pts:
        clipped = r["bh"] > lim_hi or r["net"] > lim_hi
        x = min(r["bh"], lim_hi - 6)
        y = min(r["net"], lim_hi - 6)
        beat = r["net"] > r["bh"]
        profit = r["net"] > 0
        if beat and profit:
            c, s, z = ACCENT, 46, 6
        elif beat:
            c, s, z = "#f0b27a", 30, 5
        else:
            c, s, z = FAIL, 20, 3
        ax.scatter(x, y, color=c, s=s, zorder=z, edgecolor="white",
                   linewidth=0.6, marker="^" if clipped else "o")

    # Labels for the points worth naming. Clipped points sit on the axis edge,
    # so their labels are offset inward to stay inside the plot area.
    label_offsets = {
        "CYS": (10, -14), "AKE": (-10, 10), "BTW": (-10, 12),
        "MINA": (9, 5), "PAXG": (9, -12), "Q": (-10, -4),
    }
    for name, off in label_offsets.items():
        r = next((p for p in pts if p["pair"] == name), None)
        if not r:
            continue
        x = min(r["bh"], lim_hi - 6)
        y = min(r["net"], lim_hi - 6)
        ax.annotate(name, (x, y), textcoords="offset points", xytext=off,
                    fontsize=9, fontweight="bold", color=INK,
                    ha="right" if off[0] < 0 else "left")

    ax.text(lim_hi - 14, lim_hi - 26, "strategy beats\nbuy-and-hold",
            ha="right", va="top", fontsize=9.5, color=MUTED, style="italic")
    ax.text(170, -88, "buy-and-hold wins  ·  110 of 132 pairs",
            ha="center", va="bottom", fontsize=9.5, color=MUTED, style="italic")

    ax.set_xlim(lim_lo, lim_hi)
    ax.set_ylim(lim_lo, lim_hi)
    ax.set_xlabel("Buy-and-hold return over the same window (%)")
    ax.set_ylabel("Strategy net return after costs (%)")
    ax.set_title("Strategy return vs simply holding the asset")

    # The legend lives under the axes: the upper-left corner of this plot is
    # where CYS lands once clipped, and the two would overlap in-axes.
    ax.legend(
        handles=[
            Line2D([], [], marker="o", ls="", color=ACCENT, markersize=8,
                   label="beat B&H and made money (10)"),
            Line2D([], [], marker="o", ls="", color="#f0b27a", markersize=7,
                   label="beat B&H but still lost money (11)"),
            Line2D([], [], marker="o", ls="", color=FAIL, markersize=6,
                   label="lost to B&H (110)"),
            Line2D([], [], marker="^", ls="", color=MUTED, markersize=7,
                   label="clipped at axis limit"),
        ],
        loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=2, fontsize=9,
    )

    finish(
        fig,
        "fig4-vs-buyhold.svg",
        "Axes clipped at +420% — AKE (B&H +8,226%), BTW (+3,114%) and CYS (net +501%) sit beyond it, marked as triangles.",
        caption_y=-0.20,
    )


# -------------------------------------------------------------- fig 5: DD vs PF
def fig_dd_vs_pf(rows: list[dict]) -> None:
    fig, ax = plt.subplots(figsize=(8.6, 5.4))

    # The pass box: PF >= 1.25 AND DD < 10%. The y-axis is inverted further
    # down, so "below the box" in data terms means a larger drawdown value.
    ax.add_patch(Rectangle((PF_THRESHOLD, 0), 0.30, 10, facecolor="#dcfce7",
                           edgecolor=GOOD, lw=1.3, zorder=1))
    ax.text(PF_THRESHOLD + 0.015, 5.0, "pass region\nPF ≥ 1.25,  DD < 10%",
            fontsize=8.5, color=GOOD, fontweight="bold", va="center", zorder=5)

    for r in rows:
        big = r["trades"] >= 60
        ax.scatter(r["pf"], r["dd"],
                   s=26 if big else 13,
                   color=ACCENT if r["pf"] >= PF_THRESHOLD else FAIL,
                   alpha=0.95 if big else 0.55,
                   edgecolor="white", linewidth=0.5, zorder=4)

    # Two Binance tickers are CJK; DejaVu Sans has no glyphs for them, so the
    # chart uses the romanised name the exchange lists alongside the symbol.
    romanised = {"龙虾": "Lobster", "牛来": "Niulai"}
    dd_offsets = {"CYS": (9, 0), "MINA": (9, 0), "PAXG": (-9, 0),
                  "ASTER": (9, 0), "龙虾": (9, 4), "Q": (9, -6)}
    for name, off in dd_offsets.items():
        r = next((p for p in rows if p["pair"] == name), None)
        if not r:
            continue
        ax.annotate(romanised.get(name, name), (r["pf"], r["dd"]),
                    textcoords="offset points", xytext=off,
                    fontsize=9, fontweight="bold", color=INK, zorder=6,
                    va="center", ha="right" if off[0] < 0 else "left")

    ax.axvline(PF_THRESHOLD, color=ACCENT, lw=1.3, ls=":", zorder=3)
    ax.axhline(10, color=GOOD, lw=1.3, ls=":", zorder=3)
    ax.axvline(BREAKEVEN, color=INK, lw=1.1, zorder=3)

    ax.set_xlabel("Profit factor")
    ax.set_ylabel("Maximum drawdown (%)")
    ax.set_title("No pair landed in the pass region")
    ax.set_xlim(0.52, 1.40)
    ax.set_ylim(0, 97)
    ax.invert_yaxis()

    ax.legend(
        handles=[
            Line2D([], [], marker="o", ls="", color=FAIL, markersize=7, label="≥ 60 trades"),
            Line2D([], [], marker="o", ls="", color=FAIL, markersize=5, alpha=0.55,
                   label="< 60 trades (sample too small to screen)"),
        ],
        loc="lower right", fontsize=9,
    )

    finish(
        fig,
        "fig5-dd-vs-pf.svg",
        "Drawdown axis inverted so better outcomes sit higher. ASTER is the only pair under 10% DD and it fired just 25 trades.",
    )


# --------------------------------------------------------- fig 6: screening funnel
def fig_funnel(rows: list[dict]) -> None:
    n_total = len(rows)
    n_trades = sum(1 for r in rows if r["trades"] >= 60)
    n_net = sum(1 for r in rows if r["trades"] >= 60 and r["net"] > 0)
    n_pf = sum(1 for r in rows if r["trades"] >= 60 and r["net"] > 0 and r["pf"] >= PF_THRESHOLD)
    n_dd = sum(1 for r in rows if r["trades"] >= 60 and r["net"] > 0
               and r["pf"] >= PF_THRESHOLD and r["dd"] < 10)

    stages = [
        ("Pairs tested", n_total),
        ("≥ 60 trades", n_trades),
        ("Net positive after costs", n_net),
        ("Profit factor ≥ 1.25", n_pf),
        ("Max drawdown < 10%", n_dd),
    ]

    fig, ax = plt.subplots(figsize=(9.0, 4.2))
    ys = range(len(stages))
    vals = [s[1] for s in stages]
    colours = [FAIL] * (len(stages) - 2) + [ACCENT, "#b91c1c"]

    ax.barh(list(ys), vals, color=colours, height=0.62, zorder=3)
    for y, (label, v) in zip(ys, stages):
        ax.text(v + 1.6, y, str(v), va="center", fontsize=11, fontweight="bold", color=INK)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([s[0] for s in stages], fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, n_total + 14)
    ax.set_xlabel("Pairs remaining")
    ax.set_title("Pre-registered screen, applied in order")
    ax.grid(axis="y", visible=False)

    finish(
        fig,
        "fig6-screening-funnel.svg",
        "The two criteria that also had to hold — both sides non-bleeding, and beating buy-and-hold risk-adjusted — never became binding.",
    )


def main() -> int:
    rows = load()
    print(f"loaded {len(rows)} tested pairs")
    fig_pf_distribution(rows)
    fig_depth_decay()
    fig_regime_split()
    fig_vs_buyhold(rows)
    fig_dd_vs_pf(rows)
    fig_funnel(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

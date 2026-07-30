#!/usr/bin/env python3
"""Regenerate the recap deck's best-observed throughput chart."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DEFAULT_OUTPUT = Path(__file__).resolve().parent / "performance_comparison.png"

CATEGORIES = [
    "Quectel 5G F1\nbackhaul",
    "Wi-Fi GRE\nF1 backhaul",
    "Tuned Ethernet\nCU/DU split",
    "Monolithic\nreference",
]
THROUGHPUT = [78.0, 52.0, 100.0, 190.0]
COLORS = ["#f43f5e", "#a855f7", "#3b82f6", "#10b981"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"output PNG path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "figure.facecolor": "#0b0f19",
            "axes.facecolor": "#0f172a",
            "text.color": "#f8fafc",
            "axes.labelcolor": "#94a3b8",
            "xtick.color": "#94a3b8",
            "ytick.color": "#94a3b8",
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "DejaVu Sans", "Arial"],
        }
    )

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    bars = ax.barh(
        CATEGORIES,
        THROUGHPUT,
        color=COLORS,
        height=0.6,
        edgecolor="none",
    )

    ax.set_title(
        "Best-observed throughput by configuration",
        fontsize=14,
        fontweight="bold",
        pad=20,
        color="#f8fafc",
    )
    ax.set_xlabel("User throughput (Mbps)", fontsize=11, labelpad=10)
    ax.xaxis.grid(True, linestyle="--", alpha=0.15, color="#e2e8f0")
    ax.set_axisbelow(True)

    for spine in ("top", "right", "left", "bottom"):
        ax.spines[spine].set_visible(False)

    for bar, value in zip(bars, THROUGHPUT):
        ax.text(
            value + 3,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.0f} Mbps",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
            color="#f8fafc",
        )

    ax.set_xlim(0, 220)
    fig.text(
        0.5,
        0.01,
        "Different hosts/runs; best observations, not controlled averages",
        ha="center",
        fontsize=8,
        color="#94a3b8",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(
        output,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        edgecolor="none",
    )
    plt.close(fig)
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()

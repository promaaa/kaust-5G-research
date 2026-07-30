#!/usr/bin/env python3
"""Render best-observed throughput charts used by the public documentation.

The values are best observations from different runs and hosts, not controlled
averages. Reports 18–22 provide the experiment narrative. The 78 Mbps Quectel
value is a researcher-confirmed 19 July 2026 result that still needs a repeated,
public evidence bundle.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


CONFIGS = [
    "Monolithic\nOAI reference",
    "Ethernet CU/DU\nwith SIB8",
    "Wi-Fi CU/DU\nwith SIB8",
    "Quectel 5G F1\nbackhaul",
]
COLORS = ["#2ecc71", "#3498db", "#9b59b6", "#e74c3c"]

CURRENT_BEST = [190, 100, 52, 78]
PREVIOUS_BEST = [150, 23, 12, 50]

DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parents[1] / "docs" / "Presentation" / "img"
)


def style_axis(ax: plt.Axes, title: str) -> None:
    ax.set_ylabel("Throughput (Mbps)", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylim(0, 220)
    ax.set_yticks(np.arange(0, 221, 20))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=10)


def add_labels(ax: plt.Axes, bars, values: list[int]) -> None:
    for bar, value in zip(bars, values):
        ax.annotate(
            f"{value} Mbps",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )


def render_updated_chart(output_dir: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        CONFIGS,
        CURRENT_BEST,
        color=COLORS,
        edgecolor="white",
        linewidth=1.5,
    )
    add_labels(ax, bars, CURRENT_BEST)
    style_axis(ax, "Best Observed Throughput by Configuration")
    fig.text(
        0.5,
        0.01,
        "Best observations across different hosts/runs; not controlled averages",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    output = output_dir / "throughput_chart_best.png"
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output


def render_side_by_side(output_dir: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    x = np.arange(len(CONFIGS))

    previous_bars = axes[0].bar(
        x,
        PREVIOUS_BEST,
        color=COLORS,
        edgecolor="white",
        linewidth=1.5,
    )
    current_bars = axes[1].bar(
        x,
        CURRENT_BEST,
        color=COLORS,
        edgecolor="white",
        linewidth=1.5,
    )

    for ax in axes:
        ax.set_xticks(x, CONFIGS)
    add_labels(axes[0], previous_bars, PREVIOUS_BEST)
    add_labels(axes[1], current_bars, CURRENT_BEST)
    style_axis(axes[0], "Earlier Best Observed")
    style_axis(axes[1], "Current Best Observed")
    axes[1].set_ylabel("")

    fig.suptitle(
        "Throughput Improvements Across Shared Configurations",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.01,
        "Best observations across different hosts/runs; not controlled averages",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))

    output = output_dir / "throughput_improvements_side_by_side.png"
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"chart output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for chart in (
        render_updated_chart(output_dir),
        render_side_by_side(output_dir),
    ):
        print(f"Saved: {chart}")


if __name__ == "__main__":
    main()


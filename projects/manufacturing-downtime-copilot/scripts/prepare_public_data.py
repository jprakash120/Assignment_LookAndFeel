"""Create an anonymized public dataset and a reproducible portfolio preview."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def prepare(input_path: Path, output_path: Path, preview_path: Path) -> None:
    df = pd.read_csv(input_path, encoding="utf-8-sig")
    operator_column = "Operator"
    mapping = {
        name: f"Operator {chr(65 + index)}"
        for index, name in enumerate(sorted(df[operator_column].dropna().astype(str).unique()))
    }
    df[operator_column] = df[operator_column].map(mapping)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    minutes_column = "Sum of Downtime_Minutes"
    reasons = df.groupby("Description")[minutes_column].sum().sort_values().tail(8)
    products = df.groupby("Product")[minutes_column].sum().sort_values(ascending=False)
    shifts = df.groupby("Shift")[minutes_column].sum().sort_values(ascending=False)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig = plt.figure(figsize=(16, 9), facecolor="#07111f")
    grid = fig.add_gridspec(12, 24, left=.12, right=.97, top=.90, bottom=.08, wspace=2.2, hspace=2.0)
    fig.text(.055, .955, "Manufacturing Downtime Intelligence", color="#edf5ff", fontsize=24, fontweight="bold")
    fig.text(.055, .915, "Verified portfolio dataset · 61 events · 35 affected batches", color="#8fa4bd", fontsize=11)

    total = int(df[minutes_column].sum())
    kpis = [
        ("TOTAL DOWNTIME", f"{total:,}", "minutes"),
        ("TOP REASON", reasons.index[-1], f"{int(reasons.iloc[-1]):,} minutes"),
        ("LARGEST PRODUCT", products.index[0], f"{int(products.iloc[0]):,} minutes"),
        ("OPERATOR SHARE", f"{df.loc[df['Operator Error'].eq('Yes'), minutes_column].sum() / total:.0%}", "of downtime"),
    ]
    for index, (label, value, note) in enumerate(kpis):
        ax = fig.add_subplot(grid[0:3, index * 6:(index + 1) * 6])
        ax.set_facecolor("#102238")
        ax.text(.06, .78, label, color="#69d8c7", fontsize=9, fontweight="bold", transform=ax.transAxes)
        ax.text(.06, .41, value, color="#f3f7fc", fontsize=19, fontweight="bold", transform=ax.transAxes)
        ax.text(.06, .15, note, color="#92a5ba", fontsize=9, transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values(): spine.set_visible(False)

    ax1 = fig.add_subplot(grid[4:12, 0:14])
    ax1.set_facecolor("#102238")
    ax1.barh(reasons.index, reasons.values, color="#36c6b3", height=.56)
    ax1.set_title("Downtime by reason", loc="left", color="#edf5ff", fontsize=14, fontweight="bold", pad=18)
    ax1.tick_params(colors="#c2cfdd", labelsize=9)
    ax1.grid(axis="x", color="#29415e", alpha=.55)
    ax1.set_axisbelow(True)
    for spine in ax1.spines.values(): spine.set_visible(False)
    for y, value in enumerate(reasons.values):
        ax1.text(value + 5, y, f"{int(value)}", va="center", color="#b9c8d8", fontsize=9)

    ax2 = fig.add_subplot(grid[4:8, 15:24])
    ax2.set_facecolor("#102238")
    ax2.bar(products.index, products.values, color="#5f8fff", width=.58)
    ax2.set_title("Downtime by product", loc="left", color="#edf5ff", fontsize=14, fontweight="bold", pad=14)
    ax2.tick_params(colors="#c2cfdd", labelsize=8)
    ax2.grid(axis="y", color="#29415e", alpha=.55)
    ax2.set_axisbelow(True)
    for spine in ax2.spines.values(): spine.set_visible(False)

    ax3 = fig.add_subplot(grid[9:12, 15:24])
    ax3.set_facecolor("#102238")
    ax3.barh(shifts.index[::-1], shifts.values[::-1], color="#ffb168", height=.5)
    ax3.set_title("Downtime by shift", loc="left", color="#edf5ff", fontsize=14, fontweight="bold", pad=10)
    ax3.tick_params(colors="#c2cfdd", labelsize=8)
    ax3.grid(axis="x", color="#29415e", alpha=.55)
    ax3.set_axisbelow(True)
    for spine in ax3.spines.values(): spine.set_visible(False)

    preview_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(preview_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.input, args.output, args.preview)

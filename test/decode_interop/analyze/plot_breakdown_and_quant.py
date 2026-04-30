"""Stacked breakdown + per-method per-bitwidth quantization speedup plots.

Reads `analyze/overhead_prod_vs_P.csv` (produced by `plot_overhead_prod.py`)
and emits four PNGs used by `docs/quantization/docs/3. waferllm_scale_overhead_analysis.md`:

  - breakdown_stacked_prod.png    : stacked compute / reduce / bcast bars by P
  - quant_speedup_method_A.png    : intra-op-only quantization speedup, per b, per P
  - quant_speedup_method_B.png    : bcast-only quantization speedup, per b, per P
  - quant_speedup_method_C.png    : both (A + B) — channel-only / full quantization

Methods (re-stated for the speedup plot):
  Method A  -- intra-op only      : reduce phases 1+2 at b bits, bcast at FP16
  Method B  -- bcast only         : reduce at FP16, bcast phase 3 at b bits
  Method C  -- A + B (channel-only): reduce + bcast both at b bits  (= doc's original Method A)

Cost model (matches docs/quantization/docs/2. quant_reduce_feasibility.md §2.5):
  non_quant     = compute + reconfig
  transit_red   = reduce - reconfig             # intra-op K-tree transit
  transit_bcast = bcast                         # inter-op K-tree transit
  e2e(b, mode)  = non_quant + scale_red(mode,b) * transit_red + scale_bcast(mode,b) * transit_bcast

Reconfig is held at 1188 cycles per step (3 x op:reconfig_x ~= 200 + 3 x op:reconfig_y ~= 196),
constant across P by topology.
"""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
ANALYZE = ROOT / "analyze"

RECONFIG_CYCLES = 1188.0
BITWIDTHS = [16, 8, 6, 4.2, 4]
BIT_LABELS = {16: "FP16", 8: "INT8", 6: "FP6", 4.2: "INT4+BF16", 4: "INT4"}


def load_summary():
    df = pd.read_csv(ANALYZE / "overhead_prod_vs_P.csv").sort_values("P").reset_index(drop=True)
    df["non_quant"] = df["compute_mean_cycles"] + RECONFIG_CYCLES
    df["transit_red"] = df["reduce_mean_cycles"] - RECONFIG_CYCLES
    df["transit_bcast"] = df["bcast_mean_cycles"]
    df["baseline_e2e"] = df["non_quant"] + df["transit_red"] + df["transit_bcast"]
    return df


# ----------------------------------------------------------------------
# Plot 1 — stacked breakdown
# ----------------------------------------------------------------------

def plot_stacked_breakdown(df: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    P = df["P"].astype(int).tolist()
    x = np.arange(len(P))
    width = 0.55

    compute = df["compute_mean_cycles"].to_numpy()
    intra = df["reduce_mean_cycles"].to_numpy()        # intra-op (reduce, includes reconfig)
    inter = df["bcast_mean_cycles"].to_numpy()         # inter-op (bcast)

    b1 = ax.bar(x, compute, width, label="compute", color="#2ca02c")
    b2 = ax.bar(x, intra, width, bottom=compute, label="intra-comm (reduce)", color="#9467bd")
    b3 = ax.bar(x, inter, width, bottom=compute + intra, label="inter-comm (bcast)", color="#d62728")

    totals = compute + intra + inter
    for xi, tot in zip(x, totals):
        ax.text(xi, tot + 120, f"{tot:.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    # annotate each segment with its cycle value
    for xi, c, r, b in zip(x, compute, intra, inter):
        ax.text(xi, c / 2, f"{c:.0f}", ha="center", va="center", fontsize=8, color="white")
        ax.text(xi, c + r / 2, f"{r:.0f}", ha="center", va="center", fontsize=8, color="white")
        ax.text(xi, c + r + b / 2, f"{b:.0f}", ha="center", va="center", fontsize=8, color="white")

    ax.set_xticks(x)
    ax.set_xticklabels([str(p) for p in P])
    ax.set_xlabel("P (grid side)")
    ax.set_ylabel("Mean cycles per decode step")
    ax.set_title("Per-config cycle breakdown — production scale (ppg=20)")
    ax.set_ylim(0, totals.max() * 1.10)
    ax.legend(loc="upper left", framealpha=0.95)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close(fig)
    print(f"saved {out}")


# ----------------------------------------------------------------------
# Plots 2/3/4 — per-method speedup vs bitwidth
# ----------------------------------------------------------------------

def e2e_for(df_row, b: float, mode: str) -> float:
    """Compute projected e2e cycles for a single P row at bitwidth b for the given method."""
    nq = df_row["non_quant"]
    tr = df_row["transit_red"]
    tb = df_row["transit_bcast"]
    f = b / 16.0
    if mode == "A":
        return nq + f * tr + tb
    if mode == "B":
        return nq + tr + f * tb
    if mode == "C":
        return nq + f * tr + f * tb
    raise ValueError(mode)


METHOD_TITLES = {
    "A": "Method A — intra-op (reduce phases 1+2) only at b bits",
    "B": "Method B — bcast (inter-op) only at b bits",
    "C": "Method C — A + B combined (reduce + bcast both at b bits)",
}
METHOD_COLORS = {
    "A": ["#cce5ff", "#80bfff", "#3399ff", "#0073e6", "#003d80"],
    "B": ["#ffd6cc", "#ff8566", "#ff5733", "#cc3300", "#661a00"],
    "C": ["#d9f2d9", "#80d480", "#33a833", "#1a7a1a", "#0d3d0d"],
}


def plot_method_speedup(df: pd.DataFrame, mode: str, out: Path):
    P_vals = df["P"].astype(int).tolist()
    n_p = len(P_vals)
    n_b = len(BITWIDTHS)
    width = 0.8 / n_b
    x = np.arange(n_p)

    fig, ax = plt.subplots(figsize=(8.5, 5.0))

    for j, b in enumerate(BITWIDTHS):
        reductions = []
        for _, row in df.iterrows():
            e2e_q = e2e_for(row, b, mode)
            red = (1.0 - e2e_q / row["baseline_e2e"]) * 100.0
            reductions.append(red)
        offset = (j - (n_b - 1) / 2.0) * width
        bars = ax.bar(
            x + offset,
            reductions,
            width,
            label=f"b={b:g}  ({BIT_LABELS[b]})",
            color=METHOD_COLORS[mode][j],
            edgecolor="black",
            linewidth=0.4,
        )
        for bar, val in zip(bars, reductions):
            if val < 0.05:
                ax.text(bar.get_x() + bar.get_width() / 2, 0.3, "—", ha="center", va="bottom", fontsize=8, color="gray")
            else:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    val + 0.4,
                    f"{val:.1f}%",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

    ax.set_xticks(x)
    ax.set_xticklabels([str(p) for p in P_vals])
    ax.set_xlabel("P (grid side)")
    ax.set_ylabel("Projected e2e reduction vs FP16 baseline (%)")
    ax.set_title(METHOD_TITLES[mode])
    ax.set_ylim(0, 50)
    ax.axhline(0, color="black", linewidth=0.6)
    ax.legend(loc="upper left", framealpha=0.95, ncol=3, fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close(fig)
    print(f"saved {out}")


def main():
    df = load_summary()
    print(df[["P", "compute_mean_cycles", "reduce_mean_cycles", "bcast_mean_cycles",
             "non_quant", "transit_red", "transit_bcast", "baseline_e2e"]].to_string(index=False))

    plot_stacked_breakdown(df, ANALYZE / "breakdown_stacked_prod.png")
    for mode in ("A", "B", "C"):
        plot_method_speedup(df, mode, ANALYZE / f"quant_speedup_method_{mode}.png")


if __name__ == "__main__":
    main()

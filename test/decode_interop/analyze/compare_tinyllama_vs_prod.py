"""Overlay the tinyllama-scale and production-scale sweeps on one plot.

Reads both `overhead_vs_P.csv` (tinyllama, from plot_overhead.py) and
`overhead_prod_vs_P.csv` (production, from plot_overhead_prod.py) and
emits:
- analyze/compare_bcast_ratio.png — bcast_ratio vs P, both sweeps
- analyze/compare_table.csv — joint summary table
"""

from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
ANA = ROOT / "analyze"


def main():
    tiny = pd.read_csv(ANA / "overhead_vs_P.csv").assign(
        workload="tinyllama (dim_p_pe=8, seq_len_p_pe=4, ffn_dim_p_pe=32)"
    )
    prod = pd.read_csv(ANA / "overhead_prod_vs_P.csv").assign(
        workload="production (dim_p_pe=12, seq_len_p_pe=12, ffn_dim_p_pe=40, ppg=20)"
    )
    joint = pd.concat([tiny, prod], ignore_index=True)
    joint.to_csv(ANA / "compare_table.csv", index=False)

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(13, 4.5))

    for label, df, ls in [("tinyllama e2e", tiny, "--"), ("prod e2e", prod, "-")]:
        ax_left.plot(df.P, df.e2e_mean_cycles, ls, marker="o", label=label)
    for label, df, ls in [("tinyllama bcast", tiny, "--"), ("prod bcast", prod, "-")]:
        ax_left.plot(df.P, df.bcast_mean_cycles, ls, marker="P", label=label)
    ax_left.set_xlabel("P (grid side)")
    ax_left.set_ylabel("Mean cycles per decode step")
    ax_left.set_title("Absolute cycles: tinyllama vs production")
    ax_left.legend()
    ax_left.grid(True, alpha=0.3)

    ax_right.plot(tiny.P, tiny.bcast_ratio * 100, "d--", label="tinyllama bcast/e2e (%)")
    ax_right.plot(prod.P, prod.bcast_ratio * 100, "d-", label="prod bcast/e2e (%)")
    ax_right.plot(tiny.P, tiny.comm_ratio * 100, "x:", label="tinyllama comm/e2e (%)", alpha=0.5)
    ax_right.plot(prod.P, prod.comm_ratio * 100, "x-", label="prod comm/e2e (%)", alpha=0.5)
    ax_right.set_xlabel("P (grid side)")
    ax_right.set_ylabel("Ratio (%)")
    ax_right.set_title("Inter-op handoff fraction: tinyllama vs production")
    ax_right.legend()
    ax_right.grid(True, alpha=0.3)

    plt.suptitle("WaferLLM decode_struct() overhead — workload-scale comparison")
    plt.tight_layout()
    out_png = ANA / "compare_bcast_ratio.png"
    plt.savefig(out_png, dpi=150)
    print(joint.to_string(index=False))
    print(f"\nPlot saved to {out_png}")


if __name__ == "__main__":
    main()

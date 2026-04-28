"""Aggregate the production-scale sweep into a single CSV + plot.

Mirrors plot_overhead.py but globs `model_config/prod_p*.json` and reads
`results/prod_p<P>/sim.log` instead of `results/p<P>/sim.log`. Outputs:
- analyze/overhead_prod_vs_P.csv
- analyze/overhead_prod_vs_P.png
"""

import json
from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from compute_breakdown import breakdown


ROOT = Path(__file__).resolve().parents[1]


def main():
    rows = []
    for cfg_path in sorted(ROOT.glob("model_config/prod_p*.json")):
        cfg = json.loads(cfg_path.read_text())
        simlog_dir = ROOT / "results" / f"prod_p{cfg['P']}"
        simlog = simlog_dir / "sim.log"
        if not simlog.exists():
            simlog = simlog_dir / "sim.log.gz"
        if not simlog.exists():
            print(f"skip {simlog} (missing)")
            continue
        summary, _ = breakdown(simlog)
        s = summary.iloc[0].to_dict()
        s["P"] = cfg["P"]
        s["dim"] = cfg["dim"]
        rows.append(s)

    if not rows:
        print("No prod sim.logs found — run the sweep first.")
        return

    df = pd.DataFrame(rows).sort_values("P").reset_index(drop=True)
    out_csv = ROOT / "analyze" / "overhead_prod_vs_P.csv"
    df.to_csv(out_csv, index=False)
    print(df.to_string(index=False))

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(df.P, df.e2e_mean_cycles, "o-", label="e2e total", color="C0")
    ax1.plot(df.P, df.compute_mean_cycles, "^-", label="compute only", color="C2")
    ax1.plot(df.P, df.reduce_mean_cycles, "s-", label="reduce (intra-op)", color="C4")
    ax1.plot(df.P, df.bcast_mean_cycles, "P-", label="bcast (inter-op)", color="C3")
    ax1.set_xlabel("P (grid side)")
    ax1.set_ylabel("Mean cycles per decode step")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(df.P, df.bcast_ratio * 100, "d--", label="bcast / e2e (%)", color="C3")
    ax2.plot(df.P, df.comm_ratio * 100, "x:", label="comm / e2e (%)", color="C1")
    ax2.set_ylabel("Ratio (%)")
    ax2.legend(loc="upper right")

    plt.title("WaferLLM decode_struct() overhead vs P — production scale (llama8B_4k_1_360 ratios, ppg=20)")
    plt.tight_layout()
    out_png = ROOT / "analyze" / "overhead_prod_vs_P.png"
    plt.savefig(out_png, dpi=150)
    print(f"\nPlot saved to {out_png}")
    print(f"Summary CSV saved to {out_csv}")


if __name__ == "__main__":
    main()

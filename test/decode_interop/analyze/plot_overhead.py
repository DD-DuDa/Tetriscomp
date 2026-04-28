"""Aggregate sweep results into a single CSV + plot of comm overhead vs P.

Reads test/decode_interop/results/p<P>/sim.log for each interop_p<P>.json
config, runs compute_breakdown.breakdown(...) on each, and produces:
- analyze/overhead_vs_P.csv  (one row per P with summary cycles)
- analyze/overhead_vs_P.png  (twin-axis plot: cycles + comm-ratio %)
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
    for cfg_path in sorted(ROOT.glob("model_config/interop_p*.json")):
        cfg = json.loads(cfg_path.read_text())
        simlog = ROOT / "results" / f"p{cfg['P']}" / "sim.log"
        if not simlog.exists():
            print(f"skip {simlog} (missing)")
            continue
        summary, _ = breakdown(simlog)
        s = summary.iloc[0].to_dict()
        s["P"] = cfg["P"]
        s["dim"] = cfg["dim"]
        rows.append(s)

    if not rows:
        print("No sim.logs found — run the sweep first.")
        return

    df = pd.DataFrame(rows).sort_values("P").reset_index(drop=True)
    out_csv = ROOT / "analyze" / "overhead_vs_P.csv"
    df.to_csv(out_csv, index=False)
    print(df.to_string(index=False))

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(df.P, df.e2e_mean_cycles, "o-", label="e2e total", color="C0")
    ax1.plot(df.P, df.comm_mean_cycles, "s-", label="comm only", color="C3")
    ax1.plot(df.P, df.compute_mean_cycles, "^-", label="compute only", color="C2")
    ax1.set_xlabel("P (grid side)")
    ax1.set_ylabel("Mean cycles per decode step")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(df.P, df.comm_ratio * 100, "d--", label="comm / e2e (%)", color="C1")
    ax2.set_ylabel("Comm ratio (%)")
    ax2.legend(loc="upper right")

    plt.title("WaferLLM decode_struct() inter-op communication overhead vs P")
    plt.tight_layout()
    out_png = ROOT / "analyze" / "overhead_vs_P.png"
    plt.savefig(out_png, dpi=150)
    print(f"\nPlot saved to {out_png}")
    print(f"Summary CSV saved to {out_csv}")


if __name__ == "__main__":
    main()

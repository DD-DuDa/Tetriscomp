"""Aggregate per-PE region cycles into a comm-vs-compute breakdown for one config.

Input:  results/p<P>/sim.log
Output: breakdown_p<P>.csv with columns:
        region, mean_cycles, max_cycles, count_invocations
Also prints summary: total e2e mean cycles, comm mean cycles,
compute mean cycles, comm/total ratio.

Methodology:
- For each PE, sum cycles across all `op:*` regions => per-PE total e2e
  cycles for one decode step.
- Mean across PEs => "e2e mean cycles".
- For each PE, sum cycles across all `comm:*` regions (from comm_pe.csl
  primitives) + any `op:reconfig_*` regions (reconfig_allreduce_axis is
  pure-comm with no inner comm tag, since it's a route-config call) =>
  per-PE comm cycles. Mean across PEs => "comm mean cycles".
- compute mean cycles = e2e - comm.
"""

import sys
from pathlib import Path
import pandas as pd
from parse_simlog import parse


# op:reconfig_x and op:reconfig_y wrap pure-comm route-reconfig calls;
# their inner comm_pe.csl primitives don't have a paired comm:reconfig_x
# or comm:reconfig_y tag (the inner tag is just `comm:reconfig`, which
# we already count via comm:*). We add the op-level reconfig cycles to
# the comm bucket because the entire op IS comm.
COMM_OP_TAGS = {"op:reconfig_x", "op:reconfig_y"}


def breakdown(simlog_path: Path):
    """Returns (summary_df, per_region_df) for one sim.log."""
    with open(simlog_path) as f:
        df = parse(f)

    # Per-PE total of all op:* regions = e2e per PE (one decode step)
    op = df[df.region.str.startswith("op:")]
    e2e_per_pe = op.groupby(["pe_x", "pe_y"])["cycles"].sum()

    # Per-PE total of comm:* regions + op:reconfig_*
    comm = df[df.region.str.startswith("comm:") | df.region.isin(COMM_OP_TAGS)]
    comm_per_pe = comm.groupby(["pe_x", "pe_y"])["cycles"].sum()

    # Reindex to e2e_per_pe so PEs that didn't touch comm get a 0
    e2e_mean = e2e_per_pe.mean()
    comm_mean = comm_per_pe.reindex(e2e_per_pe.index, fill_value=0).mean()
    compute_mean = e2e_mean - comm_mean

    summary = pd.DataFrame([{
        "e2e_mean_cycles": e2e_mean,
        "comm_mean_cycles": comm_mean,
        "compute_mean_cycles": compute_mean,
        "comm_ratio": comm_mean / e2e_mean if e2e_mean else float("nan"),
    }])

    per_region = (
        df.groupby("region")["cycles"]
          .agg(mean_cycles="mean", max_cycles="max", count_invocations="count")
          .reset_index()
          .sort_values("mean_cycles", ascending=False)
          .reset_index(drop=True)
    )

    return summary, per_region


if __name__ == "__main__":
    simlog = Path(sys.argv[1])
    summary, per_region = breakdown(simlog)

    out_csv = simlog.parent / f"breakdown_{simlog.parent.name}.csv"
    per_region.to_csv(out_csv, index=False)

    print(summary.to_string(index=False))
    print(f"\nPer-region detail written to: {out_csv}")

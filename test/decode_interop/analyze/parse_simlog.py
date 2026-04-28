"""Parse a sim.log produced by SDK 1.4 simulator with simprint markers.

Marker line shape: ``@<cycle> PE(<x>,<y>): <prefix>:<tag>``
where prefix in {op_start, op_end, comm_start, comm_end}, cycle is the
simulator-reported cycle index, x/y are integer PE coordinates, and tag
matches ``[A-Za-z0-9_]+`` (case matters - e.g. ``all_reduceMax_bsz``).

For each (PE, region, occurrence) the parser pairs up the start and end
markers and emits one row with the cycle delta. ``region`` is e.g.
``op:rmsnorm_x`` or ``comm:all_reduce_bsz``. ``occurrence`` is the
0-indexed dynamic invocation count, since the same primitive is called
multiple times per decode step.

Usage:
    python3 parse_simlog.py path/to/sim.log > regions.csv
"""

import gzip
import re
import sys
from collections import defaultdict
from pathlib import Path
import pandas as pd


LINE_RE = re.compile(
    r"^@(?P<cycle>\d+)\s+PE\((?P<x>\d+),(?P<y>\d+)\):\s+"
    r"(?P<prefix>op_start|op_end|comm_start|comm_end):(?P<tag>[A-Za-z0-9_]+)"
)


def parse(stream):
    """Parse a sim.log stream into a DataFrame of (pe_x, pe_y, region, occurrence, cycles)."""
    open_starts = defaultdict(list)  # (x, y, region) -> FIFO list of pending start cycles
    occ_count = defaultdict(int)     # (x, y, region) -> next dynamic-invocation index
    rows = []

    for line in stream:
        m = LINE_RE.match(line)
        if not m:
            continue
        cycle = int(m["cycle"])
        x, y = int(m["x"]), int(m["y"])
        prefix, tag = m["prefix"], m["tag"]
        kind = "op" if prefix.startswith("op_") else "comm"
        region = f"{kind}:{tag}"
        key = (x, y, region)
        if prefix.endswith("_start"):
            open_starts[key].append(cycle)
        else:
            if not open_starts[key]:
                # End without a matching start (truncated log or out-of-order)
                continue
            start = open_starts[key].pop(0)
            rows.append({
                "pe_x": x,
                "pe_y": y,
                "region": region,
                "occurrence": occ_count[key],
                "cycles": cycle - start,
            })
            occ_count[key] += 1

    return pd.DataFrame(rows, columns=["pe_x", "pe_y", "region", "occurrence", "cycles"])


def _open(path):
    """Open a path, transparently handling .gz."""
    p = Path(path)
    if p.suffix == ".gz":
        return gzip.open(p, "rt")
    return p.open()


if __name__ == "__main__":
    src = sys.stdin if len(sys.argv) < 2 else _open(sys.argv[1])
    df = parse(src)
    df.to_csv(sys.stdout, index=False)

import json
import os
import argparse
import numpy as np

from cerebras.sdk.runtime.sdkruntimepybind import (
    SdkRuntime, SimfabConfig, get_simulator,
)


class Config:
    def __init__(self):
        self.P = 8
        self.bsz = 1
        self.group_num = 2
        self.dim = 64
        self.n_heads = 1
        self.n_kv_heads = 1
        self.head_dim = 64
        self.seq_len = 64
        self.ffn_dim = 64


def parse_args():
    parser = argparse.ArgumentParser(description="Launch decode kernel under simulator (cycle-count only)")
    parser.add_argument("--config", default="config.json", type=str, help="Config file")
    return parser.parse_args()


def main():
    args = parse_args()
    config = Config()

    if not os.path.exists(args.config):
        print("Host: Use default test values.")
    else:
        with open(args.config) as f:
            config.__dict__.update(json.load(f))

    P = config.P
    bsz = config.bsz
    dim = config.dim
    n_heads = config.n_heads
    n_kv_heads = config.n_kv_heads
    head_dim = config.head_dim
    seq_len = config.seq_len
    ffn_dim = config.ffn_dim

    dim_p_pe = dim // P
    pes_p_head = P // n_heads
    pes_p_kv_head = P // n_kv_heads
    head_dim_p_pe = head_dim // P
    seq_len_p_pe = seq_len // P
    ffn_dim_p_pe = ffn_dim // P

    print(f"Host: P: {P}, Batch size: {bsz}, dim_p_pe: {dim_p_pe}, "
          f"pes_p_head: {pes_p_head}, pes_p_kv_head: {pes_p_kv_head}, "
          f"head_dim_p_pe: {head_dim_p_pe}, seq_len_p_pe: {seq_len_p_pe}, "
          f"ffn_dim_p_pe: {ffn_dim_p_pe}")

    # SDK 1.4 caps num_threads at 64. suppress_trace=True skips the multi-GB
    # simfab_traces directory — we measure cycles via simprint markers in
    # sim.log, not via host-side D2H, so no traces or tensor I/O are needed.
    runner = SdkRuntime("out", get_simulator(SimfabConfig(num_threads=64, suppress_trace=True)))
    runner.load()
    runner.run()

    runner.launch("init_task", nonblock=False)

    repeat_steps = 1
    warmup_steps = 0
    runner.launch("decode_host", np.int16(repeat_steps), np.int16(warmup_steps), nonblock=False)

    runner.stop()

    print(f"Host: simulator finished. P={P}, repeat_steps={repeat_steps}. "
          f"Cycle data is in sim.log (parse via simprint markers).")


if __name__ == "__main__":
    main()

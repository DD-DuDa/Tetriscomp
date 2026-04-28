#!/bin/bash
# Sweep the production-scale (llama8B_4k_1_360 ratios, ppg=20) configs
# across P ∈ {40, 60, 80, 100}. Mirror of sweep_bcast.sh for the prod_p* set.
# Run inside the tetris container, e.g.:
#   docker exec tetris bash -lc 'export PATH=/home/dayou/Downloads/sdk1.4:$PATH && bash /mnt/raid0nvme0/dayou/Projs/Tetriscomp/test/decode_interop/sweep_prod.sh'
set -e
cd /home/dayou/Projs/Tetriscomp/test/decode_interop
for P in 40 60 80 100; do
  echo "=== Running prod P=$P at $(date +%T) ==="
  RESULT_DIR=results/prod_p${P} bash run_sim.sh model_config/prod_p${P}.json 2>&1 | tail -5
  echo "--- prod P=$P done at $(date +%T) ---"
done
echo "ALL_DONE"

set -e
# Container SDK location. Task plan said /workspace/sdk, but the tetris container
# does not have that path; the canonical install is /home/dayou/Downloads/sdk1.4
# (the same path every refer/tetris/ run script uses). Using that here.
export PATH=/home/dayou/Downloads/sdk1.4:$PATH

# export SINGULARITYENV_SIMFABRIC_DEBUG=router
CONFIG=$1

if [ -z "$CONFIG" ]; then
    CONFIG="config.json"
fi

# if config.json exists
if [ -f $CONFIG ]; then
    echo "Use config values from $CONFIG."
    # The tetris container has no jq; use python3 to extract the same fields.
    eval "$(python3 -c "
import json, sys
c = json.load(open('$CONFIG'))
keys = [('P','P'),('GROUP_NUM','group_num'),('BSZ','bsz'),('DIM','dim'),
        ('N_HEADS','n_heads'),('N_KV_HEADS','n_kv_heads'),('HEAD_DIM','head_dim'),
        ('SEQ_LEN','seq_len'),('FFN_DIM','ffn_dim')]
for shvar, jkey in keys:
    print(f'{shvar}={c[jkey]}')
")"
else
    echo "Use default test values."
    P=8
    GROUP_NUM=2
    BSZ=1
    DIM=64
    N_HEADS=1
    N_KV_HEADS=1
    HEAD_DIM=64
    SEQ_LEN=64
    FFN_DIM=64
fi

FABRIC_W=$(($P + 7))
FABRIC_H=$(($P + 2))

dim_p_pe=$(($DIM / $P))
pes_p_head=$(($P / $N_HEADS))
pes_p_kv_head=$(($P / $N_KV_HEADS))
head_dim_p_pe=$(($HEAD_DIM / $P))
seq_len_p_pe=$(($SEQ_LEN / $P))
ffn_dim_p_pe=$(($FFN_DIM / $P))
pe_num_p_group=$(($P / $GROUP_NUM))

root_1st_phase=$((pe_num_p_group / 2))
root_2nd_phase=$(((($GROUP_NUM / 2) * pe_num_p_group) + root_1st_phase))

echo "P: $P"
echo "BSZ: $BSZ"
echo "DIM: $DIM"
echo "N_HEADS: $N_HEADS"
echo "N_KV_HEADS: $N_KV_HEADS"
echo "HEAD_DIM: $HEAD_DIM"
echo "SEQ_LEN: $SEQ_LEN"
echo "FFN_DIM: $FFN_DIM"

echo "GROUP_NUM: $GROUP_NUM"
echo "PE_NUM_PER_GROUP: $pe_num_p_group"
echo "ROOT_1ST_PHASE: $root_1st_phase"
echo "ROOT_2ND_PHASE: $root_2nd_phase"

cslc --arch=wse3 ./src/layout.csl --fabric-dims="$FABRIC_W","$FABRIC_H" --fabric-offsets=4,1 \
    --params=P:"$P",bsz:"$BSZ",dim_p_pe:"$dim_p_pe",pes_p_head:"$pes_p_head",pes_p_kv_head:"$pes_p_kv_head",head_dim_p_pe:"$head_dim_p_pe",seq_len_p_pe:"$seq_len_p_pe",ffn_dim_p_pe:"$ffn_dim_p_pe",pe_num_p_group:"$pe_num_p_group",root_1st_phase:"$root_1st_phase",root_2nd_phase:"$root_2nd_phase" \
    --max-inlined-iterations=100000 \
    -o out --memcpy --channels 1

cs_python launch_sim.py --config $CONFIG

RESULT_DIR=${RESULT_DIR:-results/p${P}}
mkdir -p "${RESULT_DIR}"
if [ -f ./sim.log ]; then mv ./sim.log "${RESULT_DIR}/sim.log"; fi

# Per refer/tetris/CLAUDE.md rule 2 — clean wio* after every CSL invocation
rm -rf wio*

# rm -rf simfab_traces  # disabled - we use a persistent symlink to /mnt/raid0nvme0/dayou/decode_interop_simfab_traces
rm -rf wio_flows_tmpdir.*
rm -f wsjob-*.json
rm -f run_meta.json
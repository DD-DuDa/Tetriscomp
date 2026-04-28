# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Tetriscomp is a research project applying **quantization + sparsity to LLM decoding on the Cerebras Wafer-Scale Engine (WSE)**. At this stage the repo is mostly planning/docs and a small toolchain — there is no kernel source tree yet. Most engineering output takes the form of analyses written into `docs/`, with CSL kernel work expected to land later.

## Workflow rules (override defaults)

1. **Never delete the `# My Prompt` section** at the top of any task file under `docs/<track>/tasks/`. It captures the user's original ask verbatim and is the source of truth for the task.
2. For each task: write the **plan** into the task file under `docs/<track>/tasks/`, then after finishing, write the **result, analysis, and what the code did** into `docs/<track>/docs/`. `tasks/` is the goal; `docs/` is the deliverable.
3. The two work tracks are `quantization/` and `sparsity/`. Each has its own `tasks/` and `docs/` subtree; keep deliverables in the matching track.
4. **CSL programs only run inside the `tetris` Docker container.** Do not invoke `cslc` / `cs_python` / `run.sh` from the host. Standard pattern:
   ```bash
   docker exec -it tetris /bin/bash
   cd /home/dayou/tetris/examples/<example>
   bash run.sh
   ```
   See `refer/tetris/CLAUDE.md` for the full container conventions (SDK on `PATH`, `simfab_traces` symlink, post-run cleanup).
   **SDK path inside the container** is `/home/dayou/Downloads/sdk1.4` (the host directory is bind-mounted at the same path). `refer/tetris/CLAUDE.md` mentions `/workspace/sdk`, but that path does not exist in the current `tetris` container — verified empirically 2026-04-28. The SDK 1.4 simulator caps `SimfabConfig(num_threads=…)` at 64.

## Repo layout (the parts that aren't obvious from `ls`)

- `docs/quantization/` and `docs/sparsity/` — the two parallel research tracks. `tasks/` holds prompts + plans, `docs/` holds finished analyses (e.g. `docs/sparsity/docs/x1. spmv_csl.md` — a kernel-level comparison of the Cerebras GEMV-checkerboard vs. 7pt-stencil benchmarks, with concrete next-step recommendations for the project).
- `docs/cerebras-sdk-guides-rebuild.md` — log of the SDK-skill rebuild (2026-04-27), including how to refresh.
- `refer/` — symlinks to sibling reference projects on disk:
  - `refer/tetris/` → the Tetris ASPLOS'26 paper + CSL analysis (also contains an older `cerebras-sdk-guides` skill from a 1.4.0 crawl that served as the rebuild template).
  - `refer/WaferLLM/` → reference WSE kernels (`Decode/`, `Prefill/`, `MeshGEMM/`, `MeshGEMV/`); the production-relevant baseline for decode-time inference.
- `.claude/skills/cerebras-sdk-guides/` — locally bundled SDK 2.10.0 reference (91 pages: 84 guides + 6 api + 1 core), produced by `scripts/crawl_cerebras_sdk.py`. Use this skill via `Skill` rather than re-fetching pages from `sdk.cerebras.net`.

## Common commands

Refresh the bundled Cerebras SDK reference (re-crawls `sdk.cerebras.net` in place, updates `index.md` + `crawl-summary.json` + `pages/*.md`):

```bash
python3 scripts/crawl_cerebras_sdk.py \
  /mnt/raid0nvme0/dayou/Projs/Tetriscomp/.claude/skills/cerebras-sdk-guides
```

Add new SDK pages by appending to the `SEEDS` list in `scripts/crawl_cerebras_sdk.py` before re-running.

## Architectural orientation for kernel work

When citing or paraphrasing SDK behavior in analyses, ground the claim in `.claude/skills/cerebras-sdk-guides/references/pages/<slug>.md` (SDK 2.10.0) — not memory, and not the older 1.4.0 copy under `refer/tetris/`.

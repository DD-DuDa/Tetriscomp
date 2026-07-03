---
name: cerebras-sdk-guides
description: This skill should be used when tasks involve Cerebras SDK tutorials, end-to-end examples, optimization workflows, production hardening, or best-practice implementation patterns.
---

# Cerebras SDK Guides

## Overview

Use this skill for workflow-level implementation, tutorial-driven development, and production-oriented guidance. Prioritize example adaptation, debugging strategy, and operational reliability.

This skill covers the broad tutorial and guide corpus from `https://sdk.cerebras.net` (SDK 2.10.0). The current crawl saved 91 pages total; 84 are tagged for this guides skill (the other 7 are split: 6 API references and 1 core/installation page) but all are kept under `references/pages/` so cross-links continue to resolve.

## Use This Skill When

- Build from tutorial or benchmark examples.
- Adapt sample code to a new workload.
- Design production-ready execution patterns and reliability checks.
- Improve debugging, observability, and iterative optimization workflows.
- Explain conceptual model choices before API-level coding.

## Workflow

1. Identify the closest tutorial/benchmark pattern in `references/index.md`.
2. Extract the minimal reproducible workflow from the selected guide page.
3. Adapt in small steps: baseline run, incremental modification, validation after each change.
4. Add production guardrails: explicit config capture, deterministic run commands, and failure triage checkpoints.
5. If blocked by exact API semantics, consult the `api-docs__*` pages (sdkruntime, sdklayout, appliance); if blocked by environment setup, consult `installation-guide.md`.

## How To Use This Skill

Use prompts like:
- "Map this workload to the closest Cerebras tutorial and produce an implementation plan."
- "Turn this benchmark example into a production-ready runbook with retries and checkpoints."
- "Explain the conceptual model behind this Cerebras code sample before modifying it."
- "Refactor this tutorial-based prototype into a maintainable project structure."
- "Create a debugging playbook for runtime failures in a multi-step guide workflow."
- "Show a production-ready streaming pattern with retries and validation checkpoints."
- "Identify which example best matches my input/output and performance constraints."

## Failure Handling

- Assume guide text may lag runtime behavior; verify version assumptions from `references/crawl-summary.json` (`generated_at` and `root_url`) and the user environment.
- If a guide step fails, isolate to the first failing command and verify prerequisites before changing multiple variables.
- If a guide references API behavior implicitly, cross-check with the API reference pages before applying the workaround.

## What Changed Since the Previous Crawl (1.4.0 → 2.10.0)

- New tutorial: `csl/code-examples/tutorial-topic-16-queue-flush` (Topic 16: Queue Flush).
- New language page: `csl/comptime-struct-migration` (comptime-struct migration guide).
- All previously-known pages re-crawled at SDK 2.10.0; release notes and doc-update logs reflect cumulative changes since 1.4.0.

## References

- Primary index: `references/index.md`
- Crawl metadata: `references/crawl-summary.json`
- Full pages: `references/pages/*.md`

For targeted lookup, search locally:

```bash
rg -n "tutorial|example|benchmark|debug|production|workflow|stream" \
   .claude/skills/cerebras-sdk-guides/references/pages
```

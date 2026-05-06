# Alice Cloud Thesis Execution Runbook

This runbook is the active cloud execution guide for thesis-grade M-RAG
experiments. It replaces older cloud-provider notes and keeps local validation
separate from thesis-grade MIDM BASE runs.

## Instance Recommendation

| Purpose | Recommended Alice Profile | Notes |
|---|---|---|
| BASE smoke and controlled serial runs | `G-NAHPM-40 / A100 MIG 40GB` | First choice for 1-sample smoke and cautious staged tuning. |
| Full main generation headroom | `G-NAHP-80 / A100 80GB PCIe` | Safer choice if smoke OOMs, if context grows, or for the full matrix. |

Start with the 40GB profile for the 1-sample smoke. Move to the 80GB profile if
the smoke fails due to VRAM, if model loading is unstable, or if the main run
needs more headroom.

## Model Policy

- Local MIDM Mini is validation-only.
- Local MIDM Mini outputs are not thesis-grade results.
- Local MIDM BASE is blocked by local VRAM and should not be attempted again
  without a separate explicit plan.
- Alice Cloud MIDM BASE is the thesis-grade model path:
  `K-intelligence/Midm-2.0-Base-Instruct`.
- Alice BASE smoke output is still a smoke artifact, not a final thesis result.
- Thesis claims require the later approved thesis tuning, freeze, main
  generation, and evaluation phases.

## Clone The Repository

HTTPS clone is simplest for a public repository:

```bash
git clone https://github.com/LxNx-Hn/M_RAG.git
cd M_RAG
git checkout main
git pull --ff-only origin main
```

SSH clone is acceptable only if the user configures SSH keys manually on Alice:

```bash
git clone git@github.com:LxNx-Hn/M_RAG.git
```

Never commit SSH private keys, passwords, Alice credentials, API tokens, or
secret files to the repository.

## SSH Key Safety

- Keep private keys outside git.
- Store keys under `~/.ssh/` on Alice, never inside this repository.
- Use strict permissions:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/<key>
```

- Prefer `ssh-agent` or Alice secret mechanisms.
- Do not paste private keys into Codex or write them into tracked files.

## Hugging Face Token Handling

If the MIDM model requires Hugging Face authentication, use one of these
methods on Alice:

```bash
export HF_TOKEN="<token-from-your-shell-or-secret-manager>"
huggingface-cli login
```

Do not commit `HF_TOKEN`, Hugging Face cache credentials, or `.env` files. If a
local environment file is used on Alice, keep it untracked and restrict file
permissions.

## OpenAI And RAGAS Policy

- OpenAI is disabled by default.
- RAGAS is disabled by default.
- Official RAGAS or OpenAI-based evaluation belongs to a later evaluation phase
  and requires explicit user approval.
- Alice smoke, tuning, and main generation must not call OpenAI or RAGAS.

## Execution Order

1. Setup the Alice instance and dependencies.
2. Run Alice MIDM BASE smoke with exactly 1 sample.
3. Run limited thesis tuning only after explicit approval.
4. Create the Phase 8 parameter freeze checkpoint.
5. Run main generation only after frozen params are confirmed.
6. Prepare evaluation and analysis only after generation artifacts exist.

Main generation must not run before `experiments/configs/frozen_params.yaml`
exists, unless a later phase explicitly approves an equivalent freeze
confirmation.

## Setup

From the repository root on Alice:

```bash
bash experiments/scripts/alice/alice_setup.sh
```

The setup script checks Python, git, CUDA, PyTorch, and GPU visibility. It does
not run models. It does not download models unless the user explicitly sets:

```bash
ALLOW_MODEL_DOWNLOAD=1 bash experiments/scripts/alice/alice_setup.sh
```

## Alice BASE Smoke

Run the one-sample smoke only after the setup check passes:

```bash
CONFIRM_ALICE_BASE_SMOKE=1 bash experiments/scripts/alice/alice_base_smoke.sh
```

Smoke defaults:

- `MODEL_NAME=K-intelligence/Midm-2.0-Base-Instruct`
- `QUERY_SPLIT=tuning_queries`
- `QUERY_LIMIT=1`
- `PROFILE=current_defaults`
- `AXIS_CONFIG=hyde_off__no_decoder_control`
- `MAX_SAMPLES=1`
- `MAX_NEW_TOKENS=512`
- `TEMPERATURE=0.0`
- `OPENAI_ENABLED=0`
- `RAGAS_ENABLED=0`

The script fails closed if confirmation is missing or if more than one sample
would run.

## Tuning And Freeze Planning

Plan the thesis tuning stage:

```bash
bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage tuning
```

Check whether frozen params are ready:

```bash
bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage freeze-check
```

Real tuning requires a later explicit user-approved phase. Do not use
`decoder_main_queries` or `candidate_final_eval_queries` to choose parameters.

## Main Generation Planning

Plan main generation only after the freeze checkpoint is ready:

```bash
bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage main-generation
```

The main stage requires `experiments/configs/frozen_params.yaml`, or an explicit
future approval flag. Do not bypass the freeze checkpoint casually.

## Cost Control

- Use `batch_size=1`.
- Use `max_parallel_requests=1`.
- Use `MAX_NEW_TOKENS=512` for smoke.
- Start with 1 sample.
- Expand only after inspecting logs, output shape, and GPU memory.
- Keep OpenAI and RAGAS disabled during generation.

## Stop Safely

If a run is active:

```bash
ps -ef | grep -E "run_local_smoke|run_generation|run_tuning"
nvidia-smi
```

Stop only the intended process, then preserve logs and output files for review.
Avoid deleting result artifacts unless a later cleanup phase explicitly approves
it.

## Collect Result Files

Smoke outputs:

```bash
experiments/results/smoke/
experiments/reports/
```

Future tuning and generation outputs should remain under `experiments/results/`
with matching reports under `experiments/reports/`. Do not edit generated output
records by hand.

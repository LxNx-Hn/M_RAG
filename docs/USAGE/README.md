# M-RAG Usage Documents

## Document Map

| Document | Purpose |
|---|---|
| `DEPLOY.md` | Local, Docker, and service deployment notes |
| `DEPLOYMENT_BOUNDARY.md` | Runtime/experiment/docs package boundary and verification checklist |
| `ALICE_CLOUD.md` | Alice Cloud thesis execution runbook |
| `ALICE_CLOUD_GUIDE.md` | Deprecated pointer to `ALICE_CLOUD.md` |
| `ALICE_SETUP.md` | Deprecated pointer to `ALICE_CLOUD.md` |
| `POSTGRES_GUIDE.md` | PostgreSQL operational database guide |
| `TESTING_GUIDE.md` | Local validation and CI-oriented checks |

## Execution Path Selection

| Purpose | Recommended Path |
|---|---|
| Local smoke validation | Local SQLite + MIDM Mini, validation-only |
| Thesis-grade BASE smoke | Alice Cloud + MIDM Base, 1 sample |
| Thesis tuning and freeze | Alice Cloud + MIDM Base, explicit staged approval |
| Main thesis generation | Alice Cloud + frozen params + 8 HyDE/CAD/SCD configs |
| Service demonstration | PostgreSQL + service API path |

## Important Policy

- Local MIDM Mini outputs are validation-only and must not be used for final thesis claims.
- Local MIDM Base is blocked by VRAM and must not be attempted again without an explicit offload or smaller-scope approval.
- Thesis-grade experiments use `K-intelligence/Midm-2.0-Base-Instruct` on Alice Cloud.
- Main generation requires a parameter freeze checkpoint before it can run.
- OpenAI and RAGAS are disabled by default and belong to later explicitly approved evaluation phases only.

# M-RAG Usage Documents

## Document Map

| Document | Purpose |
|---|---|
| `DEPLOY.md` | Local, Docker, and service deployment notes |
| `DEPLOYMENT_BOUNDARY.md` | Runtime/experiment/docs package boundary and verification checklist |
| `POSTGRES_GUIDE.md` | PostgreSQL operational database guide |
| `TESTING_GUIDE.md` | Local validation and CI-oriented checks |
| `../../FINALDOCS/VALIDATION/verify_finaldocs_60q.py` | Read-only final thesis-package verification |

## Execution Path Selection

| Purpose | Recommended Path |
|---|---|
| Local smoke validation | Local SQLite + MIDM Mini, validation-only |
| Final thesis verification | `FINALDOCS/VALIDATION/verify_finaldocs_60q.py` |
| Service demonstration | PostgreSQL + service API path |

## Important Policy

- Local MIDM Mini outputs are validation-only and must not be used for final thesis claims.
- Local MIDM Base is blocked by VRAM and must not be attempted again without an explicit offload or smaller-scope approval.
- Final thesis claims are read from the stored 60-query package in `FINALDOCS/`; this directory no longer provides a cloud-execution guide.
- OpenAI and RAGAS remain disabled by default. They may run only in an explicitly approved evaluation phase.

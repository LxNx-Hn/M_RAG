# M-RAG Production Audit Final Report
Date: 2026-04-14
Scope: Security, tenancy isolation, reliability, deployment readiness, and RAG quality guardrails

## 1) Final verdict
- Current codebase has moved from "demo-risk" to "internal demo-ready with controlled risk".
- Tier 0 and most Tier 1/Tier 2 blocking items are now implemented in code.
- External/public launch is still not recommended until Tier 3 items are finished (refresh-cookie auth, TLS/HSTS end-to-end, audit logging, E2E/load validation).

## 2) What was completed
### Tier 0 (critical blockers)
- Enforced JWT auth dependency across protected routers.
- Removed insecure auth fallbacks; startup now fails fast when required auth setup is missing.
- Added user ownership filtering (`user_id`) for papers/history/chat/citations paths.
- Removed database URL leakage from root/health responses.
- Hardened upload flow with rollback boundary across file/vector/db.
- Collection delete now validates ownership and performs coordinated cleanup.
- Docker compose now uses env-required secrets and restart policy.

### Tier R0 / Tier 1 quality and safety
- Stream route aligned with main pipeline path and explicit timeout/error SSE events.
- Pipeline C fixed to explicit pairwise comparison mode (exactly 2 documents).
- Collection namespaced by user (`{user_id}__{collection_name}`) for tenant isolation.
- Query length and request schema bounds hardened (`max_length`, filters).
- Frontend 401 handling now triggers logout and redirect.
- BM25 migrated to per-collection index map with disk persistence.

### Tier 2 (deployment prerequisites)
- Added global rate limiter scaffold (`slowapi`) and route-level limits:
  - `/api/auth/register`: 3/min
  - `/api/auth/login`: 10/min
  - `/api/papers/upload`: 5/min
  - `/api/chat/query`, `/api/chat/query/stream`: 20/min
- Added security headers middleware (CSP, XFO, XCTO, Referrer-Policy, HSTS in prod).
- Logging upgraded to JSON + rotating file handler + request/user context.
- Database pool tuning added (`pool_size`, `max_overflow`, `pre_ping`, `recycle`).
- Added token revocation table/model and `/api/auth/logout` blacklist path.
- Added MIME/signature validation for uploads (`python-magic` + magic-byte fallback).
- Added citation PDF download allowlist + content-type/signature verification for SSRF risk reduction.
- Added Alembic second migration for auth/paper hardening.
- Added backend entrypoint migration hook (`alembic upgrade head` on startup).
- Added CI workflow (backend lint/test/build + frontend lint/build + docker build).
- Added frontend nginx cache/security header defaults.

## 3) Verification summary (this session)
- `python -m py_compile` passed for all modified backend modules, routers, schemas, alembic files.
- `npm run build` passed on frontend.
- `alembic upgrade head` passed locally (SQLite path) including new revision chain.
- Runtime API import smoke (`import api.main`) was not executable in this shell due missing local FastAPI package in the current Python environment.

## 4) Remaining work before public launch
Priority P0 (must before external exposure):
- Refresh token flow (short-lived access + refresh rotation).
- Move access token to httpOnly cookie + CSRF strategy.
- End-to-end HTTPS termination and strict secure-cookie path.
- Audit log table/events for login/upload/delete/auth failures.

Priority P1 (strongly recommended):
- Generator concurrency policy validation under load (429 behavior + queue metrics).
- Prompt injection defensive sanitization and boundary markers.

Priority P2 (quality/operations):
- Full Playwright E2E scenario pack.
- Locust load profile and SLO targets.
- BM25 tokenizer enhancement for Korean morphology-aware sparse retrieval.

## 5) Files with major changes
- Backend core: `backend/api/auth.py`, `backend/api/main.py`, `backend/api/database.py`, `backend/api/models.py`, `backend/api/schemas.py`
- Routers: `backend/api/routers/auth.py`, `chat.py`, `papers.py`, `history.py`, `citations.py`
- Retrieval: `backend/modules/hybrid_retriever.py`, `backend/modules/vector_store.py`
- Migrations/ops: `backend/alembic/*`, `backend/scripts/entrypoint.sh`, `backend/scripts/backup.sh`, `backend/Dockerfile`, `docker-compose.yml`, `.env.example`
- Frontend: `frontend/src/api/client.ts`, `frontend/src/types/api.ts`, `frontend/src/App.tsx`, `frontend/src/stores/authStore.ts`, `frontend/nginx.conf`
- CI: `.github/workflows/ci.yml`

## 6) Important implementation notes
- Some legacy docs in `docs/GUIDE/` remain as project baseline docs; this file is the single merged result for audit/plan/report context.
- Model/migration drift was reduced by introducing Alembic revision `20260414_000002`; fresh deploy should use Alembic-first startup path.
- Collection namespace migration may require re-upload or a one-time data migration for legacy records.

## 7) Claim re-verification notes (RAG/LLM findings)
- BM25 Korean tokenization claim corrected:
  - `\w+` does not split Hangul into jamo in Python 3.
  - Real issue is lack of morphology-aware segmentation for compound Korean terms, which can still reduce sparse recall.
- HyDE leakage claim is not treated as a confirmed blocker:
  - The quality risk remains possible via retrieval bias, but direct "HyDE text leak into final context" was not finalized as a proven invariant in this pass.
- Pipeline C "3-paper hard limit" claim corrected:
  - Current behavior was normalized to explicit pairwise mode (exactly two docs) to avoid ambiguous partial comparisons.
- CAD/SCD implementation exists, but production control gaps remain:
  - Cost/concurrency/timeout guardrails were added, yet deeper quality benchmarking for CAD/SCD parameter policy is still pending.

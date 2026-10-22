# 📚 Topic Depth Learning Sheet

**Purpose:** the single home for everything worth remembering — built for interview recall. Each day's row is flashcard material; the memorable numbers and one-liners are in the cells. Reading backlog items is optional depth, never a blocker.

**How this works (our working model):**
- **You code, I guide.** You stay hands-on and write the code; I review, explain, and unblock you.
- **Essential topics get saved, not sidetracked.** When a concept deserves deeper reading than the moment allows, I log just the **topic name** in [Saved for Later](#-saved-for-later-backlog).
- **One row per day**, filled in as the day happens: Commands · Topics · Algorithms · Libs/Tools · Concepts.

---

## 📖 Days 1–10

| Day | Commands | Topics | Algorithms | Libs / Tools | Concepts |
|-----|----------|--------|------------|--------------|----------|
| 1 — Architecture | — | system design basics; monolith vs serverless; tech-stack selection | — | Next.js, FastAPI, PostgreSQL, Redis, Gemini (selected) | MVP scoping; simplest architecture that works; "Build → Deploy → Observe → Break → Understand → Improve → Scale" |
| 2 — Scaffolding | `git init`; `npx create-next-app`; `python -m venv` | repo layout; frontend/backend separation | — | Next.js scaffold; FastAPI scaffold | `.gitignore`; secrets hygiene (`.env` vs `.env.example`) |
| 3 — Docker | `docker build`; `docker compose up/down`; `docker compose logs` | containerization; images vs containers; port mapping; volumes | — | Docker; Docker Compose | hot reload via volume mounts; `depends_on`; declarative env config |
| 4 — React frontend | `npm run dev` | Next.js App Router; layouts; client components; CORS | — | Next.js; React; TypeScript | CORS; REST calls from the browser; `fetch` |
| 5 — FastAPI endpoints | `bash scripts/test_api.sh`; `curl` | REST API design; request/response schemas; bearer auth | — | FastAPI; Pydantic; HTTPBearer | validation at the boundary; status codes; mock persistence; automated API testing |
| 6 — PostgreSQL + SQLAlchemy | `docker compose exec db psql` | ORM; connection pooling; foreign keys; cascade deletes | — | SQLAlchemy 2.0 (`Mapped`/`mapped_column`); psycopg; PostgreSQL | sessions & unit-of-work; `create_all` ≠ migrations; container DNS (service names as hostnames) |
| 7 — Cloud deployment | `gcloud run deploy`; `gcloud run services describe`; `gh secret set` | serverless (Cloud Run); serverless Postgres (Neon); connection pooling (PgBouncer); IAM service accounts; CI/CD GitOps; region alignment & latency | — | Google Cloud Run; Neon; GitHub Actions; Vercel; Artifact Registry | Docker `CMD` shell vs exec form; **CORS wildcard `*` + credentials conflict**; secrets management; pooling prevents connection exhaustion when serverless scales |
| 8 — Password auth | `openssl rand -hex 32` | password hashing; JWT anatomy (header.payload.signature); stateless auth; 401 vs 403; secret management | bcrypt (adaptive cost, built-in salt, ~100–250 ms/verify at cost 12, format `$2b$12$...`); base64url | general hashes (SHA) are **fast** → wrong for passwords; JWTs are **signed, not encrypted**; claims: `sub`/`iat`/`exp`; stateless ⇒ **no token revocation**; constant-time compare; vague login errors prevent user enumeration; DB is final authority, not the token; HS256 ⇒ ≥256-bit random secret (`openssl rand -hex 32`), weak secrets fail silently; rotating the secret = instant global logout |
| 9 — Authorization (RBAC) | `ALTER TABLE users ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT 'USER';`; `UPDATE users SET role='ADMIN' WHERE email=...` | RBAC; authorization vs authentication; dependency chaining; bootstrap problem | — | psql; DBeaver | **401 = unknown, 403 = known-but-not-allowed**; `create_all` never ALTERs existing tables (dev-only shortcut → Alembic on Day 16); never trust the client: role **never** from request body (privilege escalation); permissions attach to **roles, not users**; role read from **DB per request**, not JWT claims (claims go stale on demotion); first admin appointed **out-of-band**; "the privilege is the absence of the user_id filter" |
| 10 — JWT Deep Dive + Frontend Auth Integration | `POST /auth/refresh`; `POST /auth/logout`; `docker compose up -d --force-recreate backend` (env_file is read only at container CREATION - env changes need recreate, not restart!); `npx tsc --noEmit` | access vs refresh tokens; rotation; server-side logout; token theft window; **auto-refresh fetch wrapper**; session restore; client-side auth state | — | `secrets.token_urlsafe(48)`; SHA-256 for high-entropy tokens (bcrypt is only for low-entropy human passwords); Next 16: `'use client'`, `useRouter` from `next/navigation` | access = stateless JWT, **15 min**; refresh = **opaque + stateful DB row**, 7 days, stored **SHA-256 hashed**; **logout = revoke the refresh row** (access lives out its ≤15 min - accepted); rotation ⇒ replayed old refresh → 401 (reuse = theft signal); `.env` overrides code defaults — 60 was hiding our 15; **single-flight refresh** (concurrent 401s share one refresh promise - rotation would kill the rest); client 401 ⇒ refresh ⇒ retry once, callers never see expiry; **localStorage readable by any JS ⇒ httpOnly cookies + CSRF is the production pattern**; App Router: **layout stays mounted across navigation ⇒ auth state needs an explicit event** ("auth-changed"); **`NEXT_PUBLIC_API_URL` decides which backend the browser hits** — a Day-7 `.env.local` leftover silently pointed local dev at PROD (blank `role` in the response exposed it) |

---

## 🗓 Current Day

*Filled in as the day progresses.*

| Day | Commands | Topics | Algorithms | Libs / Tools | Concepts |
|-----|----------|--------|------------|--------------|----------|
| 11 — SQL Fundamentals | *(in progress)* | — | — | — | — |

---

## 📌 Saved for Later (backlog — read when you have time)

*Just topic names. Nothing here blocks current work.*

- Argon2 (memory-hard password hashing — the modern upgrade path from bcrypt)
- Token revocation strategies (denylist, short TTLs)
- Lazy password-hash migration (verify-on-login, then re-hash)
- Why python-jose vs PyJWT matters (library maintenance & CVE history)
- Alembic database migrations (`create_all` is a dev-only shortcut)
- OAuth2 / OpenID Connect
- Message queues (Celery/Redis) & background workers
- Vector databases & embeddings (the RAG core)
- LangChain / LangGraph
- Observability: structured logging, metrics, distributed tracing
- Kubernetes (deferred by design — only when there's a concrete reason)

# 📚 Topic Depth Learning Sheet

**Purpose:** the single home for everything worth remembering — built for interview recall. Each day's row is flashcard material; the memorable numbers and one-liners are in the cells. Reading backlog items is optional depth, never a blocker.

**How this works (our working model):**
- **You code, I guide.** You stay hands-on and write the code; I review, explain, and unblock you.
- **Essential topics get saved, not sidetracked.** When a concept deserves deeper reading than the moment allows, I log just the **topic name** in [Saved for Later](#-saved-for-later-backlog).
- **One row per day**, filled in as the day happens: Commands · Topics · Algorithms · Libs/Tools · Concepts.

---

## 📖 Days 1–8

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

---

## 🗓 Current Day

*Filled in as the day progresses.*

| Day | Commands | Topics | Algorithms | Libs / Tools | Concepts |
|-----|----------|--------|------------|--------------|----------|
| 9 — Authorization (RBAC) | *(in progress)* | RBAC; authorization vs authentication; permissions modeling | — | DBeaver (`localhost:5432`, db `mydb`) for browsing dev data | 401 vs 403 distinction in practice; least privilege |

---

## 📌 Saved for Later (backlog — read when you have time)

*Just topic names. Nothing here blocks current work.*

- Argon2 (memory-hard password hashing — the modern upgrade path from bcrypt)
- Refresh tokens & logout flows (Day 10)
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

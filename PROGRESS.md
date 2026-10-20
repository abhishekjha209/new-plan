# Progress Log

**Current Status:** Completed Day 8
**Next Up:** Start Day 9 (Authorization / RBAC) — Task 1: add `role` column to User model

## 🏆 What Has Been Accomplished (Days 1 - 8)

### 1. Architecture & Design (Day 1)
- Defined the product: **AI Knowledge Platform**
- Selected Tech Stack: Next.js (TypeScript), FastAPI (Python), PostgreSQL, Redis, Gemini API.
- Documented initial database schema (Users, Documents, Conversations, Messages).

### 2. Repository & Scaffolding (Day 2)
- Initialized Git repository.
- Created standard `.gitignore` and `.env` files.
- Scaffolded Next.js App Router in `frontend/`.
- Scaffolded basic FastAPI app in `backend/`.

### 3. Docker Containerization (Day 3)
- Created `frontend/Dockerfile` (Node.js/Next).
- Created `backend/Dockerfile` (Python/FastAPI).
- Configured `docker-compose.yml` to spin up:
  - Frontend (Port 3000)
  - Backend (Port 8000) - Configured for hot-reloading (`fastapi dev`).
  - PostgreSQL (Port 5432)
  - Redis (Port 6379)

### 4. React Frontend (Day 4)
- Created basic navigation in `layout.tsx`.
- Scaffolded UI pages for `/login`, `/chat`, and `/documents`.
- Added CORS middleware to FastAPI to allow browser requests.
- Successfully verified frontend-to-backend communication (fetch on `/` calling `/health`).

### 5. FastAPI Endpoints (Day 5)
- Completed `backend/schemas.py` defining full input and response validation schemas (Register, Login, Token, DocumentCreate, DocumentResponse, ChatRequest, ChatResponse).
- Created mock in-memory database in `backend/main.py`.
- Developed `HTTPBearer` security dependency to handle token extraction and user session mapping.
- Implemented core REST endpoints: `/auth/register`, `/auth/login`, `/users/me`, `/documents` (POST and GET), and `/chat` (POST with conversation thread support).
- Built a portable, automated cross-platform API integration test suite in `scripts/test_api.sh` and confirmed all endpoints pass validation.

### 6. PostgreSQL + SQLAlchemy (Day 6)
- Configured modern, object-oriented, type-safe relational database models in `backend/models.py` using SQLAlchemy 2.0 (`Mapped` and `mapped_column` type annotations).
- Configured robust database-level foreign keys, unique indexes, and cascade deletions (`ondelete="CASCADE"`).
- Set up engine, connection pooling, and request-scoped session factories (`SessionLocal` with auto-closing generators) in `backend/database.py`.
- Automated table creation on backend startup using SQLAlchemy metadata creation routines.
- Re-routed all API endpoints in `backend/main.py` to query, create, commit, and refresh data directly in PostgreSQL.
- Resolved docker-internal container-to-container network resolving using `docker-compose.yml` environment overrides.
- Experimentally verified persistent storage by restarting database and server services, successfully retrieving data from disk storage volumes.

### 7. Cloud Deployment Blueprint (Day 7)
- **High-Performance Production Dockerization:** Upgraded `backend/Dockerfile` to use a production-grade **Uvicorn** server instead of local `fastapi dev` tools. Configured the startup command in **Shell Execution Form** (`CMD uvicorn ...`) rather than Exec Form to allow dynamic shell expansion of the `$PORT` environment variable dynamically injected by the Google Cloud Run load balancer, defaulting to `8080`.
- **Dynamic CORS Isolation:** Modernized `backend/main.py` to parse allowed CORS origins dynamically from the `ALLOWED_ORIGINS` environment variable. This securely decouples local development on `localhost:3000` from your public web clients, preventing browser cross-origin blocking.
- **Dynamic Frontend Integration:** Refactored the Next.js Home Page to read the backend API URL dynamically via `NEXT_PUBLIC_API_URL` environment variables. Created a local frontend config file (`frontend/.env.local`) to redirect your local browser client across the internet to your live cloud server with zero code changes.
- **Enterprise Multi-Cloud Region Alignment:**
  - Aligned our Google Cloud Run deployment region to GCP Ohio (`us-east5`) to match our serverless Neon PostgreSQL database (AWS Ohio `us-east-2`), collapsing database socket roundtrip latency from ~40ms down to **~2ms**.
  - Leveraged Neon's **Connection Pooler (`DATABASE_URL_POOLED`)** (PgBouncer proxy) to manage connection reuse dynamically, preventing database connection exhaustion as serverless containers scale horizontally.
- **Enterprise GCP IAM Robot Setup:**
  - Created a dedicated robot deployer identity named **`github-deployer`** inside the GCP IAM Console.
  - Granted the service account the **5 specific permissions (Roles)** required for automated deployment clearance:
    1. `Cloud Run Admin` (Allows updating Cloud Run services)
    2. `Storage Admin` (Allows uploading backend source code bundles)
    3. `Cloud Build Editor` (Allows triggering cloud-based container compilation)
    4. `Artifact Registry Administrator` (Allows storing built container images)
    5. `Service Account User` (Required to bind Cloud Run to default compute identities)
  - Generated and downloaded a private cryptographic authentication key in **JSON** format.
- **Automated CI/CD GitOps Pipeline:**
  - Designed and configured `.github/workflows/deploy.yml` to trigger automated builds whenever code is pushed to the `main` branch.
  - Integrated steps to checkout code, authenticate with GCP using Google's Auth Action via the `GCP_SA_KEY` secret, configure Docker, and execute remote serverless builds on Google Cloud Run with dynamic environmental injections.
  - Securely configured **GitHub Encrypted Repository Secrets** to manage:
    * `GCP_PROJECT_ID` (`ai-platform-98765`)
    * `DATABASE_URL` *(Your Neon pooled connection string)*
    * `GCP_SA_KEY` *(The entire downloaded GCP JSON Key text)*
- **LIVE DEPLOYMENT SUCCESS:** Built, verified, and pushed our serverless container live to Google Cloud Run! The API is serving public traffic live at: **`https://ai-knowledge-api-610287324530.us-east5.run.app/health`**.

### 7.5. Production CORS & CI/CD Pipeline Automation (Hotfix & Enhancement)
- **Safe Wildcard Credentials Matching:** Resolved a standard browser security conflict where browsers reject CORS responses containing both `Access-Control-Allow-Origin: *` and `Access-Control-Allow-Credentials: true`. Upgraded the FastAPI backend in `backend/main.py` to automatically detect a wildcard `*` configuration and seamlessly translate it to `allow_origin_regex=".*"`. This dynamically mirrors back the browser's requesting origin, allowing credentialed API calls to succeed flawlessly.
- **Semicolon Delimiter Support for CLI:** Introduced semicolon delimiter support (`ALLOWED_ORIGINS=https://my-frontend.vercel.app;http://localhost:3000`) on the backend. This gracefully bypasses the Google Cloud SDK CLI parsing issue where commas are treated as environment variable separators, avoiding deployment script failures.
- **Automated URL Resolution in GitHub Actions:** Integrated dynamic URL discovery directly inside the `.github/workflows/deploy.yml` pipeline. Upon deploying the backend to Google Cloud Run, the pipeline automatically queries, extracts, and prints the live service URL:
  ```bash
  BACKEND_URL=$(gcloud run services describe ai-knowledge-api --region us-east5 --format="value(status.url)")
  ```
- **Automated Frontend GitOps Rebuild:** Connected your frontend and backend deployment lifecycles by adding a dynamic Vercel Deployment Action step to the GitHub Actions workflow. When secrets are configured (`VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID`), the pipeline automatically updates your frontend's `NEXT_PUBLIC_API_URL` environment variable on Vercel and triggers a clean production rebuild of the Next.js application, completely automating your end-to-end deployment on push.

### 8. Password Authentication (Day 8)
- New `backend/auth.py` module: `hash_password` / `verify_password` (bcrypt) and `create_access_token` / `decode_access_token` (PyJWT, HS256). Missing `JWT_SECRET` falls back to an ephemeral per-process secret with a loud warning — dev still works, but tokens die on restart.
- `POST /auth/register` bcrypt-hashes before persisting — plaintext never touches the DB. `POST /auth/login` verifies with bcrypt (constant-time, vague "Incorrect email or password" for both failure modes so we don't leak which accounts exist) and issues a signed JWT instead of the old `mock-session-token-{id}` string.
- `get_current_user` verifies signature + expiry via PyJWT and resolves the user from the `sub` claim against PostgreSQL (DB remains the final authority - deleted users' tokens die).
- `HTTPBearer(auto_error=False)`: missing `Authorization` header now returns RFC-correct **401** with `WWW-Authenticate: Bearer` instead of Starlette's default 403.
- Config plumbing: `JWT_SECRET` + `JWT_EXPIRE_MINUTES` (default 60) documented in `.env.example` and injected into Cloud Run via `.github/workflows/deploy.yml` (`JWT_SECRET` GitHub secret).
- Verified end-to-end: old mock tokens, no header, attacker-forged token, and wrong password all → 401; expired token (real secret, past `exp`) → `ExpiredSignatureError` → 401 "Token has expired"; decoded a live token's payload with plain base64 to prove JWTs are readable — only `sub`/`iat`/`exp` inside; DB inspection: password column holds `$2b$12$...`, zero plaintext; login latency ~0.4s vs instant string compare (bcrypt cost visible).
- Engineering decisions: bcrypt over argon2 for Day 8 (simpler to reason about first; argon2 noted as the modern memory-hard upgrade path — in the Learning Sheet backlog); PyJWT over python-jose (jose has maintenance/CVE history; PyJWT is clean and current); wiped the 6 plaintext users instead of building throwaway migration machinery (real-world lazy migration pattern discussed and shelved); fixed a latent Day 7 regression — the production Dockerfile change (`uvicorn ${PORT:-8080}`) had silently broken `docker compose up` (compose mapped 8000:8000, server listened on 8080), so compose now overrides with `fastapi dev main.py --port 8000` for hot reload.
- Concepts learned (why SHA is wrong for passwords, bcrypt cost/salt, JWT anatomy `header.payload.signature` signed-not-encoded, stateless revocation tradeoff, 401 vs 403) are logged in the Day 8 row of `docs/Learning-Sheet.md`.

## 🚀 Next Steps for New Session (Day 9)
Begin **Day 9: Authorization (RBAC)** — distinguish authentication (who are you, done Day 8) from authorization (what are you allowed to do). Introduce `USER` / `ADMIN` roles, restrict admin APIs, and learn permissions modeling.

- [ ] Task 1 (in progress): add `role` column to User model (`USER` default) — mind the `create_all` wall
- [ ] Task 2: `require_admin` dependency
- [ ] Task 3: admin-only endpoint + verify 403 vs 200 with curl

## ⏳ Still To Do (user actions before next deploy)
- [x] Add `JWT_SECRET` (generate: `openssl rand -hex 32`) to local `.env`. *(done 2026-10-20 via `gh`)*
- [x] Create the `JWT_SECRET` secret in GitHub repo settings (needed by deploy.yml). *(done 2026-10-20 via `gh secret set`)*
- [ ] Optionally `DELETE FROM users;` on the live Neon DB (old plaintext users are already locked out - bcrypt verify fails - but removing them is tidier).
- [ ] With `JWT_SECRET` set, re-run the expired-token curl live to see the 401 "Token has expired" path end-to-end.

# Progress Log

**Current Status:** Completed Day 6
**Next Up:** Start Day 7 (First Deployment)

## 🏆 What Has Been Accomplished (Days 1 - 6)

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

## 🚀 Next Steps for New Session (Day 7)
In the next session, begin with **Day 7: First Deployment**. 
The goal is to deploy our React frontend, FastAPI backend, and PostgreSQL database live to a real cloud URL!



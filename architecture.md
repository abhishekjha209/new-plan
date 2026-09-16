# Architecture

## Tech Stack
- **Frontend:** Next.js + TypeScript
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL
- **AI/LLM:** Gemini API, LangChain LangGraph

## Phase 1 Architecture Flow
In our first phase, we are keeping it as simple as possible. No queues, no caching, no vector databases yet.

```mermaid
flowchart TD
    Client[Frontend Browser] -->|HTTP REST| API[Backend API]
    API -->|Read/Write| DB[(PostgreSQL)]
    API -->|Prompt| LLM[LLM API]

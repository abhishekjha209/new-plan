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

## Initial Database Schema

**Users** 
- `id` (Primary Key)
- `email` (Unique)
- `password_hash` (Never store plain text passwords!)
- `name`
- `created_at`

**Documents**
- `id` (Primary Key)
- `user_id` (Foreign Key -> Users.id)
- `filename`
- `content` (Text)
- `created_at`
- `updated_at`

*Conversations**
- `id` (Primary Key)
- `user_id` (Foreign Key -> Users.id)
- `document_id` (Foreign Key -> Documents.id)
- `created_at`

**Messages**
- `id` (Primary Key)
- `conversation_id` (Foreign Key -> Conversations.id)
- `role` ("user" or "ai")
- `content` (Text)
- `created_at`

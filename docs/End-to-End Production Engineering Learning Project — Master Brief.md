# End-to-End Production Engineering + AI Engineering Project

## 1. My Goal

I want to build **one complete end-to-end application from scratch** that teaches me how a real production system is designed, built, deployed, operated, scaled, debugged, and evolved.

My goal is **not** to build the most complicated system possible.

My goal is to build a relatively simple product and progressively introduce real engineering concepts so that I understand the **entire flow deeply**.

I want to eventually be comfortable discussing and working with:

- Frontend
- Backend
- APIs
- Authentication / authorization
- SQL
- PostgreSQL
- Transactions
- Indexing
- Query optimization
- Connection pooling
- Caching
- Redis
- Background workers
- Queues
- Async processing
- Load balancing
- Reverse proxies
- Networking
- Docker
- Multiple environments
- CI/CD
- Cloud deployment
- Kubernetes
- Horizontal scaling
- Observability
- Logging
- Metrics
- Distributed tracing
- Load testing
- Failure handling
- Database migrations
- Backups / recovery
- Read replicas
- Distributed systems concepts
- LLM integration
- LLM hosting
- RAG
- BM25
- Vector search
- Hybrid search
- Reranking
- Agents
- Tool calling
- Durable execution
- LLM evaluation
- LLM latency / cost / reliability

---

# 2. Learning Philosophy

I want to learn this **by actually building and operating the system**, not by consuming theory first.

The project should follow this philosophy:

> Build → Deploy → Observe → Break → Understand → Improve → Scale

I want to make **one meaningful win every day**.

I can spend approximately:

- **1 hour/day normally**
- **Up to 2 hours/day when needed**

I want the complete roadmap to fit approximately **1–2 months**, with the ability to continue expanding the system afterward.

---

# 3. Very Important Constraint: Do Not Over-Engineer

I do NOT want to start with:

- Kubernetes
- Kafka
- 10 microservices
- Redis Cluster
- Multiple databases
- Complex event-driven architecture
- Service mesh
- Distributed systems everywhere

Instead, start with the **simplest architecture that works**.

Then introduce complexity only when there is a reason to do so.

For example:

```text
Start:

Frontend
   ↓
Backend
   ↓
PostgreSQL
   ↓
LLM
```

Later:

```text
Frontend
   ↓
Load Balancer
   ↓
Reverse Proxy
   ↓
Multiple API instances
   ↓
Redis
   ↓
PostgreSQL
   ↓
Workers
   ↓
Queue
   ↓
Vector DB
   ↓
LLM
```

Later:

```text
Kubernetes
├── API pods
├── Worker pods
├── Ingress
├── Autoscaling
└── Rolling deployments
```

Every additional component must have a clear reason.

---

# 4. The Product I Want to Build

Build a relatively small **AI Knowledge / Documentation Platform**.

Think of it as a small internal company knowledge system.

Users should eventually be able to:

1. Register
2. Login
3. Authenticate using JWT
4. Have roles / permissions
5. Upload documents
6. Search documents
7. Ask questions about documents
8. Receive RAG-based answers
9. See citations / sources
10. Have conversations
11. Resume previous conversations
12. Search using keyword + semantic search
13. Use reranking
14. Trigger agentic workflows when appropriate
15. See basic usage / latency information

Admins should eventually be able to:

- Upload documents
- Delete documents
- View ingestion status
- Manage users / permissions
- Inspect failures

The product itself does not need to become huge.

The **engineering underneath it** is the main learning objective.

---

# 5. Desired Final Architecture

The final system should eventually resemble something like:

```text
                         Internet
                            │
                            ▼
                       DNS / HTTPS
                            │
                            ▼
                     Load Balancer
                            │
                            ▼
                     Reverse Proxy
                         Nginx
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
             API Pod 1              API Pod 2
                 │                     │
                 └──────────┬──────────┘
                            │
          ┌─────────────────┼──────────────────┐
          ▼                 ▼                  ▼
      PostgreSQL          Redis             Vector DB
          │
          │
          ▼
    Background Queue
          │
          ▼
       Workers
          │
     ┌────┼─────────┐
     ▼    ▼         ▼
   OCR  Chunking  Embeddings
                         │
                         ▼
                     Vector DB


User Query
    │
    ▼
Query Processing
    │
    ├──────────► BM25
    │
    └──────────► Vector Search
                       │
                       ▼
                    Hybrid
                    Retrieval
                       │
                       ▼
                    Reranker
                       │
                       ▼
                     Context
                       │
                       ▼
                      LLM
                       │
                       ▼
                    Response
                       │
                       ▼
                    Frontend
```

This is the **eventual destination**, not the starting architecture.

---

# 6. Technology Direction

I am primarily interested in:

## Frontend

- React
- TypeScript
- Basic state management
- API integration
- Authentication
- Streaming responses
- Error handling
- Production build

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- REST APIs
- Async Python

## Database

- PostgreSQL
- SQL
- SQLAlchemy
- Alembic

## Cache

- Redis

## AI

- LLM APIs initially
- Embeddings
- Vector database
- BM25
- Hybrid retrieval
- Reranking
- RAG
- Tool calling
- Agents
- LangGraph or equivalent
- Local LLM hosting
- vLLM / Ollama exploration

## Infrastructure

- Docker
- Docker Compose
- Nginx
- Cloud deployment
- Kubernetes
- GitHub Actions / CI/CD

## Testing

- Pytest
- API/integration testing
- Load testing using k6 or equivalent

## Observability

- Structured logging
- Metrics
- Tracing
- Request IDs
- Latency measurements

Exact technology choices should be evaluated rather than assumed.

---

# 7. How I Want the LLM to Help Me

I want to use an LLM heavily, but **I do not want the LLM to make all the engineering decisions for me.**

Treat the LLM as a:

> Senior engineer + mentor + reviewer + interviewer

Not as:

> Code generator that builds the project for me.

---

# 8. Decision-Making Rule

I want to make the important decisions myself.

Before implementing a component, I should first explain:

```text
What am I building?

Why do I need it?

What alternatives exist?

Why am I choosing this?

What are the failure modes?

What happens at 10x traffic?

What state does it own?

How will I observe it?

How will I test it?
```

The LLM should **challenge my decision**, point out missing considerations, and explain alternatives.

It should not immediately give me the answer.

---

# 9. Preferred LLM Workflow

For each feature:

### Step 1 — I propose the design

Example:

```text
I think I should use Redis cache-aside for document metadata.

My reasoning is:
...

Challenge this design.
Don't give me implementation yet.
```

### Step 2 — LLM critiques it

Identify:

- Missing considerations
- Failure modes
- Scaling issues
- Security issues
- Consistency issues
- Operational issues

### Step 3 — I make the final decision

I update my architecture.

### Step 4 — Learn the required concepts

Ask the LLM to explain concepts I don't understand.

### Step 5 — I implement

I should write most of the code myself.

### Step 6 — LLM reviews

Give the implementation to the LLM and ask for:

- Bugs
- Race conditions
- Security issues
- Performance issues
- Maintainability problems
- Production risks

### Step 7 — I test it

Especially by intentionally breaking things.

---

# 10. One-Win-a-Day System

Every day should have a small, concrete outcome.

Each day should follow:

```text
Today's Goal:

Concept:

What I will build:

What I need to understand:

Experiment:

How I will verify it:

What can I intentionally break:

What I learned:

Engineering decision:
```

The daily goal should be achievable in approximately **1–2 hours**.

Do not give me unrealistic daily workloads.

---

# 11. Deployment Philosophy

Deployment is extremely important to me.

I want to get something **live very early**.

I do NOT want to spend several weeks building locally before deployment.

The first version should be deployed as soon as it is useful.

Then I want to progressively evolve the deployed system.

For example:

```text
Local MVP
    ↓
Dockerized
    ↓
Live deployment
    ↓
Production-like environment
    ↓
Caching
    ↓
Load testing
    ↓
Observability
    ↓
Multiple instances
    ↓
CI/CD
    ↓
Kubernetes
    ↓
Autoscaling
    ↓
Failure testing
```

The system should remain live while it evolves whenever practical.

---

# 12. Environments

I want to eventually have:

```text
development
staging
production
```

I want to understand:

- Environment variables
- Secrets
- Configuration
- Database configuration
- Deployment configuration
- Feature flags
- Different API endpoints
- Safe migrations
- Production configuration

---

# 13. Database Topics I Must Learn

Do not skip these.

## SQL

- SELECT
- JOINs
- GROUP BY
- HAVING
- CTEs
- Subqueries
- Window functions
- Aggregations
- Pagination

## PostgreSQL

- Schema design
- Primary keys
- Foreign keys
- Constraints
- Indexes
- Composite indexes
- Partial indexes
- EXPLAIN
- EXPLAIN ANALYZE
- Query optimization
- Transactions
- ACID
- Isolation levels
- Locks
- Deadlocks
- Connection pooling
- Migrations
- Backups
- Restore
- Replication
- Read replicas
- Partitioning

I should actually reproduce some problems instead of only reading about them.

---

# 14. Caching Topics

I want to understand:

- Why caching exists
- Cache-aside
- TTL
- Eviction
- Cache invalidation
- Cache stampede
- Cache consistency
- Distributed locks
- Rate limiting
- Session storage
- Redis data structures

I should measure:

```text
Cache hit rate
Cache miss rate
Latency
DB load
```

---

# 15. Backend Topics

I should understand:

- HTTP
- REST
- Status codes
- Middleware
- Dependency injection
- Validation
- Serialization
- Error handling
- Pagination
- Authentication
- Authorization
- JWT
- OAuth basics
- CORS
- Rate limiting
- Idempotency
- Retries
- Timeouts
- Async processing
- SSE
- WebSockets basics
- Graceful shutdown

---

# 16. Networking Topics

I should understand enough networking to trace a request:

```text
Browser
 ↓
DNS
 ↓
TCP/TLS
 ↓
Load Balancer
 ↓
Reverse Proxy
 ↓
Application
 ↓
Database
```

Topics:

- DNS
- HTTP
- HTTPS
- TLS
- TCP basics
- Ports
- Connections
- Keep-alive
- Reverse proxy
- Load balancer
- CDN
- Timeouts
- Connection pooling

I don't need to become a network specialist.

I need to understand the request path.

---

# 17. Distributed Systems Topics

Focus on practical concepts:

- Synchronous vs asynchronous processing
- Queues
- Workers
- Retries
- Exponential backoff
- Jitter
- Timeouts
- Circuit breakers
- Idempotency
- At-least-once delivery
- Duplicate processing
- Dead-letter queues
- Horizontal scaling
- Replication
- Eventual consistency
- Read-after-write consistency

Do not introduce distributed systems complexity just for the sake of it.

---

# 18. AI Engineering Topics

The AI portion should eventually include:

## LLM

- API integration
- Streaming
- Token usage
- Context windows
- Temperature
- Latency
- Cost
- Timeouts
- Retries
- Fallback models

## RAG

- Document ingestion
- Parsing
- Chunking
- Metadata
- Embeddings
- Vector search
- Metadata filtering
- Retrieval evaluation

## Search

- BM25
- Dense retrieval
- Sparse retrieval
- Hybrid retrieval
- Reciprocal Rank Fusion
- ANN
- HNSW

## Reranking

Understand:

- Bi-encoder
- Cross-encoder
- Reranker
- Why reranking helps
- Latency tradeoffs

## Agents

- Tool calling
- Agent state
- Planning
- Tool execution
- State machines
- LangGraph
- Checkpoints
- Interrupts
- Retries
- Durable execution

## Production AI

- Prompt injection
- PII
- Hallucination
- Evaluation
- Retrieval quality
- Model failures
- Cost monitoring
- Latency monitoring
- Model fallback
- Guardrails

---

# 19. LLM Hosting

I want to understand the difference between:

```text
Calling a hosted LLM API
```

and:

```text
Hosting an LLM myself
```

Eventually experiment with:

- Ollama
- vLLM
- GPU inference
- Batching
- KV cache
- Prefill
- Decode
- TTFT
- Tokens/sec
- Quantization
- Model memory requirements

I want to measure the difference rather than only learn it theoretically.

---

# 20. Observability

The system should eventually expose:

```text
Request count
Error rate
p50 latency
p95 latency
p99 latency
CPU
Memory
DB connections
Cache hit rate
Queue depth
Worker failures
LLM latency
LLM token usage
LLM cost
```

I should be able to answer:

> "Why was this request slow?"

by looking at actual telemetry.

---

# 21. Load Testing

Load testing is a major part of this project.

Start small:

```text
10 users
50 users
100 users
```

Then:

```text
500 users
1000 users
```

I want to understand:

- Throughput
- Latency
- p50
- p95
- p99
- Error rate
- CPU bottlenecks
- Memory bottlenecks
- DB bottlenecks
- Connection pool exhaustion
- Cache effectiveness
- Queue backlog

The goal is not to achieve an arbitrary number.

The goal is:

> Generate load → observe bottleneck → form hypothesis → fix → retest.

---

# 22. Kubernetes

Kubernetes should come **after I understand the underlying application.**

Topics:

- Pod
- Deployment
- Service
- Ingress
- ConfigMap
- Secret
- Namespace
- Readiness probe
- Liveness probe
- Rolling deployment
- Horizontal Pod Autoscaler
- Resource requests/limits
- Graceful shutdown

I want to actually:

1. Deploy the application
2. Run multiple pods
3. Kill a pod
4. Watch it recover
5. Generate load
6. Trigger autoscaling
7. Deploy a new version
8. Observe rolling deployment

---

# 23. CI/CD

Eventually:

```text
git push
   ↓
tests
   ↓
lint
   ↓
build
   ↓
Docker image
   ↓
registry
   ↓
deployment
```

I want to understand the complete path from:

> `git push`

to:

> new production version running.

---

# 24. Failure Engineering

I want to intentionally break the system.

Examples:

```text
Redis goes down
Postgres goes down
LLM times out
Worker crashes
Queue gets backed up
API pod dies
Database connection pool gets exhausted
Duplicate request arrives
Network becomes slow
External API returns 500
```

For every failure:

```text
What happens?
Why?
Is the behavior acceptable?
How should it recover?
How do I observe it?
```

---

# 25. Migration and Evolution

I specifically want to understand how a system evolves.

For example:

```text
Version 1

API → PostgreSQL
```

Then:

```text
Version 2

API → Redis → PostgreSQL
```

Then:

```text
Version 3

API → Queue → Worker → PostgreSQL
```

Then:

```text
Version 4

API → Search + Vector DB
```

Then:

```text
Version 5

Kubernetes + multiple API pods
```

I want to understand **why the architecture changed at every stage.**

---

# 26. What I Do NOT Want

Do not:

- Give me a giant codebase upfront.
- Give me all implementation at once.
- Introduce technologies just because they are popular.
- Create microservices unnecessarily.
- Use Kafka when a simple queue is sufficient.
- Use Kubernetes before there is a reason.
- Hide complexity behind libraries.
- Tell me "this is production ready" without evidence.
- Let me blindly copy architecture diagrams.
- Optimize things before measuring them.

If something is unnecessary, explicitly say:

> "Don't build this yet."

---

# 27. What I Want From the Roadmap

Create a roadmap of approximately **6–8 weeks**.

Assume:

```text
1–2 hours/day
```

For every day provide:

```text
Day
Goal
Estimated time
Concepts
Implementation task
Experiment
Expected outcome
```

Organize it into phases such as:

```text
Phase 1 — MVP + deployment
Phase 2 — Database engineering
Phase 3 — Caching + performance
Phase 4 — RAG/search
Phase 5 — Agents + durable execution
Phase 6 — Production engineering
Phase 7 — Kubernetes
Phase 8 — Load testing + failure engineering
```

The ordering can change if there is a better learning progression.

---

# 28. Important: Deployment Early

I want the first meaningful version **live within the first week**.

Do not postpone deployment until the end.

After the first deployment, every major phase should ideally improve the same live system.

---

# 29. My Definition of Success

At the end of this project, I should be able to take a request such as:

> "Build a production system where users can search 10 million documents and ask an AI questions about them."

and independently reason about:

```text
Frontend
API
Authentication
Database
Schema
Indexes
Transactions
Caching
Queues
Workers
Search
Vector DB
BM25
Reranking
LLM
Agents
Latency
Throughput
Load balancing
Scaling
Observability
Security
Deployment
CI/CD
Kubernetes
Failures
Backups
Migrations
Cost
```

More importantly, I should be able to explain:

> **Why I chose each component, what alternatives existed, what can go wrong, and how I would find and fix the problem.**

---

# 30. Final Principle

The objective is not:

> "Build a fancy AI project."

The objective is:

> **Use one real application as a laboratory for learning the complete software engineering lifecycle.**

I want to go from:

```text
Nothing
  ↓
Code
  ↓
Local application
  ↓
Docker
  ↓
Live application
  ↓
Database
  ↓
Caching
  ↓
Async processing
  ↓
AI/RAG
  ↓
Agents
  ↓
Observability
  ↓
Load testing
  ↓
Scaling
  ↓
Kubernetes
  ↓
CI/CD
  ↓
Failure recovery
  ↓
Production system
```

The system can remain relatively simple.

**The depth of my understanding should come from repeatedly building, measuring, breaking, and improving it.**
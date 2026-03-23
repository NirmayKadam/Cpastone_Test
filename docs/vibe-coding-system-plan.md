# Quantitative Derivatives Terminal: Phased Vibe Coding System Plan

## 1. Definition: “Vibe Coding” for This Project

In this terminal project, **vibe coding** means an **AI-assisted, modular, iterative, feedback-driven developer workflow** where engineers:

1. Build one service boundary at a time instead of generating the whole platform in one pass.
2. Use reusable prompts to scaffold files, write interfaces, generate tests, and review architecture decisions.
3. Validate each phase with deterministic checks, integration tests, and observability signals before moving forward.
4. Keep services loosely coupled through event contracts instead of direct code dependencies.
5. Use AI as a force multiplier for implementation speed, but require human review for architecture, numerical correctness, latency budgets, and production safety.

**Operating rule:** AI may accelerate implementation, but the system only advances when a phase meets explicit exit criteria. No downstream phase starts until upstream contracts, tests, and deployment paths are stable.

---

## 2. Non-Negotiable System Constraints

The workflow must enforce the following across every phase:

- **Architecture:** strict event-driven microservices using **Redis Streams and/or Kafka pub-sub**.
- **Coupling:** quant, ML, API, and UI remain independently deployable and communicate only through contracts.
- **Latency:** target **< 50 ms tick-to-dashboard** for the real-time path.
- **Throughput:** support **100+ option strikes/sec**.
- **Concurrency:** async-first ingestion and inference using **Python AsyncIO**.
- **Quant performance:** parallel PDE computation using **Numba/vectorization**, with optional GPU for ML.
- **APIs:** **FastAPI** for REST + WebSockets.
- **Data separation:**
  - **TimescaleDB** for tick/time-series data.
  - **Redis** for messaging and cache.
  - **PostgreSQL** for metadata and control-plane state.
- **Frontend:** React + TypeScript + Tailwind + Plotly with a **60 FPS** rendering target.
- **Infra:** Docker, Kubernetes, GitHub Actions.
- **Cloud:** AWS or Azure with scalable compute and GPU-enabled ML workers when needed.
- **Observability:** structured logging, metrics, tracing.
- **Resilience:** graceful degradation, retries, dead-letter handling, and health checks.
- **Validation:** quant outputs must be deterministic and reproducible.
- **Workflow discipline:** no phase overlap; each phase exits cleanly before the next begins.

---

## 3. Target Monorepo Structure

The build begins with a **microservices monorepo** so contracts, deployment assets, CI, and shared schemas evolve together while services remain independently deployable.

```text
quant-terminal/
├─ apps/
│  ├─ api-gateway/
│  │  ├─ app/
│  │  │  ├─ api/
│  │  │  ├─ core/
│  │  │  ├─ schemas/
│  │  │  ├─ services/
│  │  │  └─ main.py
│  │  ├─ tests/
│  │  ├─ Dockerfile
│  │  └─ requirements.txt
│  ├─ market-data-service/
│  │  ├─ app/
│  │  │  ├─ adapters/
│  │  │  ├─ api/
│  │  │  ├─ pipelines/
│  │  │  ├─ schemas/
│  │  │  ├─ streams/
│  │  │  └─ main.py
│  │  ├─ tests/
│  │  ├─ Dockerfile
│  │  └─ requirements.txt
│  ├─ quant-engine/
│  │  ├─ app/
│  │  │  ├─ api/
│  │  │  ├─ greeks/
│  │  │  ├─ models/
│  │  │  ├─ pde/
│  │  │  ├─ schemas/
│  │  │  ├─ workers/
│  │  │  └─ main.py
│  │  ├─ tests/
│  │  ├─ Dockerfile
│  │  └─ requirements.txt
│  ├─ ml-service/
│  │  ├─ app/
│  │  │  ├─ api/
│  │  │  ├─ features/
│  │  │  ├─ inference/
│  │  │  ├─ training/
│  │  │  ├─ registry/
│  │  │  └─ main.py
│  │  ├─ tests/
│  │  ├─ Dockerfile
│  │  └─ requirements.txt
│  ├─ frontend/
│  │  ├─ src/
│  │  │  ├─ components/
│  │  │  ├─ features/
│  │  │  ├─ hooks/
│  │  │  ├─ pages/
│  │  │  ├─ services/
│  │  │  ├─ state/
│  │  │  └─ types/
│  │  ├─ public/
│  │  ├─ Dockerfile
│  │  └─ package.json
│  └─ worker-orchestrator/
│     ├─ app/
│     │  ├─ celery_app.py
│     │  ├─ jobs/
│     │  ├─ routing/
│     │  └─ main.py
│     ├─ tests/
│     ├─ Dockerfile
│     └─ requirements.txt
├─ libs/
│  ├─ event-schemas/
│  │  ├─ python/
│  │  ├─ jsonschema/
│  │  └─ avro/
│  ├─ quant-core/
│  │  ├─ finite_difference/
│  │  ├─ stochastic_vol/
│  │  └─ tests/
│  ├─ ml-core/
│  │  ├─ datasets/
│  │  ├─ evaluation/
│  │  └─ tests/
│  ├─ observability/
│  │  ├─ logging/
│  │  ├─ metrics/
│  │  └─ tracing/
│  └─ common-config/
│     ├─ settings/
│     └─ security/
├─ infra/
│  ├─ docker/
│  │  ├─ compose/
│  │  └─ base-images/
│  ├─ k8s/
│  │  ├─ base/
│  │  ├─ overlays/dev/
│  │  ├─ overlays/staging/
│  │  └─ overlays/prod/
│  ├─ terraform/
│  │  ├─ aws/
│  │  └─ azure/
│  └─ github-actions/
├─ configs/
│  ├─ env/
│  ├─ logging/
│  ├─ mlflow/
│  └─ prometheus/
├─ scripts/
│  ├─ bootstrap/
│  ├─ dev/
│  ├─ test/
│  └─ release/
├─ docs/
│  ├─ architecture/
│  ├─ runbooks/
│  └─ vibe-coding-system-plan.md
├─ .env.example
├─ docker-compose.yml
├─ Makefile
├─ pyproject.toml
└─ README.md
```

### Service Boundaries

| Service | Responsibility | Inputs | Outputs | Must Not Own |
|---|---|---|---|---|
| market-data-service | Connect to NSE feeds, normalize ticks, validate payloads, publish events | raw websocket frames, control commands | normalized tick events, preprocessing events | pricing logic, ML inference, UI state |
| quant-engine | Consume normalized market events, run Black-Scholes/Heston PDE pricing, compute Greeks | normalized ticks, instrument metadata, solver requests | price surface events, Greeks events, solver diagnostics | feed connectivity, model training, frontend rendering |
| ml-service | Train volatility models offline, serve async real-time inference | feature events, historical training sets, model registry refs | volatility forecasts, residual corrections, evaluation metrics | exchange adapters, PDE solving, direct DB writes for ticks |
| api-gateway | Unified REST/WebSocket access, auth, fan-out to frontend | client requests, service events | dashboard streams, command requests | heavy compute, long-running training jobs |
| worker-orchestrator | Celery-based background workflows and scheduled jobs | task events, cron schedules | preprocessing jobs, retraining jobs, backfills | public API exposure |
| frontend | Render terminal views, option chain, volatility surfaces, Greeks heatmaps | websocket streams, REST queries | user commands, dashboard interactions | direct quant logic, direct broker/feed integrations |
| infra/shared libs | Shared contracts, observability, deployment automation | repo-managed config | reusable packages/assets | service-specific business behavior |

### Docker Strategy

Each service gets its own Dockerfile to preserve independent deployment. Use multi-stage builds where appropriate.

**Service-level Dockerfile pattern:**

```dockerfile
FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile pattern:**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

### `docker-compose.yml` Baseline

The initial composition should include:

- api-gateway
- market-data-service
- quant-engine
- ml-service
- worker-orchestrator
- frontend
- redis
- timescaledb
- postgres
- mlflow
- prometheus
- grafana
- jaeger

**Development rule:** start with compose for local integration, then mirror the same boundaries in Kubernetes manifests under `infra/k8s`.

### `.env` Structure

Use a single root `.env.example`, grouped by service. Real deployments split secrets into environment-specific stores.

```env
# -----------------------------
# GLOBAL
# -----------------------------
APP_ENV=development
LOG_LEVEL=INFO
TRACE_ENABLED=true
METRICS_ENABLED=true
REDIS_URL=redis://redis:6379/0
POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/metadata
TIMESCALE_URL=postgresql://postgres:postgres@timescaledb:5432/ticks
MLFLOW_TRACKING_URI=http://mlflow:5000
EVENT_BACKBONE=redis-streams
LATENCY_BUDGET_MS=50
TARGET_STRIKES_PER_SEC=100

# -----------------------------
# DATA SERVICE
# -----------------------------
NSE_WS_URL=wss://example-nse-feed
NSE_API_KEY=
DATA_STREAM_TICK_TOPIC=market.ticks.normalized
DATA_STREAM_CONTROL_TOPIC=market.control
DATA_STREAM_DLQ_TOPIC=market.ticks.dlq
PREPROCESS_BATCH_SIZE=500
NORMALIZATION_TIMEZONE=Asia/Kolkata

# -----------------------------
# QUANT ENGINE
# -----------------------------
QUANT_SOLVER_GRID_S_MIN=0
QUANT_SOLVER_GRID_S_MAX=50000
QUANT_SOLVER_TIME_STEPS=100
QUANT_SOLVER_PRICE_STEPS=400
QUANT_NUMBA_CACHE=true
QUANT_MAX_WORKERS=8
QUANT_OUTPUT_TOPIC=quant.pricing.surface
GREEKS_OUTPUT_TOPIC=quant.greeks.surface

# -----------------------------
# ML SERVICE
# -----------------------------
ML_TRAINING_DATASET_URI=
ML_MODEL_NAME=volatility-lstm
ML_INFERENCE_TOPIC=ml.volatility.inference
ML_FEATURE_TOPIC=ml.features.realtime
ML_RESIDUAL_MODEL_ENABLED=true
ML_DEVICE=cpu
ML_BATCH_SIZE=64

# -----------------------------
# API GATEWAY
# -----------------------------
API_HOST=0.0.0.0
API_PORT=8000
API_WS_PATH=/ws
API_ALLOWED_ORIGINS=http://localhost:3000

# -----------------------------
# FRONTEND
# -----------------------------
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_PLOTLY_RENDER_TARGET_FPS=60

# -----------------------------
# INFRA / OBSERVABILITY
# -----------------------------
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
JAEGER_ENDPOINT=http://jaeger:4318
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

---

## 4. Strict Phased Delivery Plan

> **Execution rule:** Finish Phase 1 completely before starting Phase 2. Finish Phase 2 completely before starting Phase 3. Finish Phase 3 completely before starting Phase 4.

---

## Phase 1 — Environment & Project Setup

### Goal

Create the monorepo, baseline service shells, local containers, shared contracts directory, observability skeleton, and CI scaffolding. No real trading logic yet.

### Implementation Scope

1. Create the monorepo structure shown above.
2. Add service-level Dockerfiles.
3. Add `docker-compose.yml` with all local dependencies.
4. Add `.env.example` grouped by service.
5. Add FastAPI bootstrap stubs for backend services.
6. Add frontend shell with React + TypeScript + Tailwind + Plotly wiring only.
7. Add shared libraries for schemas and observability.
8. Add GitHub Actions skeleton for lint/test/build.
9. Add Kubernetes base manifests without advanced autoscaling yet.

### Developer Workflow

1. **Architecture-first prompt pass**
   - Use AI to scaffold folders, interfaces, compose files, and placeholder service startup code.
   - Keep prompts narrow: one service, one Dockerfile, one config unit at a time.
2. **Contract-first review**
   - Human reviews service boundaries before any implementation logic is added.
3. **Bootstrap pass**
   - Generate health endpoints and startup probes for every service.
4. **Local integration pass**
   - Bring the stack up with `docker-compose` and verify containers, networking, and environment injection.
5. **CI pass**
   - Add minimal lint/test workflows to guarantee every service can build independently.

### AI Prompt Templates for Engineers

**Prompt: monorepo scaffolding**

```text
Create a production-structured microservices monorepo for a quantitative derivatives terminal.
Constraints:
- Python FastAPI backend services
- React/TypeScript frontend
- Redis, TimescaleDB, PostgreSQL, MLflow
- Docker + docker-compose + Kubernetes-ready layout
- Strict service isolation
Output only the folder tree and minimal bootstrap files for Phase 1.
Do not implement business logic.
```

**Prompt: service bootstrap**

```text
Generate a minimal FastAPI bootstrap for [SERVICE_NAME].
Requirements:
- /health endpoint
- environment-driven settings
- structured logging hooks
- readiness for Redis/Postgres/Timescale clients
- no business logic yet
Include unit tests for the health endpoint.
```

**Prompt: Docker setup**

```text
Create a Dockerfile and docker-compose service definition for [SERVICE_NAME].
Requirements:
- dev-friendly startup
- deterministic dependency installation
- healthcheck support
- environment variable injection from .env
Do not add unrelated services.
```

### Testing Strategy

**Unit tests**
- Service health endpoint returns `200` with expected payload.
- Config loader validates required environment variables.
- Shared schema package imports cleanly.

**Integration tests**
- `docker-compose up` brings up all core containers.
- API gateway can reach Redis/Postgres/TimescaleDB.
- Frontend can connect to API gateway over expected base URL.

**Operational checks**
- Container health checks succeed.
- Logs are structured JSON.
- Trace IDs propagate through request middleware stubs.

### Exit Criteria

Phase 1 is complete only when:

- Every service builds independently in Docker.
- `docker-compose` starts the full local stack without manual fixes.
- All services expose `/health` and pass smoke tests.
- `.env.example` is complete and grouped by service.
- Service boundaries are documented and approved.
- CI validates build + lint + unit tests for all current services.

---

## Phase 2 — Data Ingestion & Preprocessing

### Goal

Implement the market data ingestion path as the first real runtime workflow: connect to NSE WebSockets, normalize ticks, validate events, publish to the event backbone, and expose basic operational APIs.

### Implementation Scope

1. Build **market-data-service** with **Python AsyncIO**.
2. Add NSE websocket adapter abstraction.
3. Normalize raw exchange frames to a deterministic internal tick schema.
4. Validate and enrich events before publishing.
5. Publish to **Redis Streams** initially; keep Kafka-compatible topic definitions for future scale-out.
6. Persist tick data to **TimescaleDB** asynchronously.
7. Expose API endpoints for health, stream control, and preprocessing triggers.

### Event Schema: Tick-Level Normalized Data

Use a versioned schema contract shared under `libs/event-schemas`.

```json
{
  "schema_version": "1.0.0",
  "event_type": "market.tick.normalized",
  "event_id": "uuid",
  "trace_id": "uuid",
  "source": "nse.websocket",
  "published_at": "2026-03-23T12:00:00.000Z",
  "instrument": {
    "symbol": "NIFTY",
    "expiry": "2026-03-26",
    "strike": 22500,
    "option_type": "CE",
    "instrument_token": "token"
  },
  "market": {
    "spot_price": 22482.15,
    "last_traded_price": 152.35,
    "bid_price": 152.25,
    "ask_price": 152.45,
    "bid_qty": 500,
    "ask_qty": 450,
    "volume": 120000,
    "open_interest": 240000,
    "implied_volatility": null
  },
  "timing": {
    "exchange_timestamp": "2026-03-23T12:00:00.001Z",
    "ingestion_timestamp": "2026-03-23T12:00:00.007Z",
    "normalization_latency_ms": 2
  },
  "quality": {
    "is_valid": true,
    "dropped_fields": [],
    "anomaly_flags": []
  }
}
```

### Messaging System Design

**Redis Streams initial channels**
- `market.ticks.normalized`
- `market.ticks.validated`
- `market.preprocessing.requests`
- `market.preprocessing.completed`
- `market.control`
- `market.ticks.dlq`

**Kafka-compatible topic mirror names**
- `market.ticks.normalized.v1`
- `market.ticks.validated.v1`
- `market.preprocessing.requests.v1`
- `market.control.v1`

**Backbone rule:** service code depends on a messaging abstraction, not directly on Redis-specific client semantics.

### API Endpoints

**Health checks**
- `GET /health`
- `GET /health/ready`
- `GET /health/live`

**Stream control**
- `POST /streams/start`
- `POST /streams/stop`
- `GET /streams/status`

**Preprocessing triggers**
- `POST /preprocessing/run`
- `POST /preprocessing/replay`
- `GET /preprocessing/status/{job_id}`

### Validation + Normalization Pipeline

1. Receive raw websocket frame.
2. Validate source payload shape.
3. Map exchange-specific fields into internal schema.
4. Normalize timestamps, symbol metadata, numeric precision, and option identifiers.
5. Reject invalid or stale payloads.
6. Annotate quality flags and latency metadata.
7. Publish validated event.
8. Write asynchronously to TimescaleDB.
9. Route malformed payloads to DLQ.

### Developer Workflow

1. **Adapter-first**
   - AI generates the websocket adapter interface and mock adapter before touching real NSE specifics.
2. **Schema-first**
   - Engineers define the normalized event schema and validation rules before implementing publishers.
3. **Pipeline pass**
   - AI scaffolds normalization functions and validation middleware in small units.
4. **Backbone pass**
   - Add Redis Streams producer/consumer wrappers and replay support.
5. **Persistence pass**
   - Add asynchronous TimescaleDB writer.
6. **Operational API pass**
   - Add FastAPI control endpoints for stream lifecycle and preprocessing jobs.
7. **Latency pass**
   - Measure raw-frame-to-publish latency and optimize AsyncIO hot path.

### AI Prompt Templates for Engineers

**Prompt: event schema design**

```text
Design a versioned normalized tick event schema for NSE derivatives market data.
Requirements:
- suitable for Redis Streams and Kafka
- include instrument, market, timing, quality, trace metadata
- deterministic numeric field naming
- compatible with TimescaleDB persistence and downstream quant/ML consumers
Output JSON schema and a Python Pydantic model.
```

**Prompt: ingestion pipeline**

```text
Implement an AsyncIO market data ingestion pipeline for FastAPI.
Requirements:
- websocket adapter abstraction
- validation and normalization stages
- Redis Streams publisher abstraction
- DLQ handling
- no pricing logic
Also generate unit tests for normalization and integration tests with mocked Redis.
```

**Prompt: operational API**

```text
Create FastAPI endpoints for market-data-service:
- GET /health, /health/ready, /health/live
- POST /streams/start
- POST /streams/stop
- GET /streams/status
- POST /preprocessing/run
- POST /preprocessing/replay
- GET /preprocessing/status/{job_id}
Use service classes and dependency injection.
```

### Testing Strategy

**Unit tests**
- Raw-to-normalized mapping correctness.
- Timestamp normalization and timezone handling.
- Schema validation rejects malformed ticks.
- Quality flags and DLQ routing behavior.

**Integration tests**
- Mock websocket feed to Redis Streams publish flow.
- Redis Streams consumer group replay behavior.
- TimescaleDB asynchronous write path.
- API endpoints correctly start/stop stream workers.

**Performance tests**
- Burst ingest at 100+ strikes/sec.
- Validate publish latency remains within target budget for the ingestion stage.

### Exit Criteria

Phase 2 is complete only when:

- Market data service ingests and publishes normalized events reliably.
- Event schema is versioned, documented, and shared.
- All required endpoints are implemented and tested.
- Invalid payloads are routed to DLQ with trace metadata.
- TimescaleDB persistence works asynchronously.
- Measured ingestion path supports target throughput without blocking the event loop.

---

## Phase 3 — Quant Engine (PDE Solver)

### Goal

Implement deterministic option pricing and Greeks as an event-driven quant service consuming normalized market data and producing pricing surfaces/Greeks outputs.

### Implementation Scope

1. Build **Black-Scholes PDE solver**.
2. Build **Heston PDE solver**.
3. Use **Crank-Nicolson finite difference** method.
4. Compute Greeks: **Delta, Gamma, Theta, Vega, Vanna, Volga**.
5. Consume normalized tick events and metadata events.
6. Publish pricing and Greeks events.
7. Parallelize with **Numba** and vectorization.

### Service Interfaces

**Input events**
- `market.ticks.validated`
- `reference.instrument.metadata`
- `quant.pricing.requests`

**Output events**
- `quant.pricing.surface`
- `quant.greeks.surface`
- `quant.solver.diagnostics`
- `quant.pricing.dlq`

### Quant Output Contract

Each pricing output should include:
- instrument identifiers
- model used (`black_scholes_pde` or `heston_pde`)
- grid parameters
- fair value
- Greeks bundle
- solver convergence metadata
- latency metrics
- deterministic checksum/version for reproducibility

### Numerical Design Rules

- Crank-Nicolson implementation must be deterministic for identical inputs.
- Boundary and terminal conditions are explicit and documented.
- Solver kernels are isolated in `libs/quant-core` for unit testing.
- Quant service wraps solver kernels, but does not embed UI or ML assumptions.
- Use Numba JIT and vectorized linear algebra where it improves latency predictably.
- QuantLib may be used for benchmark/reference validation, not as an excuse to skip numerical transparency.

### Developer Workflow

1. **Reference-first**
   - Engineers define mathematical assumptions, grid boundaries, and expected outputs before prompting AI to generate solver code.
2. **Kernel-first**
   - AI generates finite-difference kernels in isolated library modules, not inside API handlers.
3. **Validation-first**
   - Compare Black-Scholes PDE outputs to analytical Black-Scholes prices.
4. **Greeks pass**
   - Add Delta/Gamma/Theta first, then Vega/Vanna/Volga.
5. **Heston pass**
   - Implement Heston solver only after the Black-Scholes solver is stable and benchmarked.
6. **Event integration pass**
   - Wire the quant engine to consume validated ticks and emit pricing events.
7. **Performance pass**
   - Profile vectorization, Numba caching, worker parallelism, and batch sizing.

### AI Prompt Templates for Engineers

**Prompt: PDE solver implementation**

```text
Implement a Crank-Nicolson finite-difference solver for European option pricing under the Black-Scholes PDE.
Requirements:
- deterministic outputs
- isolated numerical kernel in Python using NumPy/SciPy/Numba
- clean interfaces for grid config and boundary conditions
- unit tests comparing against analytical Black-Scholes prices
Do not add API code.
```

**Prompt: Greeks computation**

```text
Add Greeks computation to the PDE pricing module.
Required Greeks: Delta, Gamma, Theta, Vega, Vanna, Volga.
Requirements:
- numerically stable finite-difference approximations or direct derivations where appropriate
- deterministic test fixtures
- publish-ready output schema
```

**Prompt: event-driven quant service**

```text
Create a FastAPI-compatible quant-engine service that consumes normalized tick events from Redis Streams and publishes pricing/Greeks events.
Requirements:
- loose coupling to the messaging backend via interfaces
- no direct frontend dependencies
- include solver diagnostics and latency metadata
- include integration tests with mocked event streams
```

### Testing Strategy

**Unit tests**
- Black-Scholes PDE vs analytical Black-Scholes tolerance checks.
- Grid convergence behavior across increasing resolution.
- Greeks correctness against finite-difference or reference benchmarks.
- Deterministic repeatability for fixed input seeds.

**Integration tests**
- Consume validated tick event → produce pricing event.
- Metadata lookup integration with PostgreSQL.
- Failure handling routes numerical exceptions to quant DLQ.

**Performance tests**
- Parallel pricing across 100+ strikes/sec.
- End-to-end quant computation latency stays inside the real-time budget allocation.

### Exit Criteria

Phase 3 is complete only when:

- Black-Scholes and Heston PDE solvers are implemented.
- Crank-Nicolson is the actual production numerical scheme.
- All required Greeks are published in the output contract.
- Solver outputs are deterministic and benchmarked.
- Quant engine consumes and emits events without tight coupling.
- Parallel execution meets throughput targets on representative workloads.

---

## Phase 4 — ML Layer

### Goal

Add a production ML layer for offline volatility model training and async real-time inference without coupling model execution to the quant or UI runtime.

### Implementation Scope

1. Build offline training pipeline.
2. Build async real-time inference pipeline.
3. Use features: volatility, order book imbalance, open interest, spot price.
4. Primary model: **LSTM**.
5. Optional residual correction: **XGBoost** over model residuals.
6. Add **MLflow** tracking and model registry.
7. Publish forecasts back to the event backbone.

### Training Pipeline Design

**Offline batch path**
1. Load historical ticks from TimescaleDB and metadata from PostgreSQL.
2. Build training dataset windows.
3. Engineer features:
   - realized/implied volatility
   - order book imbalance
   - open interest
   - spot price and derived returns
4. Train LSTM in PyTorch.
5. Optionally fit XGBoost residual model on LSTM residuals.
6. Log parameters, metrics, artifacts, and model versions to MLflow.
7. Register approved model for inference deployment.

### Real-Time Inference Pipeline Design

**Async live path**
1. Consume normalized tick events or derived feature events.
2. Build rolling feature windows asynchronously.
3. Run LSTM inference.
4. If enabled, apply residual correction.
5. Publish forecast event.
6. Cache recent forecasts in Redis for low-latency API reads.

### ML Service Interfaces

**Input events**
- `market.ticks.validated`
- `ml.features.realtime`
- `ml.training.requests`

**Output events**
- `ml.volatility.forecast`
- `ml.model.metrics`
- `ml.training.completed`
- `ml.inference.dlq`

### Model Tracking and Evaluation

Track in MLflow:
- experiment name
- model version
- feature set version
- training window range
- hyperparameters
- MSE
- R²
- directional accuracy
- latency metrics for inference

### Developer Workflow

1. **Dataset-first**
   - AI helps define dataset builders and feature contracts before model code.
2. **Training-first**
   - Implement offline training pipeline before real-time inference.
3. **Registry-first**
   - Only deploy models through MLflow-tracked artifacts.
4. **Inference pass**
   - Build asynchronous inference worker with bounded latency.
5. **Residual pass**
   - Add optional XGBoost residual model after the baseline LSTM is stable.
6. **Evaluation pass**
   - Compare current model against previous registered version using MSE, R², and directional accuracy.
7. **Integration pass**
   - Publish forecast events consumable by API or quant services, without direct service coupling.

### AI Prompt Templates for Engineers

**Prompt: ML training pipeline**

```text
Create an offline ML training pipeline for volatility prediction.
Requirements:
- PyTorch LSTM primary model
- optional XGBoost residual correction
- data loaded from TimescaleDB/PostgreSQL-derived features
- MLflow experiment tracking and model registration
- evaluation metrics: MSE, R², directional accuracy
Generate pipeline modules and unit-testable interfaces, not notebook-only code.
```

**Prompt: real-time inference**

```text
Implement an async real-time inference service for volatility forecasting.
Requirements:
- consume feature events from Redis Streams
- maintain rolling windows
- run low-latency LSTM inference
- optionally apply XGBoost residual correction
- publish forecast events and cache latest output in Redis
Include latency instrumentation and integration tests.
```

**Prompt: feature engineering contract**

```text
Design a reusable feature contract for volatility forecasting in an event-driven derivatives platform.
Mandatory inputs:
- volatility
- order book imbalance
- open interest
- spot price
Output a versioned schema, validation rules, and training/inference compatibility notes.
```

### Testing Strategy

**Unit tests**
- Feature engineering correctness.
- Dataset window generation.
- LSTM forward pass output shape.
- Residual correction pipeline behavior.
- MLflow logging wrappers.

**Integration tests**
- Offline training job logs artifacts to MLflow.
- Registered model can be loaded by inference service.
- Real-time feature event → forecast event flow works end-to-end.

**Performance tests**
- Inference latency under burst load remains compatible with overall <50 ms tick-to-dashboard target.
- Redis cache lookups meet dashboard read latency needs.

### Exit Criteria

Phase 4 is complete only when:

- Offline training is reproducible and tracked in MLflow.
- Real-time async inference publishes forecast events reliably.
- LSTM baseline is working with required features.
- Optional XGBoost residual correction is modular and switchable.
- Evaluation metrics include MSE, R², and directional accuracy.
- The ML layer remains event-driven and independently deployable.

---

## 5. Reusable Prompt Library

The following prompt library should be stored under `docs/architecture/prompt-library.md` or an internal prompt registry.

### A. File Scaffolding Prompt

```text
You are generating Phase-[X] scaffolding for a quantitative derivatives trading terminal.
Constraints:
- microservices monorepo
- event-driven architecture
- FastAPI backend, React frontend
- Redis, TimescaleDB, PostgreSQL, MLflow
- Docker/Kubernetes ready
Output:
1. exact files to create
2. minimal contents for each file
3. tests for each created module
Do not implement unrelated phases.
```

### B. FastAPI API Creation Prompt

```text
Generate a FastAPI module for [SERVICE_NAME].
Requirements:
- dependency-injected routers
- pydantic request/response models
- health endpoints
- structured logging
- async-first I/O
- unit tests and integration test stubs
Keep the module isolated to [PHASE_NAME] scope.
```

### C. Event Schema Design Prompt

```text
Design a versioned event schema for [EVENT_NAME].
Constraints:
- compatible with Redis Streams and Kafka
- include traceability fields
- include schema versioning
- support deterministic downstream processing
Return:
- JSON schema
- Pydantic model
- sample event
- validation rules
```

### D. PDE Solver Prompt

```text
Implement a production-oriented PDE solver module for [MODEL_NAME].
Requirements:
- Crank-Nicolson finite difference
- deterministic outputs
- NumPy/SciPy/Numba only
- no API/framework code
- tests against analytical/reference benchmarks
Also expose a clean interface for batch pricing and Greeks.
```

### E. ML Training / Inference Prompt

```text
Generate modular ML code for [TRAINING or INFERENCE] in an event-driven trading platform.
Requirements:
- PyTorch for LSTM
- optional XGBoost residual layer
- MLflow tracking
- async-compatible inference path
- metrics: MSE, R², directional accuracy
Output production modules, not notebooks.
```

---

## 6. Collaboration Workflow

### GitHub Branching Strategy

Use a lightweight trunk-based model with explicit phase gates.

- `main`: protected production-ready branch.
- `develop` (optional if the team prefers): shared integration branch for pre-release validation.
- `phase/1-setup-*`
- `phase/2-data-*`
- `phase/3-quant-*`
- `phase/4-ml-*`
- `hotfix/*`

**Rules**
- One pull request should map to one bounded implementation objective.
- Never mix Phase 2 data work with Phase 3 quant logic in the same branch.
- Schema changes require reviewers from every downstream consuming service.

### Code Review Guidelines

Every PR should be reviewed against these lenses:

1. **Phase discipline** — does the PR stay within the current phase scope?
2. **Service isolation** — does it preserve loose coupling?
3. **Contract quality** — are event schemas explicit, versioned, and tested?
4. **Latency awareness** — does it avoid blocking I/O or unnecessary serialization?
5. **Determinism** — for quant code, are outputs reproducible?
6. **Observability** — are logs/metrics/traces added for the new path?
7. **Rollback safety** — can the change be disabled or reverted cleanly?

### Service Ownership Boundaries

- **Data Platform Team** owns market-data-service, ingestion schemas, TimescaleDB write path.
- **Quant Team** owns quant-engine, quant-core, PDE validation, Greeks correctness.
- **ML Team** owns ml-service, ml-core, MLflow, feature contracts, model evaluation.
- **Platform Team** owns Docker/Kubernetes, CI/CD, observability stack, secrets flow.
- **Frontend Team** owns frontend terminal rendering, chart performance, operator workflows.
- **Architecture Lead** approves cross-service schema changes and phase exits.

---

## 7. Feedback Loops and Iteration Cycles

### Observability Feedback Loops

Every service must emit:

- **Structured logs** with trace IDs, event IDs, instrument IDs.
- **Metrics**:
  - ingestion latency
  - quant compute latency
  - inference latency
  - message backlog depth
  - DLQ count
  - WebSocket connection count
  - dashboard frame rate
- **Tracing**:
  - end-to-end flow from tick ingestion to dashboard delivery
  - async spans across Redis publish/consume boundaries

### Model Evaluation Feedback Loops

For every ML training or model refresh cycle, track:

- **MSE**
- **R²**
- **Directional accuracy**
- inference latency percentile distribution
- drift indicators on feature distributions
- comparison against previous production model version

### Developer Iteration Cycle

For each task, engineers follow this loop:

1. Define a narrow objective tied to the current phase.
2. Use a reusable prompt to scaffold the minimum viable implementation.
3. Run unit tests locally.
4. Run integration tests against compose services.
5. Review logs/metrics/traces.
6. Refine prompt or hand-edit implementation.
7. Open PR with phase-specific checklist.
8. Merge only after exit criteria remain satisfied.

### Graceful Degradation Rules

- If ML inference is unavailable, the dashboard continues using quant outputs and last-known forecasts.
- If quant engine is degraded, the UI surfaces stale-state warnings rather than blocking the app.
- If TimescaleDB is temporarily unavailable, ingestion can continue with bounded buffering and DLQ policy.
- If Redis Streams lag increases, the API gateway exposes backpressure status to operators.

---

## 8. Phase Gate Checklist

Before moving forward, the architecture lead or service owner should verify:

### Gate 1 → Phase 2
- Project boots locally.
- Services are containerized.
- CI is green.
- Service boundaries are frozen for the ingestion phase.

### Gate 2 → Phase 3
- Tick schema is stable and versioned.
- Market data service passes throughput tests.
- Replay and DLQ paths work.
- TimescaleDB persistence is validated.

### Gate 3 → Phase 4
- Black-Scholes and Heston PDE outputs are deterministic.
- Greeks coverage is complete.
- Quant event contracts are stable.
- Throughput and latency targets are met on representative loads.

### Gate 4 → Downstream UI/portfolio/risk phases
- MLflow-backed training/inference is stable.
- Forecast events are versioned and observable.
- Model evaluation metrics are reviewable.
- Failure paths and graceful degradation are tested.

---

## 9. Self-Check Against the Requirements

This workflow plan intentionally enforces:

- a strict **implementation-first phased sequence**,
- a precise **microservices monorepo setup**,
- **Docker + compose + Kubernetes** readiness,
- service-grouped **`.env`** design,
- **AsyncIO** market data ingestion,
- normalized **event schemas** over **Redis Streams/Kafka-style pub-sub**,
- **Crank-Nicolson** PDE implementation for **Black-Scholes and Heston**,
- required Greeks: **Delta, Gamma, Theta, Vega, Vanna, Volga**,
- **PyTorch LSTM** with optional **XGBoost** residual correction,
- **MLflow** tracking,
- per-phase **developer workflows, prompt templates, tests, and exit criteria**,
- collaboration guardrails, observability, model evaluation, and iteration loops,
- strict compliance with the required stack and performance constraints.

This is the required workflow system. It is deliberately phased so the team does **not** attempt to build the entire trading terminal at once.

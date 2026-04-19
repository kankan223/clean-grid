# ⚙️ TECH STACK ARCHITECTURE — CleanGrid
### AI-Powered Smart Waste Management & Mapping System

---

## 1. 🧠 Stack Strategy Overview

**Type of Application:** Web-first, AI-augmented geospatial operations platform with real-time data, image inference, route optimization, and gamification.

**Architecture Style:** **Modular Monolith with one isolated AI microservice**

This is the most strategic choice for CleanGrid specifically. Here's the reasoning:

The PRD describes 6 distinct domains — reporting, AI inference, mapping, routing, verification, and gamification — but nearly all of them share the same database and data flow. Splitting these into full microservices would add network overhead, service discovery complexity, and inter-service auth that a hackathon team cannot manage. A modular monolith gives you clean internal boundaries (each domain gets its own router/module in FastAPI) while deploying as one unit. The **only true microservice** is the AI inference engine — it has a different runtime (Python + GPU-optional), different scaling profile, different latency budget, and needs to be independently restartable if the model crashes. This isolation is justified. Everything else stays in one deployable backend.

**Why this fits the PRD precisely:**
- PRD Section 13 already diagrams this exact split: FastAPI core + separate AI service
- PRD explicitly warns against overengineering (Section 25)
- The "closed loop" demo requirement needs one coherent data layer, not distributed eventual consistency
- The fallback requirements (AI down → save anyway, route API down → nearest-neighbor) are far easier to implement in a monolith where you control all the state

---

## 2. 🎯 Core Stack Selection

### Frontend

| Decision | Choice |
|---|---|
| **Framework** | Next.js 14 (App Router) |
| **Styling** | Tailwind CSS + shadcn/ui |
| **State Management** | Zustand + TanStack Query (React Query v5) |
| **Mapping** | Leaflet.js + react-leaflet + plugins |
| **Routing** | Next.js App Router (file-based) |

**Why this exact combination:**

**Next.js 14 with App Router** is chosen over plain React or Vite for three non-negotiable reasons: (1) Server Components let you pre-render the leaderboard and route views without client-side fetch waterfalls, (2) API Routes give you a BFF (Backend For Frontend) layer to handle auth token management without exposing your FastAPI directly to browsers, and (3) Vercel deployment is literally one `git push` — critical under hackathon time pressure.

**Tailwind CSS + shadcn/ui** is the highest-leverage styling choice available. shadcn/ui gives you production-quality components (Table, Drawer, Badge, Sheet, Toast, Dialog) that match exactly what the PRD describes — the admin dashboard's sortable table, right-side detail drawer, status pills, and severity badges. These are not generic UI kit components; shadcn gives you the source code directly, so you can customize without fighting a component library's opinions. Combined with Tailwind, you can build the entire UI without writing a single CSS file.

**Zustand** for global client state (auth session, active filters, selected incidents, map state) over Redux because it has 1/10th the boilerplate and zero configuration. For a hackathon, Redux's ceremony kills velocity. Zustand stores are plain objects with actions — the entire auth store is 20 lines.

**TanStack Query (React Query v5)** for all server state — incident lists, leaderboard, route data. This gives you automatic caching, background refetching (which handles the 30-second polling requirement from FR-21), optimistic updates for status changes, and built-in loading/error states. You do not need to write a single `useEffect` for data fetching. This directly eliminates one of the most common hackathon bugs: stale data and race conditions.

**Leaflet.js + react-leaflet** over Mapbox GL JS for the map: OpenStreetMap tiles are free with no API key, Leaflet has first-class plugins for exactly what the PRD requires (`leaflet.markercluster` for FR-15, `leaflet.heat` for FR-14), and react-leaflet has excellent TypeScript support. Mapbox GL JS would require a paid token beyond free tier limits at demo scale and adds WebGL complexity. Leaflet is battle-tested, lighter, and sufficient for this use case.

**Specific Leaflet plugins required:**
- `leaflet.markercluster` — incident clustering (FR-15)
- `leaflet.heat` — heatmap density layer (FR-14)
- `leaflet-routing-machine` — route polyline rendering (FR-26)
- `leaflet-gesture-handling` — prevents map scroll hijacking on mobile

---

### Backend

| Decision | Choice |
|---|---|
| **Language** | Python 3.11 |
| **Framework** | FastAPI |
| **API Style** | REST with OpenAPI auto-docs |
| **Internal structure** | Domain-modular (routers per domain) |
| **Task Queue** | FastAPI Background Tasks (MVP) → Celery (V2) |
| **Real-time** | Server-Sent Events (SSE) for status updates |

**Why Python + FastAPI over Node.js/Express or Django:**

This is the most consequential stack decision and it must be defended precisely. Python is the only language where your AI inference service and your backend API share the same ecosystem natively. Your YOLOv8 service is Python. Your hotspot clustering (scikit-learn) is Python. Your geospatial logic (shapely, geopandas) is Python. If you choose Node.js for the backend, you immediately create a language boundary that costs you: separate dependency management, no code sharing, and more Docker complexity. FastAPI specifically — not Django, not Flask — because:

1. **FastAPI is async-native**, meaning image upload handlers, AI service calls, and ORS API calls can all happen concurrently without blocking. This directly satisfies NFR-02 (AI inference < 10s) without thread pool hacks.
2. **FastAPI auto-generates OpenAPI 3.0 docs** (NFR-26) from your type annotations. Your API documentation is zero additional work.
3. **FastAPI's dependency injection** system makes per-route auth, database session management, and role checking (`admin` vs `crew` vs `citizen`) clean and testable — exactly what FR-17, FR-20, FR-32 require.
4. **Pydantic v2** (built into FastAPI) gives you input validation, serialization, and schema generation. FR-01 through FR-11's validation requirements are all handled declaratively.

**Domain module structure in FastAPI:**
```
app/
  routers/
    auth.py       # POST /auth/login, /register
    reports.py    # POST/GET/PATCH /api/reports
    routes.py     # POST/GET /api/routes
    admin.py      # Admin-only operations
    leaderboard.py
    hotspots.py
  services/
    ai_client.py      # HTTP client to AI microservice
    ors_client.py     # OpenRouteService integration
    scoring.py        # Priority score formula
    points.py         # Gamification logic
  models/             # SQLAlchemy ORM models
  schemas/            # Pydantic request/response schemas
  core/
    auth.py           # JWT logic
    config.py         # Settings from .env
    database.py       # DB session factory
```

**Server-Sent Events over WebSockets for real-time:** The PRD requires status updates to propagate without page refresh (FR-21). Full WebSockets require a persistent connection manager and are overkill when you only need one-directional server → client updates. SSE is HTTP-native, works through proxies and load balancers without configuration, and is natively supported by FastAPI's `EventSourceResponse`. The admin dashboard subscribes to a `/api/events/incidents` SSE stream and receives status change events. This is 40 lines of code vs. 200+ for WebSocket management.

---

### Database

| Decision | Choice |
|---|---|
| **Primary DB** | PostgreSQL 15 with PostGIS 3.3 |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Migrations** | Alembic |
| **Connection pooling** | asyncpg (async PostgreSQL driver) |
| **Caching layer** | Redis 7 (for leaderboard, session, rate limiting) |

**Why PostgreSQL + PostGIS is non-negotiable for this product:**

The PRD's geospatial requirements — spatial indexing (FR-12 through FR-16), hotspot zone computation (FR-37 through FR-40), route waypoint storage — cannot be done efficiently in MongoDB, SQLite, or any database without a mature geospatial extension. PostGIS gives you:

- `GEOGRAPHY(POINT, 4326)` columns with GIST indexes for sub-millisecond spatial queries across 500+ incidents (NFR-06)
- `ST_DWithin()` for the 20-meter duplicate detection (Flow 2 edge cases)
- `ST_ClusterDBSCAN()` or grid-cell aggregation for hotspot computation (FR-37)
- `ST_AsGeoJSON()` for direct GeoJSON output to the frontend map
- `ST_Distance()` for the Haversine fallback in nearest-neighbor routing (FR-25)

The alternative — computing geospatial logic in Python with shapely after pulling all records — does not scale and cannot use database indexes. PostGIS is the only correct choice.

**SQLAlchemy 2.0 async** is chosen over synchronous SQLAlchemy or raw asyncpg queries because it gives you type-safe ORM models while supporting `async/await` natively with `asyncpg`. This matches FastAPI's async architecture. Alembic handles schema migrations cleanly and integrates with SQLAlchemy models — every schema change in the data model (Section 14) maps directly to an Alembic migration file.

**Redis** is added specifically for three use cases the PRD requires:
1. **Leaderboard caching** (FR-35, FR-36): The top-20 leaderboard query is expensive at scale. Cache it in Redis with a 60-second TTL, invalidated on every point award.
2. **Rate limiting** (NFR abuse prevention, Section 17): 10 reports/IP/hour is implemented as a Redis sliding window counter — the only reliable way to rate limit across multiple server instances.
3. **Session/refresh token blacklisting** (Section 17 auth): JWT refresh token rotation requires a store for revoked tokens. Redis with TTL matching the token expiry is the standard approach.

---

### Authentication

| Decision | Choice |
|---|---|
| **Method** | JWT (access + refresh token rotation) |
| **Library** | `python-jose[cryptography]` + `passlib[bcrypt]` |
| **Token storage** | HttpOnly cookies (access: 15min, refresh: 7 days) |
| **Role enforcement** | FastAPI dependency injection per router |

**Why HttpOnly cookies over localStorage for JWTs:**

The PRD requires JWT auth (NFR-13) and CSRF protection (Section 17). Storing JWTs in localStorage exposes them to XSS attacks — any injected script can steal them. HttpOnly cookies are inaccessible to JavaScript, making XSS token theft impossible. Combined with `SameSite=Strict` cookie policy (which the PRD explicitly requires in Section 17), this eliminates CSRF without needing a separate CSRF token mechanism.

FastAPI's dependency injection makes role enforcement clean:
```python
# Each protected route gets the right guard
@router.get("/admin/incidents", dependencies=[Depends(require_admin)])
@router.patch("/incidents/{id}/status", dependencies=[Depends(require_crew_or_admin)])
```

This is not bolted on — it's checked at the framework level before your handler runs.

---

## 3. 🤖 AI / ML Stack

| Component | Choice |
|---|---|
| **Detection model** | YOLOv8n (Ultralytics) — nano variant for speed |
| **Inference framework** | Ultralytics Python SDK |
| **Service framework** | FastAPI (separate process/container) |
| **Model weights** | COCO pre-trained (MVP) → TACO fine-tuned (V2) |
| **Image preprocessing** | Pillow + OpenCV-python |
| **Hotspot clustering** | PostGIS grid aggregation (MVP) → scikit-learn DBSCAN (V2) |
| **Hardware** | CPU inference (hackathon) → GPU via CUDA (production) |

**Why YOLOv8n specifically over YOLOv8s/m/l:**

The PRD requires AI inference in < 10 seconds (FR-11, NFR-02). YOLOv8n (nano) runs in 1-3 seconds on CPU for a 640×640 image, while YOLOv8s takes 4-8 seconds and YOLOv8m takes 10-15 seconds on the same hardware. For a hackathon demo running on a laptop or a $7/month cloud instance without a GPU, nano is the correct choice. The accuracy difference between nano and small on COCO classes (bottle, cup, bag — the proxy trash classes) is ~3% mAP, which is imperceptible in a demo and acceptable for MVP (PRD Section 15 assumption #1).

**AI service input/output contract** (exactly as specified in PRD Section 15):
```python
# POST /infer
class InferenceRequest(BaseModel):
    image_url: str

class Detection(BaseModel):
    label: str
    confidence: float
    box: list[float]  # [x1, y1, x2, y2]

class InferenceResponse(BaseModel):
    waste_detected: bool
    confidence: float | None
    severity: Literal["None", "Low", "Medium", "High"]
    detections: list[Detection]
```

**Severity computation logic** (FR-08, implemented in the AI service):
```python
RELEVANT_CLASSES = {"bottle", "cup", "bag", "banana", "can", "backpack", "suitcase"}
THRESHOLD = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.45"))

def compute_severity(detections: list[Detection]) -> tuple[bool, str, float]:
    relevant = [d for d in detections 
                if d.label in RELEVANT_CLASSES and d.confidence >= THRESHOLD]
    if not relevant:
        return False, "None", 0.0
    max_conf = max(d.confidence for d in relevant)
    count = len(relevant)
    if max_conf >= 0.7 or count >= 3:
        return True, "High", max_conf
    elif max_conf >= 0.45 or count == 2:
        return True, "Medium", max_conf
    else:
        return True, "Low", max_conf
```

**Fallback when AI service is down:** The core backend catches `httpx.ConnectError` and `httpx.TimeoutException` from the AI client, saves the report with `severity=null, status="Pending AI Review"`, and sets a flag that triggers a dashboard warning banner (FR-10). This is implemented as a try/except around the AI service HTTP call — not a circuit breaker library, which would be overengineering.

**Cleanup verification reuse:** The same `/infer` endpoint is called with the after-photo. The backend checks `waste_detected == False` OR `severity == "None"` → status becomes `Verified`. Otherwise → `Needs Review` (FR-31). Zero new AI code required.

---

## 4. 🔌 Integrations & APIs

### OpenRouteService (ORS) — Route Optimization
- **Endpoint:** `POST https://api.openrouteservice.org/v2/optimization`
- **Why ORS over GraphHopper or custom TSP:** ORS's optimization endpoint implements the Vehicle Routing Problem (VRP) natively — you send it a list of waypoints and it returns an optimized order, a total distance, an ETA, and a GeoJSON LineString. GraphHopper's free tier has stricter rate limits. Building a custom TSP solver in 48 hours is explicitly warned against in PRD Section 25.
- **Request structure:** Send jobs (incidents) with coordinates and optional priority weights. ORS returns `routes[].steps` with ordered stop IDs.
- **Fallback:** Nearest-neighbor greedy algorithm using PostGIS `ST_Distance()` — O(n²) but correct for n ≤ 50 waypoints. Flagged as `is_approximate = true` in the routes table.
- **Rate limit management:** Cache generated routes in the database. Never regenerate a route unless incidents change. This keeps ORS calls under 40/day on the free tier.

### Browser Geolocation API
- **Why included explicitly:** This is a browser API, not a third-party service, but it deserves explicit mention because it's the primary UX mechanism for report location (FR-03). The implementation must handle the denied-permission case (FR-04 edge case) by immediately showing the map pin picker — not blocking the user.
- **Implementation:** `navigator.geolocation.getCurrentPosition()` with a 5-second timeout. On failure or denial, silently fall back to the map picker.

### OpenStreetMap Tiles (via Leaflet)
- **URL:** `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png`
- **Why:** Zero API key, zero cost, globally cached, sufficient resolution for municipal-scale maps. The PRD explicitly names this as the default (Section 13).
- **Attribution:** Required by OSM license — Leaflet adds this automatically.

### Nominatim (Reverse Geocoding)
- **Why added (not in PRD but implied):** The `address_text` field in the incidents table (Section 14) must be populated somehow. When a user drops a pin, you need a human-readable address. Nominatim is OSM's free reverse geocoding API.
- **Usage:** `GET https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json`
- **Rate limit:** 1 req/second on the free tier — sufficient because address lookup only happens once per report submission.
- **Caching:** Cache reverse geocode results in Redis by coordinate (rounded to 4 decimal places) with a 24-hour TTL to avoid redundant API calls for reports in the same area.

### Cloudflare R2 (Image Storage)
- **Why R2 over S3:** R2 has no egress fees (S3 charges per GB downloaded). For a product where every page load fetches image thumbnails, egress costs matter immediately. R2 is S3-API compatible — your boto3 code works unchanged if you migrate to S3 later. Free tier: 10GB storage, 1M Class A operations/month.
- **Implementation:** `boto3` with the R2 endpoint URL configured. Images stored as `{UUID}.{ext}` (NFR-15). Presigned URLs for direct browser uploads (avoids routing large files through your API server).

### Redis (via Upstash for hackathon)
- **Why Upstash:** Upstash offers serverless Redis with a free tier (10,000 commands/day). For hackathon scale, this eliminates the need to run a Redis container in production. The `redis-py` client connects identically to a local Redis container (for development) or Upstash (for production) — zero code change.

---

## 5. ☁️ Infrastructure & Deployment

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     PRODUCTION                          │
│                                                         │
│  Vercel (Frontend)          Railway (Backend)           │
│  ┌─────────────────┐       ┌──────────────────────┐    │
│  │  Next.js 14     │──────▶│  FastAPI Core        │    │
│  │  (Edge CDN)     │       │  (Docker container)  │    │
│  └─────────────────┘       └──────────┬───────────┘    │
│                                        │                │
│                             ┌──────────▼───────────┐   │
│                             │  FastAPI AI Service  │   │
│                             │  (Docker container)  │   │
│                             └──────────┬───────────┘   │
│                                        │                │
│  ┌─────────────┐    ┌──────────────┐  │                │
│  │ Cloudflare  │    │  PostgreSQL  │◀─┘                │
│  │     R2      │    │  + PostGIS   │                   │
│  │  (Images)   │    │  (Railway)   │                   │
│  └─────────────┘    └──────────────┘                   │
│                                                         │
│  Upstash Redis (serverless, global)                    │
└─────────────────────────────────────────────────────────┘
```

| Layer | Platform | Justification |
|---|---|---|
| **Frontend** | Vercel | Git push deploys, edge CDN, built-in preview environments per PR |
| **Backend API** | Railway | Docker-native, $5/month starter, automatic HTTPS, built-in PostgreSQL |
| **AI Service** | Railway (separate service) | Same platform as backend, independent scaling, independent restart |
| **Database** | Railway PostgreSQL | PostGIS extension available, managed backups, same network as backend (no egress cost) |
| **Image storage** | Cloudflare R2 | Zero egress fees, S3-compatible, global CDN |
| **Cache** | Upstash Redis | Serverless, free tier, no container management |

### Docker Compose (Local Development)
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db, redis]
    env_file: .env
    
  ai-service:
    build: ./ai-service
    ports: ["8001:8001"]
    volumes:
      - ./models:/app/models  # Mount pre-downloaded weights
    env_file: .env.ai
    
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: cleangrid
      POSTGRES_USER: cleangrid
      POSTGRES_PASSWORD: cleangrid
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
    
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

**Why this Docker Compose structure is exactly right:** The AI service is isolated (different port, different volume for model weights, can be killed and restarted without affecting the core API). The `models/` volume mount means YOLOv8 weights are downloaded once and persisted — you don't re-download 6MB on every `docker compose up`.

### CI/CD
- **GitHub Actions** for automated testing on every PR
- **Vercel** auto-deploys frontend on every push to `main`
- **Railway** auto-deploys backend on every push to `main` (configured via Railway's GitHub integration)

---

## 6. 📦 Dev Tools & Ecosystem

### Package Management
- **Frontend:** `pnpm` — 3x faster installs than npm, strict dependency resolution, built-in workspace support if you ever need a monorepo
- **Backend:** `uv` (Astral) — the new standard for Python package management, 10-100x faster than pip, deterministic lockfiles, replaces pip + virtualenv + pip-tools in one tool

### Version Control Strategy
```
main          ← production, protected, requires PR
develop       ← integration branch
feature/*     ← individual features (feature/ai-inference, feature/map-markers)
fix/*         ← bug fixes
```
For a hackathon, simplify to: `main` (protected) + `dev` + feature branches. No PR required during the build phase — merge freely. Lock `main` 2 hours before demo for stability.

### Code Quality
| Tool | Purpose |
|---|---|
| **ESLint + TypeScript strict mode** | Frontend type safety and linting |
| **Prettier** | Formatting (configured once, forgotten forever) |
| **Ruff** | Python linting + formatting (replaces flake8 + black + isort in one tool, 100x faster) |
| **mypy** | Python type checking (FastAPI + Pydantic give you most of this for free) |
| **Husky + lint-staged** | Pre-commit hooks — only lint changed files |

### Testing
| Layer | Tool | Scope |
|---|---|---|
| **Backend unit** | pytest + pytest-asyncio | Service functions, scoring formula, nearest-neighbor algorithm |
| **Backend integration** | pytest + httpx (AsyncClient) | Full API endpoint tests with test DB |
| **Frontend unit** | Vitest + React Testing Library | Component tests |
| **E2E** | Playwright | Full user flows (report submission, admin triage, route generation) |
| **AI evaluation** | Custom pytest fixtures | 20-image test set for precision/recall measurement |

### API Testing
- **Bruno** (not Postman) — Bruno stores collections as files in your git repo. Every team member has the same API tests. No account required, no sync needed. Collections live in `/api-tests/` and are committed alongside code.

### Monitoring & Logging
| Tool | Purpose |
|---|---|
| **Loguru** (Python) | Structured JSON logging in FastAPI and AI service |
| **structlog** | Alternative if you prefer explicit structured logging |
| **Sentry** (free tier) | Error tracking — frontend and backend. One DSN per service. |
| **Railway metrics** | Built-in CPU/memory/request graphs — no setup required |
| **Axiom** (free tier) | Log aggregation if you need to search across services |

---

## 7. ⚡ Performance & Scalability Design

### Caching Strategy

| Data | Cache | TTL | Invalidation |
|---|---|---|---|
| Leaderboard top-20 | Redis | 60 seconds | On every `point_transactions` insert |
| Hotspot zones | Redis | 24 hours | On nightly recomputation job |
| Reverse geocode results | Redis | 24 hours | Never (addresses don't change) |
| Active incidents for map | TanStack Query (client) | 30 seconds | Background refetch |
| Route polylines | DB (permanent) | N/A | Admin explicitly regenerates |

**Why client-side caching via TanStack Query is a first-class strategy:** The map home screen (Screen 1) will be the most-loaded page. TanStack Query caches the incident list in memory, serves it instantly on navigation back to the map, and refetches in the background. This makes the map feel instant on the second visit — critical for demo impressiveness.

### Database Scaling

**Indexes required from day one** (not "add later"):
```sql
-- Spatial index for all geospatial queries
CREATE INDEX idx_incidents_location ON incidents USING GIST (location);

-- Status filtering (most common admin dashboard query)
CREATE INDEX idx_incidents_status ON incidents (status);

-- Priority score sorting (default dashboard sort)
CREATE INDEX idx_incidents_priority ON incidents (priority_score DESC);

-- Composite for the most common admin query: pending + high severity
CREATE INDEX idx_incidents_status_severity ON incidents (status, severity);

-- Reporter lookup for profile page
CREATE INDEX idx_incidents_reporter ON incidents (reporter_id);
```

These indexes are in the Alembic migration from day one. Not added "when we need them." The PRD's 500-marker map requirement (NFR-01) requires the spatial index from the first request.

### Async Processing
- **FastAPI Background Tasks** (built-in, zero dependencies) for: priority score recalculation after incident status change, points award after verification, Nominatim reverse geocoding after report submission (non-blocking — address can populate after the response returns)
- **APScheduler** for the nightly hotspot recomputation job (FR-40). APScheduler runs inside the FastAPI process — no separate Celery worker required for one scheduled job. Add Celery + Redis in V2 if jobs multiply.

### Load Handling
- The backend API is stateless (JWT auth, no server-side session). Any number of instances behind a load balancer work without coordination.
- The AI service is the bottleneck. At scale, run multiple AI service instances behind Railway's load balancer. Each instance is independent (stateless inference).
- PostgreSQL connection pooling via `asyncpg` + SQLAlchemy pool (min: 5, max: 20 connections). Railway's PostgreSQL handles 100 concurrent connections on the starter plan.

---

## 8. 🔒 Security Stack

### Auth Security
- **bcrypt cost factor 12** for password hashing (Section 17). This is the industry standard — cost factor 10 is the minimum, 12 adds ~300ms to login which is imperceptible to users but significant for brute force.
- **Access token: 15 minutes** (not 24 hours as the PRD suggests — 24 hours is too long for a security-sensitive admin system). **Refresh token: 7 days** with rotation on each use.
- **HttpOnly + Secure + SameSite=Strict** cookies for both tokens.
- **Refresh token blacklist in Redis:** When a refresh token is used, it's immediately invalidated and a new one is issued. The old token is added to a Redis set with TTL = remaining token validity. This prevents refresh token replay attacks.

### Data Protection
- **UUID v4 filenames** for all uploaded images (NFR-15). Never use sequential IDs or user-provided filenames.
- **Coordinate precision limiting** in public API responses (3 decimal places ≈ 111m fuzz) (Section 17). Implemented as a Pydantic serializer on the public incident schema.
- **Input sanitization:** Pydantic v2 validates all incoming data. SQLAlchemy ORM parameterizes all queries — no raw SQL string interpolation anywhere.
- **Image deduplication:** SHA-256 hash of uploaded image bytes, stored in the incidents table. On duplicate hash detection, flag for admin review (Section 17).

### API Protection
- **Rate limiting:** Redis sliding window counter per IP. `slowapi` library integrates with FastAPI in 5 lines. Limit: 10 report submissions/IP/hour, 100 general API requests/IP/minute.
- **CORS:** Explicitly whitelist the Vercel frontend domain only. Never use `allow_origins=["*"]` in production.
- **Request size limit:** 10MB maximum request body in FastAPI's Starlette config (matches FR-01).
- **SQL injection:** Impossible with SQLAlchemy ORM. Documented and enforced in code review.
- **XSS:** Next.js escapes all dynamic content by default. No `dangerouslySetInnerHTML` anywhere.

### Secrets Management
- `.env` files locally (never committed — in `.gitignore` from day one)
- Railway environment variables for production backend
- Vercel environment variables for production frontend
- **No secrets in code, Docker images, or git history — ever**
- Use `python-decouple` or Pydantic Settings for typed environment variable loading in Python

---

## 9. 🧪 Development Strategy

### Folder Architecture

```
cleangrid/
├── frontend/                    # Next.js 14
│   ├── app/
│   │   ├── (map)/
│   │   │   └── page.tsx        # Map home screen
│   │   ├── report/
│   │   │   └── page.tsx        # Report submission
│   │   ├── admin/
│   │   │   ├── page.tsx        # Admin dashboard
│   │   │   └── layout.tsx      # Admin auth guard
│   │   ├── route/[id]/
│   │   │   └── page.tsx        # Route view
│   │   ├── leaderboard/
│   │   │   └── page.tsx
│   │   └── profile/
│   │       └── page.tsx
│   ├── components/
│   │   ├── map/
│   │   │   ├── IncidentMap.tsx      # Main Leaflet map
│   │   │   ├── IncidentMarker.tsx   # Severity-coded marker
│   │   │   ├── RoutePolyline.tsx    # Route overlay
│   │   │   └── HeatmapLayer.tsx
│   │   ├── admin/
│   │   │   ├── IncidentTable.tsx
│   │   │   ├── IncidentDrawer.tsx   # Right-side detail panel
│   │   │   └── BulkActionBar.tsx
│   │   ├── report/
│   │   │   ├── ImageUploader.tsx
│   │   │   ├── LocationPicker.tsx
│   │   │   └── AIResultCard.tsx
│   │   └── ui/                 # shadcn/ui components (auto-generated)
│   ├── lib/
│   │   ├── api.ts              # API client (typed fetch wrappers)
│   │   ├── stores/
│   │   │   ├── auth.ts         # Zustand auth store
│   │   │   └── map.ts          # Map filter/state store
│   │   └── utils.ts
│   └── public/
│
├── backend/                     # FastAPI core
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py       # Pydantic Settings
│   │   │   ├── database.py     # async SQLAlchemy engine
│   │   │   ├── auth.py         # JWT logic
│   │   │   └── redis.py        # Redis client
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── incident.py
│   │   │   ├── route.py
│   │   │   └── points.py
│   │   ├── schemas/            # Pydantic request/response
│   │   │   ├── incident.py
│   │   │   ├── route.py
│   │   │   └── user.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── reports.py
│   │   │   ├── routes.py
│   │   │   ├── admin.py
│   │   │   ├── leaderboard.py
│   │   │   └── events.py       # SSE endpoint
│   │   └── services/
│   │       ├── ai_client.py
│   │       ├── ors_client.py
│   │       ├── scoring.py
│   │       ├── points.py
│   │       ├── geocoding.py
│   │       └── hotspots.py
│   ├── migrations/             # Alembic
│   ├── tests/
│   └── seed/
│       └── seed.py             # 50-incident seed script
│
├── ai-service/                  # YOLOv8 inference
│   ├── app/
│   │   ├── main.py
│   │   ├── inference.py        # YOLOv8 wrapper
│   │   ├── severity.py         # Scoring logic
│   │   └── config.py
│   ├── models/                 # YOLOv8 weights (git-ignored)
│   └── tests/
│       └── test_inference.py   # 20-image evaluation set
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── README.md
```

### Local Development Setup (Day 1 Commands)
```bash
# 1. Clone and setup
git clone https://github.com/org/cleangrid
cd cleangrid

# 2. Copy environment files
cp .env.example .env
cp ai-service/.env.example ai-service/.env

# 3. Download YOLOv8 weights (do this once)
cd ai-service && python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# 4. Start all services
docker compose up --build

# 5. Run database migrations
docker compose exec backend alembic upgrade head

# 6. Seed demo data
docker compose exec backend python seed/seed.py

# Frontend available at: http://localhost:3000
# Backend API docs at:   http://localhost:8000/docs
# AI service docs at:    http://localhost:8001/docs
```

### Team Division (4-person hackathon team)

| Role | Owns |
|---|---|
| **Engineer A (Full-stack lead)** | Next.js app structure, routing, auth flow, API client layer |
| **Engineer B (Map + UI)** | Leaflet map components, admin dashboard, all shadcn/ui components |
| **Engineer C (Backend)** | FastAPI routers, SQLAlchemy models, Alembic migrations, ORS integration |
| **Engineer D (AI)** | AI service, YOLOv8 integration, severity logic, cleanup verification |

**API contract agreed in Phase 0 (first 2 hours):** Engineers A+B mock the backend with static JSON files while C+D build the real API. When the real API is ready, swap the mock client for the real one. This parallelizes 80% of the work.

---

## 10. 🚀 Hackathon Optimization Plan

### Build Order (Non-Negotiable)

```
Hour 0-2:   Environment + API contract agreement
Hour 2-4:   DB schema + auth endpoints + seed script
Hour 4-8:   AI service (inference endpoint working with test image)
Hour 8-12:  Report submission endpoint + map markers rendering
Hour 12-16: Admin dashboard (table + assignment)
Hour 16-20: Route optimization (ORS + fallback)
Hour 20-24: Before/after verification flow
Hour 24-28: Gamification (points + leaderboard)
Hour 28-36: Hotspot layer + priority scoring + UX polish
Hour 36-40: Demo run-throughs + bug fixes
Hour 40-42: Lock code, final deploy, prepare talking points
```

### What to Mock / Simplify

| Feature | MVP Simplification | Full Implementation |
|---|---|---|
| **Reverse geocoding** | Display coordinates; add address text later | Nominatim lookup in background task |
| **SSE real-time updates** | TanStack Query polling every 30s | SSE stream (add in hour 28 if time allows) |
| **Refresh token rotation** | Single access token, 24hr expiry | Full rotation with Redis blacklist |
| **Image presigned upload** | Upload through backend API | Direct R2 presigned URL upload |
| **Hotspot DBSCAN** | Grid-cell frequency count | scikit-learn DBSCAN clustering |
| **Route sharing link** | Route ID in URL (already works) | Shareable short link |
| **Email notifications** | Dashboard warning banner | Email via SendGrid |

### Accelerators

**shadcn/ui CLI** — Install all needed components in one command:
```bash
npx shadcn-ui@latest add table drawer badge sheet toast dialog dropdown-menu
```
This gives you the entire admin dashboard's component set in 30 seconds.

**FastAPI auto-docs** — Your API is documented and testable at `/docs` from the first endpoint. No Postman setup needed for backend development.

**Alembic autogenerate** — After defining SQLAlchemy models, generate the entire migration:
```bash
alembic revision --autogenerate -m "initial schema"
```
All 5 tables from the PRD data model are created correctly, with PostGIS column types, in one command.

**Ultralytics one-liner** — The entire YOLOv8 inference is:
```python
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
results = model("image.jpg")
```
The AI service skeleton is 50 lines of code.

**Seed script strategy** — Pre-generate 50 incidents with realistic coordinates across 5 geographic clusters, varying severities, and 3 status states. Run this before every demo. This makes hotspots visible and the leaderboard populated without any manual data entry.

**Prebuilt maps pattern for Next.js + Leaflet:** Use dynamic imports with SSR disabled for all Leaflet components:
```typescript
const IncidentMap = dynamic(() => import('@/components/map/IncidentMap'), { 
  ssr: false,
  loading: () => <MapSkeleton />
});
```
Leaflet requires `window` to be defined — this pattern prevents the most common Next.js + Leaflet error and takes 2 minutes to implement correctly.

---

## 11. ⚠️ Trade-offs & Alternatives

### What Was NOT Chosen and Precisely Why

| Alternative | Why Rejected |
|---|---|
| **Django REST Framework** | Auto-admin is irrelevant here (you're building your own). DRF's ORM is synchronous — can't async-call the AI service without `sync_to_async` wrappers. FastAPI is faster to build and intrinsically async. |
| **tRPC (TypeScript end-to-end)** | Requires a Node.js backend, which creates the language boundary problem with Python AI. The type safety benefit of tRPC is replicated by Pydantic schemas + OpenAPI client generation. |
| **Prisma ORM** | Requires Node.js backend. Also: Prisma has no PostGIS support — geospatial operations would require raw SQL anyway. |
| **MongoDB / MongoDB Atlas** | No native geospatial query optimization comparable to PostGIS. `$geoNear` aggregation pipelines for spatial joins are significantly less expressive than PostGIS SQL. The PRD's spatial requirements (duplicate detection, hotspot clustering, viewport bounds queries) are all PostGIS-native operations. |
| **Supabase** | Excellent product but adds an abstraction layer over PostgreSQL that complicates PostGIS. Row-level security (RLS) policies would need to replicate your FastAPI role logic in SQL — double the auth surface. PostGIS extensions are available but less straightforward than direct PostgreSQL. |
| **Full WebSockets** | Overkill for one-directional status updates. SSE is HTTP, works through all proxies and CDNs, requires no connection manager, and has native browser support. WebSockets add a stateful connection layer that requires sticky sessions or a pub/sub broker (Redis Pub/Sub) in a multi-instance setup. |
| **Redux Toolkit** | 3-4x more boilerplate than Zustand for the same functionality. In a hackathon, the time spent writing Redux slices and action creators is time not spent building features. |
| **GraphQL** | The PRD has well-defined, stable query patterns (list incidents with filters, get route by ID, get leaderboard). GraphQL's flexibility is a liability here — it requires a schema definition, resolvers, and a client (Apollo or urql) that adds 4+ hours of setup for no benefit over typed REST + TanStack Query. |
| **Celery for background tasks** | Requires a separate worker process and Redis as a broker. For the 2-3 background tasks in the MVP (geocoding, points award, priority recalculation), FastAPI's built-in `BackgroundTasks` is sufficient and zero-dependency. Add Celery when you have >10 distinct background job types. |
| **Kubernetes** | Absolutely not for a hackathon. Railway manages container orchestration. Kubernetes adds 8+ hours of DevOps work. |
| **LangChain / LLM for detection** | YOLOv8 is purpose-built for object detection at 30+ fps. An LLM vision model (GPT-4o, Claude) would be 5-10x slower, 20x more expensive per inference, and less accurate on precise bounding box detection. The PRD explicitly names YOLO — there is no reason to deviate. |

### If Constraints Change

| Constraint Change | Stack Adaptation |
|---|---|
| **Need native mobile app** | Add React Native + Expo frontend. FastAPI backend unchanged. Shared TypeScript types via a `packages/types` monorepo package. |
| **Need real-time crew tracking** | Upgrade SSE → WebSockets with Redis Pub/Sub for fan-out to multiple admin clients. |
| **Need GPU inference** | Change AI service Dockerfile base image to `nvidia/cuda:12.0-runtime`. YOLOv8 auto-detects CUDA. Zero code change. |
| **Need multi-tenant** | Add `organization_id` to all tables. Row-level security in PostgreSQL. Tenant-aware JWT claims. |
| **Need offline PWA** | Add Next.js PWA plugin (`@ducanh2912/next-pwa`). Service worker caches the report form. IndexedDB queues offline submissions. |

---

## 12. 📈 Production Upgrade Path

### What Stays the Same (Zero Refactoring)
- PostgreSQL + PostGIS — this scales to millions of incidents with proper indexing and partitioning
- FastAPI backend — add more router modules, not a rewrite
- YOLOv8 — swap `yolov8n.pt` for TACO fine-tuned weights, zero code change
- Next.js frontend — add pages, components, and PWA support incrementally
- Docker containerization — directly translates to Kubernetes manifests
- OpenAPI contract — enables auto-generated client SDKs for mobile apps

### What Changes at Scale

**Phase 1 — 10x traffic (1,000 daily active users):**
- Add Redis caching for the incident map feed (cache by viewport bounds, invalidate on new report)
- Upgrade from FastAPI BackgroundTasks → Celery + Redis for reliable background job processing
- Add database read replica for dashboard queries (writes to primary, reads from replica)
- Add Sentry performance monitoring to identify the first bottlenecks

**Phase 2 — 100x traffic (multi-city deployment):**
- PostgreSQL table partitioning by `organization_id` (multi-tenant isolation)
- AI service → AWS Lambda + S3 trigger (stateless inference, auto-scales to zero)
- Add CDN in front of R2 for image thumbnail caching (Cloudflare is already in the path)
- Redis Pub/Sub for real-time events replacing SSE polling
- APM with Datadog or New Relic

**Phase 3 — Enterprise scale:**
- Kubernetes on EKS/GKE with horizontal pod autoscaling for backend and AI service
- Aurora PostgreSQL (AWS) with PostGIS — managed, multi-AZ, read replicas
- YOLO fine-tuning pipeline: real-world incident images → label → retrain → deploy
- Kafka for event streaming (incident created → trigger AI → trigger scoring → trigger points in a proper event-driven pipeline)
- Multi-region deployment with geographic routing

### The Architecture Story for Judges
*"We built this as a modular monolith with one isolated AI microservice — the same pattern used by companies like Shopify and Stack Overflow at massive scale. The database uses PostGIS for geospatial queries, which means adding cities is a configuration change, not a schema change. The AI service is containerized independently so we can scale inference horizontally, swap models without touching the core API, or move to GPU instances with zero code changes. The entire system can go from this Railway deployment to Kubernetes on AWS with no architectural refactoring — just infrastructure changes."*

That answer, delivered confidently, wins the technical architecture question.

---

### Final Stack Summary Card

```
┌─────────────────────────────────────────────────────────────┐
│                    CLEANGRID TECH STACK                     │
├─────────────────┬───────────────────────────────────────────┤
│ Frontend        │ Next.js 14 + Tailwind + shadcn/ui         │
│ Map             │ Leaflet.js + react-leaflet + OSM tiles    │
│ State           │ Zustand + TanStack Query v5               │
│ Backend         │ Python 3.11 + FastAPI (async)             │
│ AI Service      │ FastAPI + YOLOv8n (Ultralytics)           │
│ Database        │ PostgreSQL 15 + PostGIS 3.3               │
│ ORM             │ SQLAlchemy 2.0 async + Alembic            │
│ Cache           │ Redis 7 (Upstash in prod)                 │
│ Auth            │ JWT + bcrypt + HttpOnly cookies           │
│ Images          │ Cloudflare R2 (S3-compatible)             │
│ Routing API     │ OpenRouteService (+ nearest-neighbor fbk) │
│ Real-time       │ Server-Sent Events (SSE)                  │
│ Geocoding       │ Nominatim (OSM, free)                     │
│ Frontend deploy │ Vercel                                    │
│ Backend deploy  │ Railway (Docker containers)               │
│ Local dev       │ Docker Compose                            │
│ Testing         │ pytest + Playwright                       │
│ Monitoring      │ Sentry + Loguru + Railway metrics         │
└─────────────────┴───────────────────────────────────────────┘
```
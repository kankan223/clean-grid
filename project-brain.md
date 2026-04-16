# 🧠 CleanGrid Project Brain

**Status:** Active Development  
**Version:** 1.0  
**Last Updated:** 2026-04-16  
**Phase:** Phase 1: Core Reporting Loop (MVP)  

---

## 📋 Project Documentation Summary

### Core Loop (The Complete Operational Flow)
**Report → AI → Map → Assign → Route → Verify → Reward**

1. **Report**: Citizen uploads waste photo + location via web app
2. **AI**: YOLOv8n analyzes image, computes severity (Low/Medium/High), returns confidence
3. **Map**: Incident appears as color-coded marker on interactive Leaflet map
4. **Assign**: Admin triages, prioritizes, assigns to crew via dashboard
5. **Route**: System generates optimized collection route using OpenRouteService
6. **Verify**: Crew uploads after-photo, AI confirms cleanup, status updates
7. **Reward**: Points awarded to reporter and worker, leaderboard updates

### Key Value Proposition
CleanGrid closes the full operational loop that no competitor currently delivers. We turn waste management from a blind, schedule-based process into a real-time, AI-guided cleanup network.

---

## 🏗️ Architecture & Data Dictionary

### System Architecture
**Modular Monolith + Isolated AI Microservice**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js 14    │    │   FastAPI Core  │    │  AI Service     │
│   (Frontend)    │◄──►│  (Backend API)  │◄──►│  (YOLOv8n)      │
│   Vercel        │    │   Railway       │    │   Railway       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────▼────────┐              │
         │              │ PostgreSQL +    │              │
         │              │ PostGIS 3.3     │              │
         │              │   Railway       │              │
         └──────────────►│                 │◄─────────────┘
                        │ Redis (Upstash) │
                        │   Cache         │
                        └─────────────────┘
```

### Technology Stack Decisions
- **Frontend**: Next.js 14 (App Router) + Tailwind + shadcn/ui + Leaflet.js
- **Backend**: FastAPI + SQLAlchemy 2.0 (async) + Alembic
- **Database**: PostgreSQL 15 + PostGIS 3.3
- **AI**: YOLOv8n (Ultralytics) - separate FastAPI service
- **Maps**: Leaflet.js + OpenStreetMap tiles (no Mapbox)
- **Routing**: OpenRouteService API (with Haversine fallback)
- **Auth**: JWT with HttpOnly cookies (access: 15min, refresh: 7days)
- **Real-time**: Server-Sent Events (SSE), not WebSockets
- **Storage**: Cloudflare R2 (S3-compatible, no egress fees)
- **Cache**: Redis (leaderboard, rate limiting, session blacklist)

### Database Schema (PostgreSQL + PostGIS)

#### Core Tables
```sql
-- Users table
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE,
  password_hash VARCHAR,
  role ENUM('citizen', 'crew', 'admin'),
  points INTEGER DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Incidents table (spatial)
incidents (
  id UUID PRIMARY KEY,
  reporter_id UUID REFERENCES users(id),
  assigned_to UUID REFERENCES users(id),
  location GEOGRAPHY(POINT, 4326), -- PostGIS spatial column
  address_text VARCHAR,
  image_url VARCHAR,
  after_image_url VARCHAR,
  severity ENUM('Low', 'Medium', 'High', 'None'),
  status ENUM('Pending', 'Assigned', 'InProgress', 'Cleaned', 'Verified', 'NeedsReview'),
  priority_score INTEGER, -- 0-100 computed
  ai_confidence FLOAT,
  waste_detected BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  -- Spatial indexes
  INDEX idx_incidents_location USING GIST (location),
  INDEX idx_incidents_status (status),
  INDEX idx_incidents_priority (priority_score DESC)
)

-- Routes table
routes (
  id UUID PRIMARY KEY,
  assigned_to UUID REFERENCES users(id),
  ordered_stops JSONB, -- Array of incident IDs in order
  polyline_geojson JSONB, -- GeoJSON LineString
  total_distance_km FLOAT,
  estimated_duration_min INTEGER,
  is_approximate BOOLEAN, -- True if fallback used
  status ENUM('Active', 'Completed', 'Archived'),
  created_at TIMESTAMP
)

-- Points ledger
point_transactions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  incident_id UUID REFERENCES incidents(id),
  points INTEGER,
  reason VARCHAR, -- 'report_submitted', 'cleanup_verified', etc.
  created_at TIMESTAMP
)
```

### AI Inference Contract
```python
# POST /infer (AI Service)
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

**Severity Logic:**
- **High**: confidence ≥ 0.7 OR 3+ relevant detections
- **Medium**: confidence 0.45–0.69 OR 2 detections  
- **Low**: confidence 0.25–0.44 OR 1 detection
- **None**: confidence < 0.25

**Relevant YOLO Classes**: `{"bottle", "cup", "bag", "banana", "can", "backpack", "suitcase"}`

---

## Active Context & Working Memory

**Current Phase**: Phase 1: Core Reporting Loop (MVP) - Sprint 2 Complete
**Current Task**: Phase 1 Validation Gate
**Last Completed**: Core Reporting & Spatial Visualization - FULLY IMPLEMENTED
**Next Task**: Begin Phase 1 Sprint 3 (Admin Dashboard & Task Assignment)

**Recent Decisions**:
- React 18 for leaflet compatibility (avoid v19 conflicts)
- Fixed TypeScript/ESLint configuration for development
- Created complete modular monolith with isolated AI microservice
- Implemented exact severity scoring logic per tech stack
- All scaffolded files validated and building successfully
- Fixed Docker performance issues with optimized multi-stage builds
- Resolved Redis port conflict (6379 -> 6380)
- Fixed frontend Docker build dependencies
- Successfully validated PostgreSQL 15 + PostGIS 3.3.4
- Verified all services operational and interconnected
- **DATABASE LAYER**: Complete SQLAlchemy 2.0 async models with PostGIS Geography
- **AI SERVICE**: Working YOLOv8n simulation with deterministic severity scoring
- **DATA SEEDING**: 43 incidents across 5 geographic clusters for development
- **BACKEND API**: Complete CRUD operations with spatial queries and SSE events
- **FRONTEND UI**: Full reporting interface with image upload and location selection

**Current Blockers**: None - Full reporting loop implemented
**Validation Status**: PHASE 1 SPRINT 2 COMPLETE - Ready for Validation Gate

**Recent Decisions**:
- React 18 for leaflet compatibility (avoid v19 conflicts)
- Fixed TypeScript/ESLint configuration for development
- Created complete modular monolith with isolated AI microservice
- Implemented exact severity scoring logic per tech stack
- All scaffolded files validated and building successfully
- Fixed Docker performance issues with optimized multi-stage builds
- Resolved Redis port conflict (6379 -> 6380)
- Fixed frontend Docker build dependencies
- Successfully validated PostgreSQL 15 + PostGIS 3.3.4
- Verified all services operational and interconnected
- **DATABASE LAYER**: Complete SQLAlchemy 2.0 async models with PostGIS Geography
- **AI SERVICE**: Working YOLOv8n simulation with deterministic severity scoring
- **DATA SEEDING**: 43 incidents across 5 geographic clusters for development

**Current Blockers**: None - Data layer fully implemented
**Validation Status**: PHASE 1 SPRINT 1 COMPLETE - Ready for API & Frontend development

### Active File Paths
- `/docs/PRD.md` - Complete product requirements
- `/docs/design.md` - UI/UX specifications and screen breakdowns  
- `/docs/tech-stake.md` - Technical architecture and stack decisions
- `/project-brain.md` - This file (working memory)
- `/implementation-roadmap.md` - Detailed implementation plan

### Current Task
Initialize project tracking system with `project-brain.md` and `implementation-roadmap.md` before writing any application code.

---

## 🚫 Anti-Hallucination Guardrails

### Strict Technical Rules (NEVER VIOLATE)

1. **Database**: DO NOT use Prisma; use SQLAlchemy 2.0 async
2. **Maps**: DO NOT use Mapbox; use Leaflet.js with OpenStreetMap tiles
3. **Real-time**: DO NOT use WebSockets; use SSE for real-time updates
4. **Routing**: DO NOT build custom TSP solver; use OpenRouteService API
5. **Next.js**: ALWAYS dynamically import Leaflet with `ssr: false`
6. **Auth**: DO NOT store JWTs in localStorage; use HttpOnly cookies
7. **AI**: DO NOT use heavy YOLO models; use YOLOv8n for speed
8. **File Storage**: DO NOT use AWS S3; use Cloudflare R2 (no egress fees)
9. **State Management**: DO NOT use Redux; use Zustand for client state
10. **API Calls**: DO NOT use useEffect for data fetching; use TanStack Query

### Implementation Boundaries
- **MVP Scope**: Core loop only (Report → AI → Map → Assign → Route → Verify → Reward)
- **No IoT**: Smart bin hardware integration explicitly out of scope
- **No Native Apps**: Mobile-responsive web only
- **No Blockchain**: Points system uses simple database ledger
- **No Drone Routing**: Ground vehicle routing only

### Quality Gates
- Every phase MUST have validation gate before proceeding
- All database indexes MUST be created from day one
- AI service MUST be isolated (separate container)
- All user inputs MUST be validated via Pydantic schemas
- No hardcoded API keys or secrets in code

---

## 📝 Backlog & Technical Debt

### Deferred Items (Post-MVP)
1. **Advanced Hotspot Prediction**: Current grid aggregation → scikit-learn DBSCAN clustering
2. **Offline PWA**: Service worker for offline report submission
3. **Real-time Crew Tracking**: WebSocket upgrade for live crew locations
4. **Multi-tenant SaaS**: City-level isolation and management
5. **Advanced Analytics**: Time-series prediction and trend analysis

### Known Edge Cases (Handle Later)
1. **Duplicate Detection**: Reports within 20 meters flagged for admin review
2. **AI Service Down**: Graceful fallback to "Pending AI Review" status
3. **Route API Rate Limits**: Implement caching and retry logic
4. **Image Quality Issues**: Low-light or blurry photos affecting AI accuracy
5. **Geocoding Failures**: Address lookup failures, fall back to coordinates

### Performance Optimizations (Future)
1. **Database Read Replicas**: For scaling admin dashboard queries
2. **CDN Image Optimization**: Automatic image resizing and compression
3. **AI Model Quantization**: Reduce inference time further
4. **Connection Pooling**: Optimize database connection management
5. **Client-side Caching**: Implement service worker for map tiles

### Security Enhancements (V2)
1. **Rate Limiting Per User**: Currently IP-based only
2. **Image Content Scanning**: Detect inappropriate uploads
3. **Audit Logging**: Track all admin actions for compliance
4. **Role-based Access Control**: Granular permissions beyond basic roles
5. **API Key Rotation**: Automated external API key management

---

## 🔄 Update Log

### 2025-04-15 - Initial Creation
- Created project-brain.md with complete architecture summary
- Established anti-hallucination guardrails
- Documented current phase and active context
- Set up backlog and technical debt tracking

### Next Update Required
After completing Phase 0 validation gate, update:
- Move to Phase 1 status
- Add actual database connection details
- Document any deviations from planned architecture
- Update active file paths with generated code structure

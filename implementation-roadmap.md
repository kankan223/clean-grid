# CleanGrid Implementation Roadmap

## Phase 0: Environment & Scaffolding (The Foundation)

### Setup Docker Compose
- [x] Create docker-compose.yml with 5 services: frontend, backend, ai-service, db, redis
- [x] Configure PostgreSQL 15 + PostGIS 3.3 container
- [x] Set up Redis 7 container
- [x] Create .env.example files for all services
- [x] Add health checks and proper dependencies

### Initialize Next.js 14 Frontend
- [x] `npx create-next-app@14 frontend --typescript --tailwind --app`
- [x] Install shadcn/ui components (Table, Drawer, Badge, etc.)
- [x] Set up project structure: app/(map), components/map, lib/stores
- [x] Configure Leaflet.js with dynamic imports (ssr: false)
- [x] Install TanStack Query and Zustand

### Initialize FastAPI Backend
- [x] Create FastAPI project structure with routers/ models/ schemas/ services/
- [x] Set up SQLAlchemy 2.0 async with asyncpg driver
- [x] Configure Alembic for migrations
- [x] Create core/auth.py with JWT logic
- [x] Set up Redis client connection

### Initialize AI Service
- [x] Create separate FastAPI service for YOLOv8n inference
- [x] Install ultralytics, Pillow, OpenCV
- [x] Implement /infer endpoint with severity logic
- [x] Add model download script for yolov8n.pt

### Validation & Testing Gate
- [x] Spin up all containers: `docker compose up --build`
- [x] Verify database connection: test PostGIS extension
- [x] Check Swagger UI loads: http://localhost:8000/docs
- [x] Test AI service docs: http://localhost:8001/docs
- [x] Confirm frontend builds and serves at :3000

---

## Phase 1: Core Reporting Loop (MVP)

### Database Schema
- [x] Create User table with roles and points
- [x] Create Incident table with PostGIS location column
- [x] Add spatial indexes: GIST on location, B-tree on status/priority
- [x] Create Point_transactions table for gamification
- [x] Write seed script with 30-50 sample incidents

### AI Service Integration
- [x] Implement YOLOv8n inference endpoint
- [x] Add severity computation logic (High/Medium/Low/None)
- [x] Create bounding box annotation for result images
- [x] Add confidence threshold (0.45 default)
- [x] Implement error handling for timeouts

### Backend API Core
- [x] POST /api/reports (multipart upload, AI call, DB insert)
- [x] GET /api/incidents (with spatial query for map)
- [x] PATCH /api/incidents/:id/status
- [x] Add JWT auth middleware
- [x] Implement reverse geocoding with Nominatim
- [x] SSE events for real-time updates

### Frontend Map & Reporting
- [x] Build IncidentMap component with Leaflet
- [x] Create SeverityMarker component (color-coded pins)
- [x] Implement ReportWaste form with image upload
- [x] Add LocationPicker with GPS + manual pin
- [x] Create AIResultCard for analysis feedback

### Validation & Testing Gate
- [x] Upload test image via frontend
- [x] Verify AI JSON response (severity, confidence)
- [x] Check PostGIS insert with spatial data
- [x] Confirm map marker renders correctly
- [x] Test complete report flow end-to-end

---

## Phase 2: Admin Dashboard & Task Assignment

### Authentication System
- [x] Implement JWT login endpoint
- [x] Create refresh token rotation
- [x] Add HttpOnly cookie handling
- [x] Build role-based access control
- [x] Create admin guard middleware

### Admin Dashboard UI
- [ ] Build IncidentTable with sorting/filtering
- [ ] Create DetailDrawer for incident details
- [ ] Implement BulkActionBar for selection
- [ ] Add synchronized AdminMapPanel
- [ ] Create status override controls

### Task Assignment Backend
- [ ] GET /api/incidents with filters/pagination
- [ ] PATCH /api/incidents/:id/assign
- [ ] GET /api/incidents/stats for dashboard KPIs
- [ ] Implement SSE endpoint for real-time updates
- [ ] Add crew management endpoints

### Frontend Admin Features
- [ ] Connect table to API with TanStack Query
- [ ] Implement optimistic updates for status changes
- [ ] Add filter bar with status/severity/date filters
- [ ] Create assign dropdown with crew workload
- [ ] Build real-time sync via SSE

### Validation & Testing Gate
- [ ] Authenticate as admin user
- [ ] Filter incidents by status/severity
- [ ] Assign task to crew member
- [ ] Verify optimistic UI update
- [ ] Confirm database state change

---

## Phase 3: Route Optimization

### OpenRouteService Integration
- [ ] Create ORS client with API key handling
- [ ] Implement POST /api/routes endpoint
- [ ] Add nearest-neighbor fallback algorithm
- [ ] Store routes with GeoJSON polylines
- [ ] Handle rate limiting and errors

### Route Generation Backend
- [ ] Accept incident IDs and optional depot
- [ ] Call ORS optimization API
- [ ] Process response into ordered stops
- [ ] Calculate distance and duration
- [ ] Mark approximate routes when fallback used

### Frontend Route View
- [ ] Create /route/[id] page
- [ ] Build RouteMap with polyline rendering
- [ ] Implement StopListPanel with ordered stops
- [ ] Add numbered stop markers on map
- [ ] Create "Start Navigation" deep link

### Route Management
- [ ] Add route generation from admin dashboard
- [ ] Implement route sharing via links
- [ ] Create route status tracking
- [ ] Add route completion workflow
- [ ] Build route history view

### Validation & Testing Gate
- [ ] Select 5 incidents from admin dashboard
- [ ] Generate optimized route via ORS
- [ ] Verify polyline loads on frontend map
- [ ] Test route sharing functionality
- [ ] Force ORS failure, test Haversine fallback

---

## Phase 4: Gamification & Verification

### Cleanup Verification
- [ ] POST /api/incidents/:id/verify endpoint
- [ ] Reuse AI service for after-photo analysis
- [ ] Implement status logic (Verified/Needs Review)
- [ ] Add before/after image comparison
- [ ] Create verification history tracking

### Points System
- [ ] Implement points ledger logic
- [ ] Add award rules: report (+10), verification (+25)
- [ ] Create leaderboard calculation
- [ ] Cache top-20 leaderboard in Redis
- [ ] Build badge tiers (Cleaner/Guardian/Hero)

### Frontend Verification
- [ ] Build /task/[id] cleanup verification page
- [ ] Create before/after image viewer
- [ ] Implement after-photo upload
- [ ] Add verification result display
- [ ] Show points awarded animations

### Leaderboard & Profile
- [ ] Create /leaderboard page
- [ ] Build user profile with report history
- [ ] Implement badge display system
- [ ] Add points breakdown view
- [ ] Create community stats section

### Validation & Testing Gate
- [ ] Upload after-photo for cleanup task
- [ ] Verify status changes to 'Verified' or 'Needs Review'
- [ ] Check Redis leaderboard cache updates
- [ ] Confirm points awarded correctly
- [ ] Test badge tier progression

---

## Phase 5: Polish, Edge Cases & Deployment

### Edge Cases & Error Handling
- [ ] Handle AI service downtime gracefully
- [ ] Implement duplicate detection (20m radius)
- [ ] Add rate limiting per IP (Redis sliding window)
- [ ] Create empty states for all screens
- [ ] Build loading skeletons and error toasts

### Performance Optimization
- [ ] Add database connection pooling
- [ ] Implement client-side caching with TanStack Query
- [ ] Optimize map tile loading
- [ ] Add image compression for uploads
- [ ] Create background job for priority recalculation

### Deployment Configuration
- [ ] Set up Vercel frontend deployment
- [ ] Configure Railway backend deployment
- [ ] Add environment variable management
- [ ] Create production Dockerfiles
- [ ] Set up monitoring and logging

### Final Testing & Documentation
- [ ] Run full E2E test with Playwright
- [ ] Test complete user flows manually
- [ ] Verify all validation gates passed
- [ ] Update API documentation
- [ ] Create deployment runbook

### Validation & Testing Gate
- [ ] Complete E2E test suite passes
- [ ] All core features work in production
- [ ] Performance meets requirements (<10s AI inference)
- [ ] Security audit passed
- [ ] Demo-ready with seeded data

---

## Success Criteria

### MVP Complete When:
- [ ] Citizen can report waste with photo and location
- [ ] AI detects and classifies waste severity
- [ ] Map shows all incidents with color-coded markers
- [ ] Admin can assign tasks and generate routes
- [ ] Crew can verify cleanup with after-photo
- [ ] Points system and leaderboard work
- [ ] Complete loop works without manual intervention

### Production Ready When:
- [ ] All validation gates passed
- [ ] Performance benchmarks met
- [ ] Security measures implemented
- [ ] Error handling comprehensive
- [ ] Deployment automated
- [ ] Documentation complete
- [ ] Demo stable with seeded data

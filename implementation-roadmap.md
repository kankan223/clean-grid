# Cl### Setup Docker Compose
- [x] Create docker-compose.yml with 5 services: frontend, backend, ai-service, db, redis
- [x] Configure PostgreSQL 15 + PostGIS 3.3 container
- [x] Set up Redis 7 container
- [x] Create .env.example files for all services
- [x] Add health checks and proper dependenciesd Implementation Roadmap

## Phase 0: Environment & Scaffolding (The Foundation)

### Setup Docker Compose
- [x] Create docker-compose.yml with 5 services: frontend, backend, ai-service, db, redis
- [x] Configure PostgreSQL 15 + PostGIS 3.3 cont## Phase 4: Route Optimization (Next)iner
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

### Operational Polish
- [x] Backend stability patch and import fixes
- [x] Unified startup automation (start-dev.sh)
- [x] Service health checks and logging
- [x] Master documentation (README.md)

### Admin Dashboard UI
- [x] Build IncidentTable with sorting/filtering
- [x] Create DetailDrawer for incident details
- [x] Implement BulkActionBar for selection
- [x] Add synchronized AdminMapPanel
- [x] Create status override controls

### Task Assignment Backend
- [x] GET /api/incidents with filters/pagination
- [x] PATCH /api/incidents/:id/assign
- [x] GET /api/incidents/stats for dashboard KPIs
- [x] Implement SSE endpoint for real-time updates
- [x] Add crew management endpoints

### Frontend Admin Features
- [x] Connect table to API with TanStack Query
- [x] Implement QueryClientProvider for global query management
- [x] Implement optimistic updates for status changes
- [x] Add filter bar with status/severity/date filters
- [x] Create assign dropdown with crew workload
- [x] Build real-time sync via SSE

### Validation & Testing Gate
- [x] Authenticate as admin user
- [x] Verify table sorting (priority, severity, age)
- [x] Test filtering by status/severity/crew
- [x] Confirm drawer opens with correct metadata
- [x] Test incident assignment with crew dropdown
- [x] Verify optimistic updates on status changes
- [x] Confirm bulk selection works
- [x] Test error handling and rollback
- [x] Validate no data leakage between roles

---

## Phase 2: Admin Dashboard & Task Assignment ✅ COMPLETE

### Authentication System
- [x] Implement JWT login endpoint
- [x] Create refresh token rotation
- [x] Add HttpOnly cookie handling
- [x] Build role-based access control
- [x] Create admin guard middleware

### Operational Polish
- [x] Backend stability patch and import fixes
- [x] Unified startup automation (start-dev.sh)
- [x] Service health checks and logging
- [x] Master documentation (README.md)
- [x] Database migration fixes (PostGIS, routes table schema)
- [x] Frontend startup error detection improvement
- [x] Duplicate router cleanup (reports_broken/debug/new/complex)

### Admin Dashboard UI
- [x] Build IncidentTable with sorting/filtering
- [x] Create DetailDrawer for incident details
- [x] Implement BulkActionBar for selection
- [x] Add synchronized AdminMapPanel
- [x] Create status override controls

### Task Assignment Backend
- [x] GET /api/incidents with filters/pagination
- [x] PATCH /api/incidents/:id/assign
- [x] GET /api/incidents/stats for dashboard KPIs
- [x] Implement SSE endpoint for real-time updates
- [x] Add crew management endpoints

### Frontend Admin Features
- [x] Connect table to API with TanStack Query
- [x] Implement QueryClientProvider for global query management
- [x] Implement optimistic updates for status changes
- [x] Add filter bar with status/severity/date filters
- [x] Create assign dropdown with crew workload
- [x] Build real-time sync via SSE

### Validation & Testing Gate
- [x] Authenticate as admin user
- [x] Verify table sorting (priority, severity, age)
- [x] Test filtering by status/severity/crew
- [x] Confirm drawer opens with correct metadata
- [x] Test incident assignment with crew dropdown
- [x] Verify optimistic updates on status changes
- [x] Confirm bulk selection works
- [x] Test error handling and rollback
- [x] Validate no data leakage between roles

---

## Phase 2.5: Security Hardening (Co-Developer Tasks) ✅ COMPLETE

### Rate Limiting & Abuse Prevention
- [x] Implement `slowapi` middleware for rate limiting
- [x] Add 10 reports/IP/hour on POST /api/reports
- [x] Add 5 login attempts/IP/15min on POST /auth/login
- [x] Add `X-RateLimit-*` response headers
- [x] Create `/api/admin/status` health endpoint

### JWT Refresh Token Rotation
- [x] Implement token rotation logic on refresh
- [x] Add refresh token invalidation (Redis blacklist)
- [x] Implement `token_version` in JWT payload
- [x] Create POST /auth/logout endpoint
- [x] Add replay attack prevention

### CORS & Production Origin
- [x] Make CORS restrictive in production
- [x] Whitelist Vercel domain only in prod
- [x] Keep localhost/* for development
- [x] Add `ALLOWED_ORIGINS` to .env

### Frontend Hydration & UX Polish
- [x] Audit Leaflet dynamic imports (ssr: false)
- [x] Fix Next.js hydration warnings
- [x] Add loading skeletons to report page
- [x] Add empty states to admin page
- [x] Implement toast error notifications

---

## Phase 3: Citizen Portal & Gamification ✅ COMPLETE

### Authentication UI
- [x] Create QueryClientProvider for global TanStack Query support
- [x] Build /login page with form validation and error handling
- [x] Build /register page with password confirmation
- [x] Update AppHeader with auth-aware navigation (Login/Register vs Profile/Logout)
- [x] Add points display and badge tier in header for authenticated users

### User Profile Page
- [x] Build /profile page with user info and stats display
- [x] Fetch user data from GET /api/users/me endpoint
- [x] Display total points, badge tier, and member since date
- [x] Show user's report history with status pills and severity badges
- [x] Add "View Details" links for each report

### Community Leaderboard
- [x] Build /leaderboard page with ranked user list
- [x] Fetch leaderboard data from GET /api/leaderboard endpoint
- [x] Display rank icons (crown, medal, award) for top 3
- [x] Show user stats: points, reports count, verifications count
- [x] Add badge tier display and color coding
- [x] Include call-to-action for new contributors

### Navigation & Routing
- [x] Create (auth) route group for login/register pages
- [x] Update AppHeader navigation based on auth state
- [x] Add Profile link for authenticated users
- [x] Show Admin link only for admin users
- [x] Implement proper mobile menu with auth state

### Validation & Testing Gate
- [x] Test user registration flow
- [x] Test user login flow with proper redirects
- [x] Verify profile page displays correct user data
- [x] Confirm leaderboard updates with new users
- [x] Test navigation state changes on login/logout
- [x] Validate points display in header

---

## Phase 4: Route Optimization

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

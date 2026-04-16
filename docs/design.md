# 🎨 CleanGrid — Complete Design Specification (design.md)

**Version:** 1.0  
**Based on:** PRD v1.0 + UI Design Mockups  
**Audience:** Frontend Developers, Backend Developers, AI Code Agents  
**Status:** Implementation-Ready

---

## 1. 🧩 Design Overview

### Product Summary
CleanGrid is a web-first, AI-powered smart waste operations platform. It closes the full operational loop: **waste reported → AI analyzed → mapped → prioritized → crew dispatched → route optimized → cleanup verified → contributor rewarded.** No competitor currently delivers this complete loop in one platform.

### Design Goals
| Goal | Rationale |
|---|---|
| **Spatial-first** | Every operational screen keeps the map visible; waste management is inherently geographic |
| **Operational clarity** | Every screen enables an action, not just information display |
| **Role-aware UI** | Citizens see reporting; admins see command center; crew sees tasks |
| **Sub-60s first action** | A new user must be able to submit a waste report without instruction |
| **Graceful degradation** | AI failures, routing failures, and network drops must never crash the UX |
| **Demo-stable** | All critical flows must work with seeded data if live APIs are unavailable |

### Target Users (UX Perspective)
| Persona | Primary Screen | Key UX Need |
|---|---|---|
| **Maya** (Admin) | Admin Dashboard | Command-center overview with one-click triage |
| **Carlos** (Crew Supervisor) | Route View | Ordered stop list with map context |
| **Ravi** (Field Worker) | Crew Verification | Simple mobile task + photo upload |
| **Sofia** (Citizen Reporter) | Report Waste | Frictionless photo → pin → submit in < 60s |
| **Dr. Priya** (City Planner) | Analytics / Hotspot | Heatmap and trend data |

### Design Principles
1. **Map is king.** The interactive map is the hero element on every spatial screen.
2. **Drawers over modals.** Drawers preserve spatial context; modals destroy it.
3. **Color = severity.** Red (High), Orange (Medium), Green (Low), Gray (Cleaned). Never deviate.
4. **Skeleton loaders everywhere.** No bare spinners; all data-dependent regions use skeletons.
5. **Role-gated UI.** Admin-only elements are hidden (not disabled) for non-admin users.
6. **Mobile-first layout.** Report and crew flows are designed mobile-first; admin dashboard is desktop-first with a mobile fallback.

### Visual Design Direction
- **Aesthetic:** Clean civic-tech — professional, trustworthy, operational. Inspired by fleet management dashboards and modern GIS tools.
- **Color palette:**
  - Primary Brand: `#1A6B3C` (deep civic green)
  - Accent: `#2E86DE` (operational blue)
  - Severity High: `#E84855` (alert red)
  - Severity Medium: `#F9A03F` (amber orange)
  - Severity Low: `#4CAF50` (safe green)
  - Cleaned/Verified: `#9E9E9E` (neutral gray)
  - Background: `#F5F7FA`
  - Surface: `#FFFFFF`
  - Text Primary: `#1A1A2E`
  - Text Secondary: `#6B7280`
- **Typography:**
  - Display/Headings: `DM Sans` (bold, geometric, civic)
  - Body/Data: `IBM Plex Sans` (technical, legible, tabular numbers)
  - Monospace (IDs, coordinates): `JetBrains Mono`
- **Spacing system:** 4px base unit. All spacing is multiples of 4: `4, 8, 12, 16, 20, 24, 32, 40, 48, 64`.
- **Border radius:** `4px` (cards/inputs), `8px` (modals/drawers), `999px` (badges/pills).
- **Shadow system:**
  - `shadow-sm`: `0 1px 2px rgba(0,0,0,0.06)`
  - `shadow-md`: `0 4px 12px rgba(0,0,0,0.10)`
  - `shadow-lg`: `0 8px 24px rgba(0,0,0,0.15)`

---

## 2. 🗺️ Screen Architecture

| # | Screen Name | Route | Purpose | Entry Points | Exit / Navigation |
|---|---|---|---|---|---|
| 1 | **Landing / Map Home** | `/` | Primary map view with all incidents | Direct URL, logo click, back from any screen | Report Waste CTA, marker popup, nav links |
| 2 | **Report Waste** | `/report` | Citizen submits a waste incident | "Report Waste" button on home/nav | Submit (→ result card → home), Cancel (→ home) |
| 3 | **Admin Dashboard** | `/admin` | Admin triage, assignment, overview | Nav (admin role only), login redirect | Route planning, detail drawer, logout |
| 4 | **Route View** | `/route/:id` | Optimized collection route display | Admin "Generate Route" action, shared link | Back to admin, "Start Navigation" deep link |
| 5 | **Cleanup Verification** | `/task/:id` | Crew before/after cleanup workflow | Assignment notification, crew task list | Back to task list, route view |
| 6 | **Leaderboard** | `/leaderboard` | Public citizen points ranking | Nav, post-submission prompt | Home, Profile |
| 7 | **Profile / Login** | `/profile`, `/login` | Auth + user stats and report history | Nav, post-submit CTA for anonymous users | Home, Admin dashboard (if admin) |
| 8 | **Analytics / Hotspot** | `/analytics` | Heatmap, trend data, hotspot zones | Nav (admin/planner role), admin dashboard | Admin dashboard, map home |
| 9 | **Error / Empty States** | `*`, embedded | 404, empty data, AI failure states | Direct wrong URL, empty data conditions | Go Back to Home CTA |

---

## 3. 📱 Screen-by-Screen Breakdown

---

### 🔹 Screen 1: Landing / Map Home (`/`)

#### Layout Structure
```
┌──────────────────────────────────────────────────────────┐
│  HEADER (sticky, 64px)                                   │
│  [Logo] [Map] [Report] [Leaderboard] [Profile] [Admin?]  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│           FULL-VIEWPORT MAP (calc(100vh - 64px))         │
│                                                          │
│  ┌─────────────────┐        ┌──────────────────────┐    │
│  │ Map Controls    │        │  Layer Toggles       │    │
│  │ (top-left)      │        │  [Heatmap] [Hotspot] │    │
│  └─────────────────┘        └──────────────────────┘    │
│                                                          │
│              [Incident Markers: Red/Orange/Green/Gray]   │
│                                                          │
│                    ┌─────────────────────┐               │
│                    │ 🗑 Report Waste (CTA)│               │
│                    └─────────────────────┘               │
│                    (bottom-center mobile / top-right desk)│
└──────────────────────────────────────────────────────────┘
```

#### UI Components

| Component | Position | Purpose | Props |
|---|---|---|---|
| **AppHeader** | Top, sticky, z-50 | Global navigation | `userRole`, `isAuthenticated` |
| **MapContainer** | Full viewport below header | Leaflet map host | `center`, `zoom`, `incidents[]` |
| **SeverityMarker** | Map overlay, per incident | Color-coded incident pins | `severity`, `status`, `lat`, `lng`, `id` |
| **MarkerClusterGroup** | Map overlay | Auto-clusters >10 visible markers | `maxClusterRadius: 80` |
| **MarkerPopup** | On marker click | Quick incident preview | `imageUrl`, `severity`, `status`, `timestamp`, `incidentId` |
| **HeatmapLayer** | Map overlay (togglable) | Incident density visualization | `points[]`, `visible` |
| **HotspotLayer** | Map overlay (togglable) | Historical hotspot zones | `zones[]`, `visible` |
| **LayerToggleBar** | Top-right of map | Toggle heatmap and hotspot layers | `heatmapActive`, `hotspotActive`, `onToggle` |
| **ReportWasteFAB** | Bottom-center (mobile), top-right (desktop) | Primary CTA | `onClick` |
| **MapLoadingSkeleton** | Full viewport, visible on load | Skeleton while tiles load | - |
| **EmptyMapBanner** | Bottom overlay, conditional | "No active incidents" state | `visible` |

#### User Interactions

| Interaction | Behavior |
|---|---|
| **Click SeverityMarker** | Opens MarkerPopup anchored to pin; highlights row in any visible table |
| **Click "View Details" in popup** | Navigates to `/admin` with that incident pre-selected (admin) or shows read-only drawer (citizen) |
| **Click HeatmapToggle** | Adds/removes Leaflet.heat overlay; button state toggled; preference saved to `localStorage` |
| **Click HotspotToggle** | Adds/removes hotspot polygon layer; fetches `/api/hotspots` if not yet loaded |
| **Click ReportWasteFAB** | Navigates to `/report` |
| **Map zoom/pan** | Leaflet native; clusters update automatically |
| **Map initial load** | Auto-fits viewport to show all active incidents via `map.fitBounds(bounds)` |

#### Backend Integration

**Load incidents on map mount:**
```
GET /api/incidents?status=active&fields=id,lat,lng,severity,status,imageUrl,createdAt
→ Response: { incidents: [{ id, lat, lng, severity, status, imageUrl, createdAt }] }
→ State: set incidentMarkers[]
→ Polling: every 30s via setInterval (or WebSocket `incident.updated` event)
```

**Load hotspot zones (on toggle):**
```
GET /api/hotspots
→ Response: { zones: [{ id, polygon, incidentCount, recurrenceScore }] }
→ State: set hotspotZones[] (cached; do not re-fetch unless stale >1hr)
```

#### Data Binding
- `incidents[]`: from `GET /api/incidents`, refreshed every 30s
- `hotspotZones[]`: lazy-loaded on first toggle, cached in component state
- `userRole`: from auth context (determines admin nav visibility)

#### States
- **Loading:** Full-viewport skeleton map + spinner overlay on top; markers load progressively after tiles
- **Empty:** Map renders normally; bottom banner "No active incidents. Be the first to report." with ReportWasteFAB highlighted
- **Error (API fail):** Toast notification "Could not load incidents. Showing last known data." with retry link; stale markers remain visible
- **Normal:** Map with all markers; layers togglable

---

### 🔹 Screen 2: Report Waste (`/report`)

#### Layout Structure
```
┌─────────────────────────────────────────────────┐
│  HEADER                                         │
├─────────────────────────────────────────────────┤
│  ← Back to Map                                  │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │  STEP 1: Upload Photo                   │    │
│  │  [Drag & Drop Zone / File Picker]        │    │
│  │  [Image Preview + Remove button]         │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │  STEP 2: Location                       │    │
│  │  [Use My Location] / [Pick on Map]       │    │
│  │  [Mini-map with draggable pin]           │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │  STEP 3: Description (optional)         │    │
│  │  [Textarea, 200 char limit + counter]    │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  [Severity Pills: Low | Medium | High]          │
│  [Submit Report Button]                         │
└─────────────────────────────────────────────────┘
```

**Post-Submit overlay (replaces form):**
```
┌────────────────────────────────────────┐
│  🔍 Analyzing image...  (animated)     │
│                                        │
│  [Annotated image with bounding boxes] │
│  Severity: HIGH  Confidence: 82%       │
│                                        │
│  ✅ +10 points added! (if logged in)   │
│  [View on Map] [Report Another]        │
└────────────────────────────────────────┘
```

#### UI Components

| Component | Position | Purpose |
|---|---|---|
| **BackLink** | Top-left, below header | Navigate back to `/` without losing context |
| **ImageUploadZone** | Step 1, full width | Drag-and-drop or click-to-upload image; max 10MB |
| **ImagePreview** | Step 1, after upload | Shows thumbnail + remove button; file name + size |
| **LocationSelector** | Step 2 | Toggle: GPS button OR interactive mini-map pin |
| **MiniMap** | Step 2, 300px height | Leaflet mini-map with draggable pin for manual location |
| **CoordinateDisplay** | Step 2, below MiniMap | Shows resolved `lat, lng` or address text |
| **NoteTextarea** | Step 3 | Optional 200-char text input with live character counter |
| **SeverityPills** | Below Step 3 | Read-only display of AI-predicted severity (pre-submit hidden; post-AI shown) |
| **SubmitButton** | Bottom, full width | Disabled until image + location provided |
| **AnalysisLoader** | Post-submit overlay | Animated status card "Analyzing image..." |
| **AIResultCard** | Post-submit overlay | Annotated image, severity badge, confidence %, points earned |

#### User Interactions

| Action | Behavior |
|---|---|
| **Drag image to zone** | File accepted; preview rendered; file validated (type, size) |
| **Click upload zone** | Opens OS file picker |
| **Click "Use My Location"** | Calls `navigator.geolocation.getCurrentPosition()`; updates pin and coordinate display |
| **Drag mini-map pin** | Updates `lat/lng` in form state; reverse-geocodes to address text via `/api/geocode/reverse` |
| **Type in textarea** | Live character counter updates; hard-blocked at 200 chars |
| **Click Submit** | Validates form → shows AnalysisLoader → POSTs to API → shows AIResultCard |
| **Click "View on Map"** | Navigates to `/` with new pin auto-highlighted |
| **Click "Report Another"** | Resets form to empty state |

#### Backend Integration

**Submit report:**
```
POST /api/reports
Content-Type: multipart/form-data
Body: {
  image: File,
  lat: float,
  lng: float,
  note: string (optional, max 200)
}
→ Immediate response (202 Accepted): { reportId: uuid, status: "processing" }
→ Poll GET /api/reports/:id every 2s until status != "processing"
→ OR use SSE: GET /api/reports/:id/stream → event: "analysis_complete"
→ Final response: {
    id: uuid,
    wasteDetected: boolean,
    confidence: float,
    severity: "Low"|"Medium"|"High"|"None",
    boundingBoxes: [{ class, confidence, box: [x1,y1,x2,y2] }],
    annotatedImageUrl: string,
    pointsAwarded: int | null
  }
```

**Reverse geocode (on pin drag):**
```
GET /api/geocode/reverse?lat={lat}&lng={lng}
→ Response: { addressText: string }
```

#### Data Binding
- `imageFile`: local File object
- `lat`, `lng`: from GPS or pin drag
- `note`: local textarea state
- `analysisResult`: from API response, used to render AIResultCard

#### States
- **Initial:** Empty form; Submit disabled
- **Image selected:** Preview shows; location step highlighted
- **Location set:** Submit enabled if image also present
- **Submitting:** AnalysisLoader visible; form fields hidden; cannot cancel
- **AI success (waste detected):** AIResultCard with severity, confidence, annotated image, points
- **AI success (no waste):** AIResultCard showing "No waste detected"; option to submit anyway for admin review (no points)
- **AI failure (timeout/down):** AIResultCard shows "Analysis pending — your report was saved. An admin will review it."
- **Upload error (network):** Toast "Upload failed. Retrying..." (3 retries with backoff) then "Upload failed — please try again" with retry button
- **File too large:** Inline error below upload zone "File exceeds 10MB limit. Please compress or choose another image."
- **Wrong file type:** Inline error "Only JPEG, PNG, and WEBP images are accepted."

#### Validation Rules
```javascript
// Client-side validation before submit
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE_BYTES = 10 * 1024 * 1024; // 10MB

validate: {
  image: required, type in ALLOWED_TYPES, size <= MAX_SIZE_BYTES,
  lat: required, float, range [-90, 90],
  lng: required, float, range [-180, 180],
  note: optional, string, maxLength 200
}
```

---

### 🔹 Screen 3: Admin Dashboard (`/admin`)

#### Layout Structure
```
┌────────────────────────────────────────────────────────────────────┐
│  HEADER + Admin Nav (Dashboard | Assign | Map | Hotspot | More)     │
├─────────────────────────────────────────────────────────────────────┤
│  TOP BAR: [Hello, Maya.] [Priority Tasks ▼] [Manage Tasks]         │
│  STATS ROW: [32 Active] [14 In Progress] [6 Verified Cleanup]       │
├──────────────────────────────────────┬──────────────────────────────┤
│  LEFT PANEL (60% width)              │  RIGHT PANEL (40% width)     │
│                                      │                              │
│  FILTER BAR:                         │  Synchronized Map            │
│  [Status▼] [Severity▼] [Date▼]       │  (same filters as table)     │
│  [Crew▼]  [Search input]             │                              │
│                                      │                              │
│  INCIDENT TABLE (sortable):          │                              │
│  Priority | Severity | Location |    │  Severity-coded markers      │
│  Reporter | Age | Status | Assigned  │  Route overlay (if active)   │
│  Actions                             │                              │
│                                      │                              │
│  [Checkbox rows for bulk select]     │                              │
│                                      │                              │
│  BULK ACTION BAR (appears on select):│                              │
│  [Generate Route] [Assign All]       │                              │
│  [Change Status]                     │                              │
├──────────────────────────────────────┴──────────────────────────────┤
│  DETAIL DRAWER (slides from right, 480px, overlays map panel)       │
│  [Before Image] [After Image (if cleaned)]                          │
│  [Full metadata] [Status history timeline]                          │
│  [Assign dropdown] [Priority override] [Status change buttons]      │
└────────────────────────────────────────────────────────────────────┘
```

#### UI Components

| Component | Position | Purpose |
|---|---|---|
| **AdminStatsBar** | Top of content area | At-a-glance KPIs (active, in-progress, verified) |
| **FilterBar** | Above table | Multi-filter: status, severity, date range, crew, search |
| **IncidentTable** | Left panel | Sortable, paginated incident list; row = one incident |
| **SeverityBadge** | Table column | Color-coded pill: High/Medium/Low/None |
| **StatusPill** | Table column | Color-coded: Pending/Assigned/InProgress/Cleaned/Verified/NeedsReview |
| **PriorityScore** | Table column | Numeric 0-100 with color gradient; sortable |
| **BulkActionBar** | Below table, conditional | Appears when ≥1 row checked; "Generate Route", "Assign All", "Change Status" |
| **AdminMapPanel** | Right panel | Synchronized Leaflet map; responds to table filters |
| **DetailDrawer** | Right overlay (480px) | Slide-in on row click; full incident detail + actions |
| **AssignDropdown** | Inside drawer | Crew member list with workload count badges |
| **BeforeAfterViewer** | Inside drawer | Side-by-side image comparison; arrow to toggle |
| **StatusTimeline** | Inside drawer | Chronological status history with timestamps |
| **PriorityOverride** | Inside drawer | Admin can manually set priority score 0-100 |

#### User Interactions

| Interaction | Behavior |
|---|---|
| **Click table row** | DetailDrawer slides in from right; map highlights corresponding marker |
| **Click map marker** | Selects corresponding table row; DetailDrawer opens |
| **Check table row checkbox** | Row selected; BulkActionBar appears with count |
| **Sort table column** | Client-side sort on current page data; indicators show sort direction |
| **Change filter** | API re-fetched with new filter params; map updates to match |
| **Select crew in AssignDropdown + Assign** | PATCH `/api/incidents/:id/assign`; status changes to "Assigned"; marker updates color on map |
| **Click "Generate Route" (bulk)** | POST `/api/routes` with selected incident IDs; navigates to `/route/:id` |
| **Click "Priority Override"** | Inline number input; PATCH on blur |
| **Click status buttons in drawer** | PATCH `/api/incidents/:id/status`; immediate optimistic UI update |

#### Backend Integration

**Load incidents list:**
```
GET /api/incidents?status={filter}&severity={filter}&assignedTo={filter}&dateFrom={filter}&dateTo={filter}&sort={field}&order={asc|desc}&page={n}&limit=20
→ Response: {
    incidents: [{ id, imageUrl, lat, lng, severity, status, priorityScore, reporterName, createdAt, assignedTo, age }],
    total: int,
    page: int
  }
```

**Load admin stats:**
```
GET /api/incidents/stats
→ Response: { active: int, inProgress: int, verifiedToday: int, pendingAssignment: int }
```

**Assign incident:**
```
PATCH /api/incidents/:id/assign
Body: { assignedTo: userId }
→ Response: { id, status: "Assigned", assignedTo: { id, name, currentWorkload } }
→ State: update incident in table; update map marker color
```

**Bulk generate route:**
```
POST /api/routes
Body: { incidentIds: [uuid], depotLat?: float, depotLng?: float, assignedTo?: userId }
→ Response: { routeId: uuid, orderedStops: [...], polylineGeoJson: {...}, distanceKm: float, durationMin: int, isApproximate: boolean }
→ Navigate: /route/:routeId
```

**Change status (admin override):**
```
PATCH /api/incidents/:id/status
Body: { status: "Pending"|"Assigned"|"InProgress"|"Cleaned"|"Verified"|"NeedsReview" }
→ Response: { id, status, updatedAt }
```

#### Data Binding
- `incidents[]`: paginated, from API; re-fetched on filter change
- `stats{}`: from `/api/incidents/stats`, polled every 30s
- `selectedIncidentIds[]`: local checkbox state
- `openDrawerIncidentId`: local state driving drawer visibility

#### States
- **Loading:** Table skeleton (5 ghost rows); map shows spinner
- **Empty (filtered):** Table shows "No incidents match your filters" with "Clear filters" link
- **Empty (no incidents at all):** Illustration + "No incidents reported yet"
- **Error:** Toast "Failed to load incidents. Retrying..." with manual retry
- **Drawer open:** Right map panel slightly dimmed; drawer overlays it
- **Bulk selected:** BulkActionBar rises from bottom with slide-up animation

#### Auth Guard
- Route `/admin` requires JWT with `role: "admin"`
- Middleware check: if not authenticated → redirect to `/login?redirect=/admin`
- If authenticated but not admin → redirect to `/` with toast "Access denied"

---

### 🔹 Screen 4: Route View (`/route/:id`)

#### Layout Structure
```
┌──────────────────────────────────────────────────────────────┐
│  HEADER                                                       │
│  [← Back to Dashboard] [Optimized Route] [Share Link]         │
├───────────────────────────────────────┬───────────────────────┤
│  FULL MAP (65% width)                 │  STOP LIST PANEL      │
│                                       │  (35% width, scroll)  │
│  Route polyline (blue/teal)           │                       │
│  Numbered stop markers (①②③...)       │  Total: 12.4km        │
│  Depot marker (special icon)          │  Est: 45 min          │
│                                       │  [Approximate badge?] │
│  Clicking stop → highlight panel row  │                       │
│                                       │  ① Riverside Park     │
│                                       │    🔴 HIGH · 2.1km    │
│                                       │    123 River Rd       │
│                                       │                       │
│                                       │  ② West Flint St      │
│                                       │    🟠 MEDIUM · 0.8km  │
│                                       │                       │
│  [Start Navigation] (bottom-right)    │  [Start Navigation]   │
└───────────────────────────────────────┴───────────────────────┘
```

#### UI Components

| Component | Position | Purpose |
|---|---|---|
| **RouteMapContainer** | Left panel, 65% | Leaflet map with polyline and numbered stops |
| **RoutPolyline** | Map overlay | Teal `#2E86DE` polyline connecting all stops |
| **NumberedStopMarker** | Map overlay | Circular markers with stop number (①, ②...) |
| **DepotMarker** | Map overlay | Special "home base" icon at depot location |
| **StopListPanel** | Right panel | Ordered, scrollable list of stops |
| **StopCard** | List item | Per-stop: number, address, severity badge, distance from prev stop |
| **RouteMetaBar** | Top of right panel | Total distance (km), estimated duration (min), "Approximate" warning badge |
| **ApproximateBadge** | Conditional | Amber warning when fallback algorithm was used |
| **StartNavigationButton** | Bottom-right | Opens Google Maps / Apple Maps deep link with all waypoints |
| **ShareLinkButton** | Header right | Copies `/route/:id` URL to clipboard |

#### User Interactions

| Interaction | Behavior |
|---|---|
| **Click stop on map** | Scrolls stop list panel to highlight corresponding StopCard |
| **Click StopCard** | Map pans/zooms to stop marker; marker pulses |
| **Click "Start Navigation"** | Constructs Google Maps URL: `https://maps.google.com/maps/dir/?api=1&waypoints=lat,lng|lat,lng...` and opens in new tab |
| **Click "Share Link"** | Copies URL to clipboard; "Copied!" toast appears |

#### Backend Integration

**Load route:**
```
GET /api/routes/:id
→ Response: {
    id: uuid,
    assignedTo: { id, name },
    orderedStops: [{ incidentId, lat, lng, address, severity, distanceFromPrevKm }],
    polylineGeoJson: { type: "LineString", coordinates: [[lng,lat],...] },
    totalDistanceKm: float,
    estimatedDurationMin: int,
    isApproximate: boolean,
    status: "Active"|"Completed"|"Archived",
    createdAt: timestamp
  }
```

**Mark stop complete (crew):**
```
PATCH /api/incidents/:id/status
Body: { status: "InProgress" }
→ State: StopCard shows "In Progress" pill; marker dims on map
```

#### States
- **Loading:** Map skeleton; stop list skeleton (3-5 ghost cards)
- **Approximate route:** ApproximateBadge shown with tooltip "Optimized routing API unavailable. Route computed using nearest-neighbor algorithm."
- **Route completed:** All stops grayed out; completion banner at top of panel
- **Error loading route:** "Route not found" page with link back to dashboard

---

### 🔹 Screen 5: Cleanup Verification (`/task/:id`)

#### Layout Structure
```
┌──────────────────────────────────────────┐
│  HEADER (mobile-first)                   │
│  [← My Tasks]  Task #1234               │
├──────────────────────────────────────────┤
│  BEFORE IMAGE (full width, 240px height) │
│  📍 123 Riverside Park                   │
│  🔴 HIGH severity                        │
│                                          │
│  Status Timeline:                        │
│  [Assigned] → [In Progress] → [Cleaned]  │
│                                          │
│  ─────────────────────────────────       │
│  AFTER PHOTO UPLOAD                      │
│  [Upload "After" Photo] (required)       │
│  [Image preview when selected]           │
│                                          │
│  [Mark as Cleaned] (disabled until photo)│
└──────────────────────────────────────────┘

Post-verification:
┌──────────────────────────────────────────┐
│  BEFORE        │        AFTER            │
│  [Photo]       │        [Photo]          │
│                                          │
│  ✅ Verified Clean  OR  ⚠️ Needs Review  │
│  +25 pts (if verified)                   │
└──────────────────────────────────────────┘
```

#### UI Components

| Component | Position | Purpose |
|---|---|---|
| **TaskHeader** | Top | Task title, location, back link |
| **BeforeImage** | Full width | Before-photo from original report |
| **IncidentMeta** | Below image | Address, severity badge, report timestamp |
| **StatusTimeline** | Mid-section | Horizontal progress: Assigned → InProgress → Cleaned → Verified |
| **AfterPhotoUpload** | Lower section | Image upload zone for after-photo |
| **MarkAsCleanedButton** | Bottom | Disabled until after-photo selected; triggers AI verification |
| **VerificationResultCard** | Post-submit | Shows before/after side-by-side + verification status |
| **PointsAwardBanner** | Post-verify (success) | "+25 points awarded!" with badge level progress |

#### Backend Integration

**Load task:**
```
GET /api/incidents/:id
→ Response: { id, imageUrl, afterImageUrl, lat, lng, address, severity, status, note, createdAt, assignedTo, statusHistory: [{ status, timestamp, actor }] }
```

**Start cleanup:**
```
PATCH /api/incidents/:id/status
Body: { status: "InProgress" }
→ Response: { id, status: "InProgress", updatedAt }
```

**Submit after-photo and verify:**
```
POST /api/incidents/:id/verify
Content-Type: multipart/form-data
Body: { afterImage: File }
→ Immediate: 202 Accepted with { verificationId }
→ Poll GET /api/incidents/:id/verification or SSE stream
→ Final: {
    status: "Verified" | "NeedsReview",
    wasteDetected: boolean,
    confidence: float,
    afterImageUrl: string,
    pointsAwarded: int | null
  }
```

#### States
- **Loading:** Skeleton for image and metadata
- **Task assigned (not started):** "Start Cleanup" button prominent; after-upload hidden
- **In progress:** After-photo upload revealed; "Mark as Cleaned" disabled until photo selected
- **Verifying:** Loader overlay "Verifying cleanup..."
- **Verified Clean:** ✅ green checkmark; before/after side-by-side; "+25 pts" banner
- **Needs Review:** ⚠️ amber warning; "Admin has been notified"; before/after shown; no points
- **AI service down:** "Verification pending — admin will review manually" with "Pending Verification" status

---

### 🔹 Screen 6: Leaderboard (`/leaderboard`)

#### Layout Structure
```
┌──────────────────────────────────────────┐
│  HEADER                                  │
├──────────────────────────────────────────┤
│  🏆 Community Leaderboard                │
│  [This Week ▼]   [All Time ▼]           │
│                                          │
│  ┌─────────────────────────────────────┐ │
│  │ # │ Avatar │ Name │ Badge │ Points  │ │
│  ├───┼────────┼──────┼───────┼─────────┤ │
│  │ 1 │  [LS]  │Lucas │ Hero  │ 1,240   │ │
│  │ 2 │  [SM]  │Sofia │ Guard │  890    │ │
│  │ 3 │  [SM]  │Suara │ Guard │  745    │ │
│  │ ...                                  │ │
│  └─────────────────────────────────────┘ │
│                                          │
│  ── Your rank: #47 (320 pts) ──          │
│  (shown only when logged in)             │
└──────────────────────────────────────────┘
```

#### UI Components

| Component | Purpose |
|---|---|
| **LeaderboardTitle** | Page heading with period selector |
| **PeriodToggle** | "This Week" / "All Time" toggle; re-fetches data |
| **LeaderboardTable** | Top-20 ranked users |
| **UserRankRow** | Rank #, avatar (initials-based), name, badge icon, points |
| **BadgeTierIcon** | Bronze/Silver/Gold icon based on tier |
| **CurrentUserRankBanner** | Sticky at bottom; shows logged-in user's rank even if outside top-20 |

#### Backend Integration
```
GET /api/leaderboard?period=alltime|week&limit=20
→ Response: { users: [{ rank, displayName, totalPoints, badgeTier, reportCount }], currentUser?: { rank, totalPoints, badgeTier } }
→ No auth required; currentUser present only if JWT provided in request
```

#### States
- **Loading:** Skeleton rows (5 ghost entries)
- **Empty:** "No reports submitted yet. Be the first!"
- **Not logged in:** Table shows normally; "Your rank" banner shows "Log in to see your rank"

---

### 🔹 Screen 7: Profile / Login (`/profile`, `/login`)

#### Login Layout
```
┌──────────────────────────────┐
│  CleanGrid                   │
│                              │
│  Welcome back                │
│  [Email input]               │
│  [Password input]            │
│  [Log In button]             │
│  [Register link]             │
└──────────────────────────────┘
```

#### Profile Layout
```
┌───────────────────────────────────────────────────────┐
│  [Avatar large] Alex Johnson  ⚡ Points: 1,000         │
│  Level: 12.50   🎖 Bio-Factor                          │
│  ★★★★☆  [Progress bar to next badge]                  │
│                                                       │
│  BADGES ROW: [🏅][🏅][🏅][🏅][🏅]                    │
│                                                       │
│  LEADERBOARD RANK CARD                                │
│                                                       │
│  HOTSPOT AREAS (user's most active zones)            │
│                                                       │
│  MY REPORTS (list with status pills)                  │
└───────────────────────────────────────────────────────┘
```

#### Backend Integration

**Login:**
```
POST /api/auth/login
Body: { email, password }
→ Response: { accessToken, refreshToken, user: { id, displayName, role, totalPoints, badgeTier } }
→ State: set auth context; store tokens in httpOnly cookies (or localStorage as fallback)
```

**Register:**
```
POST /api/auth/register
Body: { email, password, displayName }
→ Response: { accessToken, user: {...} }
```

**Get profile:**
```
GET /api/users/me
Auth: Bearer token
→ Response: { id, displayName, email, role, totalPoints, badgeTier, reportCount, verifiedCleanups, recentReports: [...] }
```

---

### 🔹 Screen 8: Analytics / Hotspot (`/analytics`)

#### Layout Structure
```
┌────────────────────────────────────────────────────────────────────┐
│  HEADER + Admin Navigation tabs                                     │
│  [Dashboard | Reports | Map | Assigned | Flagged ▼ | 🔔 | 👤 | ≡]  │
├────────────────────────────────────────────────────────────────────┤
│  Analytics Overview                        [Start Task button]      │
│                                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐   │
│  │ 86 Reports   │ │ 23 Illegal   │ │ 45% Cleanups/Week         │   │
│  │ This Week    │ │ Dumping Hot  │ │ [Bar chart mini]           │   │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘   │
│                                                                     │
│  Hotspot Areas [list]:                                              │
│  1. Remote Pinning       [→]                                        │
│  2. Top File Parent...   [→]                                        │
│  3. Not Only Four Area   [→]                                        │
│                                                                     │
│  [Hotspot Map overlay — color gradient cells]                       │
└────────────────────────────────────────────────────────────────────┘
```

#### UI Components

| Component | Purpose |
|---|---|
| **StatsCards** | 3-up KPI cards: reports this week, hotspot count, cleanup rate |
| **HotspotZoneList** | Ranked list of hotspot zones with zone name, count, trend arrow |
| **HotspotMapMini** | Mini leaflet map with heat overlay; click zone → zoom in |
| **TrendChart** | Bar/line chart showing reports over past 30 days (recharts) |
| **ExportButton** | Downloads CSV of analytics data |

#### Backend Integration
```
GET /api/analytics?range=30d
→ Response: { reportsByDay: [{date, count}], hotspotZones: [{id, name, count, trend}], cleanupRate: float, weeklyReports: int }
```

---

### 🔹 Screen 9: Error / Empty States

#### 404 Page
```
┌─────────────────────────────┐
│  📱 Error 404               │
│                             │
│  Opps? Page and found.      │
│  This page you itha Making  │
│  for Doesn't exist.         │
│                             │
│  [Go Back to Home]          │
└─────────────────────────────┘
```

#### No Reports Found (inline)
```
┌─────────────────────────────┐
│  🗑 (illustration)          │
│                             │
│  No Reports Found           │
│  No incidents to display.   │
│  Everything our class here! │
│                             │
│  [Get for Go to Home]       │
└─────────────────────────────┘
```

#### Error State Components
| State | Component | Message | Action |
|---|---|---|---|
| 404 | `ErrorPage404` | "This page doesn't exist" | "Go Back to Home" button → `/` |
| No incidents | `EmptyIncidentState` | "No incidents to display" | "Report Waste" CTA |
| AI failure | `AIFailureBanner` | "AI analysis pending. Admin will review." | Dismiss; no retry needed |
| Network error | `NetworkErrorToast` | "Connection lost. Retrying..." | Auto-retry; manual retry link |
| Auth required | `AuthRequiredModal` | "Log in to earn points" | "Log In" button |
| Upload failed | `UploadErrorBanner` | "Upload failed after 3 attempts" | "Try again" retry button |

---

## 4. 🔄 User Flow Integration

### Flow 1: Citizen Waste Reporting

```
Start: User opens CleanGrid at /

Step 1: User sees map with existing incident markers
→ System: GET /api/incidents populates markers
→ State: markers rendered on map

Step 2: User clicks "Report Waste" FAB
→ Navigate: /report

Step 3: User drags or selects an image
→ Client: validates type and size
→ State: imageFile set; preview shown

Step 4: User clicks "Use My Location" OR drags pin on mini-map
→ GPS: navigator.geolocation.getCurrentPosition()
→ OR pin drag: updates lat/lng; GET /api/geocode/reverse
→ State: lat/lng set; address displayed

Step 5: User optionally types a note
→ State: note updated; counter shown

Step 6: User clicks "Submit Report"
→ Client: final validation (image + location)
→ POST /api/reports (multipart)
→ State: AnalysisLoader shown

Step 7: Backend processes (async)
→ Image saved to object storage
→ AI service called: POST /infer
→ Report record created with AI result
→ Priority score computed

Step 8: Client polls GET /api/reports/:id until status != "processing"
→ State: AIResultCard shown with severity, confidence, annotated image

Step 9a (waste detected): "+10 points" shown; map navigates to /
→ New marker appears at reported location
→ Leaderboard updated (async)

Step 9b (no waste): "No waste detected" shown; option to submit for manual review
→ If manual review: status = "Pending AI Review"; no points; marker appears

Step 9c (AI down): "Analysis pending" shown; report saved; admin notified
→ Marker appears as gray "AI Pending"

Outcome: Incident in DB; marker on map; points awarded (if applicable)
```

---

### Flow 2: Admin Triage and Assignment

```
Start: Admin navigates to /admin (authenticated with admin role)

Step 1: Dashboard loads
→ GET /api/incidents (default sort: priority score DESC)
→ GET /api/incidents/stats
→ State: table + stats cards populated; map markers synced

Step 2: Admin reviews high-priority incidents
→ Click table row
→ State: DetailDrawer slides in; map highlights marker

Step 3: Admin reviews incident detail
→ Views image, severity, confidence, age, reporter name
→ Reads status history timeline

Step 4: Admin selects crew from dropdown
→ GET /api/users?role=crew (populates dropdown with name + workload count)
→ Admin clicks "Assign Task"
→ PATCH /api/incidents/:id/assign { assignedTo: userId }
→ State: row status → "Assigned"; map marker color updates; drawer updates

Step 5 (optional): Admin bulk-selects multiple incidents
→ Checkboxes selected; BulkActionBar appears
→ Admin clicks "Generate Optimized Route"
→ POST /api/routes { incidentIds: [...] }
→ Navigate: /route/:routeId

Outcome: Incidents assigned; route generated; crew can now view tasks
```

---

### Flow 3: Crew Cleanup and Verification

```
Start: Crew member navigates to /task/:id (via route view or task list)

Step 1: Task loads
→ GET /api/incidents/:id
→ State: before-image, address, severity, status shown

Step 2: Crew clicks "Start Cleanup"
→ PATCH /api/incidents/:id/status { status: "InProgress" }
→ State: status timeline advances to "In Progress"

Step 3: Crew performs cleanup at location

Step 4: Crew clicks "Mark as Cleaned"
→ AfterPhotoUpload component revealed and required

Step 5: Crew selects after-photo
→ State: photo preview shown; "Mark as Cleaned" enabled

Step 6: Crew clicks "Mark as Cleaned"
→ POST /api/incidents/:id/verify { afterImage: File }
→ State: VerificationLoader shown

Step 7: AI processes after-photo
→ GET /infer called with after-image
→ If waste_detected = false: status → "Verified"; points → +25
→ If waste_detected = true: status → "Needs Review"; admin flagged

Step 8a (Verified):
→ ✅ "Verified Clean" shown; before/after side-by-side
→ "+25 points" banner shown to crew worker
→ "+5 points" awarded to original reporter (async)
→ Map marker grays out

Step 8b (Needs Review):
→ ⚠️ "Needs Review" shown; admin notified
→ No points awarded
→ Worker informed to clean again

Outcome: Incident verified; map updated; points distributed
```

---

### Flow 4: Admin Route Optimization

```
Start: Admin is on /admin dashboard

Step 1: Admin clicks "Plan Routes" or selects incidents via checkboxes

Step 2: Admin optionally inputs depot start address
→ Geocoded to lat/lng: GET /api/geocode/forward?q={address}

Step 3: Admin selects incidents (map click or checkbox)
→ State: selectedIncidentIds[] updated

Step 4: Admin clicks "Generate Route"
→ POST /api/routes { incidentIds: [...], depotLat?, depotLng?, assignedTo? }
→ System calls OpenRouteService API
→ If ORS fails: nearest-neighbor fallback activates; isApproximate = true
→ Route saved to DB

Step 5: Navigate to /route/:routeId
→ GET /api/routes/:id
→ Map renders polyline + numbered stops
→ Stop list panel shows ordered stops with distance/ETA

Step 6 (optional): Admin shares route
→ Click "Share Link" → URL copied to clipboard

Outcome: Route visible to crew; admins can share link directly
```

---

## 5. 🧠 Component System Design

### Core Reusable Components

#### `SeverityBadge`
```typescript
Props: {
  severity: "High" | "Medium" | "Low" | "None"
  size?: "sm" | "md" | "lg"
  showIcon?: boolean
}
Colors: { High: "#E84855", Medium: "#F9A03F", Low: "#4CAF50", None: "#9E9E9E" }
Variants: pill (default), dot-only, full-label
Reused in: MarkerPopup, IncidentTable, DetailDrawer, StopCard, TaskHeader
```

#### `StatusPill`
```typescript
Props: {
  status: "Pending"|"Assigned"|"InProgress"|"Cleaned"|"Verified"|"NeedsReview"
  size?: "sm" | "md"
}
Colors: {
  Pending: "#6B7280 bg-gray-100",
  Assigned: "#2E86DE bg-blue-50",
  InProgress: "#F9A03F bg-orange-50",
  Cleaned: "#4CAF50 bg-green-50",
  Verified: "#1A6B3C bg-emerald-50",
  NeedsReview: "#E84855 bg-red-50"
}
Reused in: IncidentTable, DetailDrawer, MarkerPopup, TaskHeader, Profile report list
```

#### `AppHeader`
```typescript
Props: {
  userRole?: "citizen" | "crew" | "admin"
  isAuthenticated: boolean
  currentPath: string
}
Behavior:
- Logo links to /
- "Admin" nav item hidden if role !== "admin"
- "Report Waste" always visible and high-contrast
- Mobile: hamburger menu with slide-in nav drawer
Reused in: All screens
```

#### `ImageUploadZone`
```typescript
Props: {
  onFileSelected: (file: File) => void
  maxSizeBytes?: number (default: 10MB)
  acceptedTypes?: string[] (default: ['image/jpeg', 'image/png', 'image/webp'])
  label?: string
}
Events: onFileSelected, onValidationError
States: idle, drag-over, file-selected (with preview), error
Reused in: Report Waste screen (before-photo), Task Verification screen (after-photo)
```

#### `MapContainer`
```typescript
Props: {
  incidents: Incident[]
  hotspotZones?: HotspotZone[]
  routePolyline?: GeoJSON.LineString
  onMarkerClick?: (incidentId: string) => void
  activeIncidentId?: string (for highlighting)
  showHeatmap?: boolean
  showHotspots?: boolean
  readOnly?: boolean
}
Reused in: Map Home, Admin Dashboard (right panel), Route View, Analytics (mini)
```

#### `DetailDrawer`
```typescript
Props: {
  incident: Incident | null
  isOpen: boolean
  onClose: () => void
  crewMembers: User[]
  onAssign: (incidentId, userId) => void
  onStatusChange: (incidentId, status) => void
  onPriorityOverride: (incidentId, score) => void
  userRole: "admin" | "crew" | "citizen"
}
Behavior: slides in from right on desktop; bottom-sheet on mobile
Reused in: Admin Dashboard, Map Home (read-only variant for citizen)
```

#### `LoadingSkeleton`
```typescript
Props: {
  variant: "table" | "card" | "map" | "image" | "text"
  rows?: number
}
Behavior: animated shimmer effect using CSS keyframes
Reused in: All screens with async data
```

#### `Toast`
```typescript
Props: {
  message: string
  type: "success" | "error" | "warning" | "info"
  duration?: number (default: 4000ms)
  action?: { label: string, onClick: () => void }
}
Position: bottom-right desktop, bottom-center mobile
Auto-dismiss after duration; manual close on X
Reused in: All screens for feedback
```

#### `PriorityScoreIndicator`
```typescript
Props: {
  score: number (0-100)
  showBar?: boolean
}
Color gradient: 0-33 green, 34-66 amber, 67-100 red
Reused in: IncidentTable, DetailDrawer
```

---

## 6. 🔗 Frontend ↔ Backend Contract

### API Endpoint Registry

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/login` | None | Login, get JWT |
| POST | `/api/auth/register` | None | Register new user |
| POST | `/api/auth/refresh` | Refresh token | Rotate access token |
| GET | `/api/users/me` | JWT | Get current user profile |
| GET | `/api/users?role=crew` | Admin JWT | List crew members for assignment |
| GET | `/api/incidents` | Optional JWT | List/filter incidents |
| POST | `/api/incidents` (multipart) | Optional JWT | Submit new incident report |
| GET | `/api/incidents/:id` | Optional JWT | Get single incident |
| PATCH | `/api/incidents/:id/assign` | Admin JWT | Assign incident to crew |
| PATCH | `/api/incidents/:id/status` | JWT (role-gated) | Update incident status |
| POST | `/api/incidents/:id/verify` (multipart) | Crew JWT | Upload after-photo + trigger AI verify |
| GET | `/api/incidents/stats` | Admin JWT | Get dashboard KPI stats |
| POST | `/api/routes` | Admin JWT | Generate optimized route |
| GET | `/api/routes/:id` | JWT | Get route detail |
| GET | `/api/leaderboard` | None | Get public leaderboard |
| GET | `/api/hotspots` | None | Get hotspot zones |
| GET | `/api/analytics` | Admin JWT | Get analytics data |
| GET | `/api/geocode/reverse` | None | Reverse geocode lat/lng |
| GET | `/api/geocode/forward` | None | Forward geocode address string |

### Core Data Schemas

**Incident (response):**
```json
{
  "id": "uuid",
  "reporterId": "uuid | null",
  "reporterName": "string | null",
  "assignedTo": { "id": "uuid", "name": "string" } | null,
  "imageUrl": "string (URL)",
  "afterImageUrl": "string (URL) | null",
  "annotatedImageUrl": "string (URL) | null",
  "lat": 26.1445,
  "lng": 91.7362,
  "addressText": "string | null",
  "note": "string | null",
  "wasteDetected": true,
  "confidence": 0.82,
  "severity": "High",
  "boundingBoxes": [{ "class": "bottle", "confidence": 0.82, "box": [x1,y1,x2,y2] }],
  "status": "Assigned",
  "priorityScore": 78.5,
  "isHotspot": true,
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T11:00:00Z",
  "statusHistory": [{ "status": "Pending", "timestamp": "...", "actor": "System" }],
  "possibleDuplicate": false
}
```

**Route (response):**
```json
{
  "id": "uuid",
  "createdBy": { "id": "uuid", "name": "string" },
  "assignedTo": { "id": "uuid", "name": "string" },
  "orderedStops": [
    { "incidentId": "uuid", "lat": 26.14, "lng": 91.73, "address": "string", "severity": "High", "distanceFromPrevKm": 2.1 }
  ],
  "polylineGeoJson": { "type": "LineString", "coordinates": [[lng, lat], ...] },
  "totalDistanceKm": 12.4,
  "estimatedDurationMin": 45,
  "isApproximate": false,
  "status": "Active",
  "createdAt": "2024-01-15T08:00:00Z"
}
```

### Validation Rules

**POST /api/incidents (multipart):**
```
image: required, MIME type in [image/jpeg, image/png, image/webp], size <= 10MB
lat: required, number, -90 <= lat <= 90
lng: required, number, -180 <= lng <= 180
note: optional, string, maxLength 200
```

**POST /api/routes:**
```
incidentIds: required, array of UUIDs, minLength 1, maxLength 50
depotLat: optional, number, -90 to 90
depotLng: optional, number, -180 to 180
assignedTo: optional, UUID of crew user
```

### Error Response Format (all endpoints)
```json
{
  "error": {
    "code": "VALIDATION_ERROR | AUTH_REQUIRED | FORBIDDEN | NOT_FOUND | AI_SERVICE_UNAVAILABLE | ROUTE_API_FAILED | INTERNAL_ERROR",
    "message": "Human-readable description",
    "fields": { "fieldName": "specific validation message" },
    "requestId": "uuid"
  }
}
```

### Authentication Handling
- Access token: JWT, 24h expiry, stored in `httpOnly` cookie (`access_token`) OR `localStorage` key `cg_access_token`
- Refresh token: 7-day expiry, `httpOnly` cookie (`refresh_token`)
- All authenticated requests include: `Authorization: Bearer {accessToken}`
- On 401 response: automatically call `POST /api/auth/refresh`; if refresh fails → redirect to `/login?redirect={currentPath}`
- Role checks: backend validates role on every protected endpoint; frontend hides role-specific UI based on auth context `userRole`

---

## 7. ⚙️ State Management Design

### Global State (React Context or Zustand store)

```typescript
AuthState: {
  isAuthenticated: boolean
  user: { id, displayName, role, totalPoints, badgeTier } | null
  accessToken: string | null
  login: (credentials) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

IncidentState: {
  incidents: Incident[]
  isLoading: boolean
  error: string | null
  filters: { status?, severity?, assignedTo?, dateFrom?, dateTo? }
  lastFetched: Date | null
  fetchIncidents: (filters?) => Promise<void>
  updateIncident: (id, patch) => void  // optimistic update
  addIncident: (incident) => void
}

MapState: {
  showHeatmap: boolean
  showHotspots: boolean
  hotspotZones: HotspotZone[]
  activeIncidentId: string | null
  toggleHeatmap: () => void
  toggleHotspots: () => void
  setActiveIncident: (id) => void
}

ToastState: {
  toasts: Toast[]
  addToast: (toast) => void
  removeToast: (id) => void
}
```

### Local State (per-screen)

| Screen | Local State |
|---|---|
| Report Waste | `imageFile`, `lat`, `lng`, `note`, `submitting`, `analysisResult` |
| Admin Dashboard | `selectedIncidentIds`, `openDrawerIncidentId`, `sortConfig`, `filterValues` |
| Route View | `highlightedStopIndex` |
| Task Verification | `afterImageFile`, `verifying`, `verificationResult` |

### State Transitions

```
INCIDENT STATE TRANSITIONS:
Pending → Assigned (admin assigns)
Assigned → InProgress (crew starts)
InProgress → Cleaned (crew marks done + after photo)
Cleaned → Verified (AI confirms no waste)
Cleaned → NeedsReview (AI detects remaining waste)
NeedsReview → Assigned (admin re-assigns)
Any → Any (admin manual override)
```

### Sync With Backend
- `incidents[]`: polled every 30s via `setInterval`; OR via WebSocket event `incident.updated`
- On PATCH operations: optimistic update applied immediately; rolled back on API error
- `leaderboard`: fetched on page load; no auto-refresh (click "Refresh" to reload)
- `hotspotZones`: fetched once on first toggle; cached in MapState until session ends

---

## 8. 🎯 UX Logic & Behavior

### Navigation Logic
- **Map Home** is the default route (`/`). Every screen has a path back to home.
- **Admin Dashboard** auto-redirects non-admin users to `/` with a toast.
- **`/report`** is accessible to all users (including unauthenticated); points require login.
- **Drawers** are always dismissed by clicking outside or pressing `Escape`.
- **Mobile bottom nav** (if implemented): icons for Map, Report, Leaderboard, Profile.
- **Back navigation**: uses `router.back()` where possible; explicit back links on task screens.
- **Post-submission redirect**: after report submission, "View on Map" navigates to `/` and highlights new marker.

### Feedback Mechanisms
| Trigger | Feedback |
|---|---|
| Successful report submission | Green toast "Report submitted!" + "+10 pts" banner on AIResultCard |
| Incident assigned | Table row updates status pill immediately (optimistic) |
| Route generated | Navigate to route view; polyline appears within 2s |
| Cleanup verified | Full-screen success state with before/after |
| Points awarded | Animated "+N pts" counter in banner |
| API error | Red toast with error type + retry action |
| Form validation error | Inline red text below offending field; field border turns red |
| File too large | Inline error before upload completes |
| Copied to clipboard | "Copied!" toast (2s auto-dismiss) |

### Accessibility Considerations
- All interactive map markers have `tabIndex={0}` and `aria-label="Severity level: High, Status: Pending, Click to view details"`
- Severity color badges include text label (not color-only); `aria-label` on color-only elements
- All form inputs have associated `<label>` or `aria-label`
- Drawers: focus trapped while open; focus returns to trigger element on close; `role="dialog"` with `aria-modal="true"`
- Toast notifications: `role="alert"` and `aria-live="polite"` for non-critical; `aria-live="assertive"` for errors
- Keyboard navigation: all interactive elements reachable via Tab; map markers navigable via arrow keys
- Color contrast: all text meets WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text)
- `prefers-reduced-motion`: skeleton shimmer and slide animations disabled if user preference set

### Performance Considerations
- **Map markers**: use `Leaflet.markercluster` for >10 visible markers; render as SVG not DOM elements
- **Heatmap layer**: computed from `incidents[]` already in state; no extra API call
- **Image lazy loading**: `loading="lazy"` on all images not above the fold
- **Table pagination**: server-side, 20 rows per page; do not load all incidents at once
- **Admin map panel**: debounced 300ms update on filter change; map re-render batched
- **Detail drawer**: data already in `incidents[]` state; no extra fetch needed for most fields
- **Code splitting**: admin dashboard, analytics, and route view are lazy-loaded chunks
- **Image storage**: use signed CDN URLs (Cloudflare R2 / S3); images never served directly from backend API

---

## 9. 🔒 Edge Cases & Error Handling

| Scenario | Client Behavior | Backend Behavior |
|---|---|---|
| Image > 10MB | Inline error before upload; "File exceeds 10MB limit" | 400 with VALIDATION_ERROR |
| Wrong file type | Inline error; file rejected from input | 400 with VALIDATION_ERROR |
| No GPS permission | Map picker shown as default; clear instruction "Drop a pin to continue" | N/A |
| AI service down | AnalysisLoader times out → "Analysis pending — your report was saved" banner | 202 with status "Pending AI Review"; admin dashboard shows warning banner |
| AI detects no waste | "No waste detected" result card; option to submit for manual review | Incident created with severity=None, wasteDetected=false |
| Same location twice (<20m, <10min) | No client-side check | Backend sets possibleDuplicate=true; admin dashboard shows "Possible Duplicate" badge on row |
| ORS API rate-limited | Route loads with ApproximateBadge | Backend activates nearest-neighbor fallback; isApproximate=true saved |
| ORS API completely down | Route loads with ApproximateBadge + tooltip | Same fallback |
| >25 waypoints for route | Warning toast "Large route — splitting into sub-routes" | Backend splits by geographic cluster; returns multiple route IDs |
| Crew marks clean without after-photo | Button disabled; "After photo required" validation message | 400 if somehow reached without photo |
| After-photo fails verification | "Needs Review" state; no points; "An admin has been notified" | status=NeedsReview; admin notification event |
| Network drop during report upload | Retry up to 3x with exponential backoff (1s, 2s, 4s) | Idempotency key in header prevents duplicate reports |
| JWT expired mid-session | Silent token refresh attempt; if fails → redirect to login with toast "Session expired" | 401 response triggers client refresh flow |
| Admin deletes incident in active route | N/A (delete not in MVP scope) | Route flagged as "Outdated"; crew notified via status message |
| >500 incidents on map | Clustering handles visual density; API viewport-bounds filtering reduces payload | `GET /api/incidents?bbox={w,s,e,n}` filters by viewport |
| Anonymous user earns points | No points awarded; post-submit CTA: "Create an account to earn points for your report!" | Points not written; report still saved |
| User submits duplicate image hash | Client: no check | Backend: flags as possibleDuplicate; holds for admin review; 409 or 200 with flag |

---

## 10. 📊 Design Consistency Rules

### Spacing System
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;

/* Component-specific */
--card-padding: var(--space-4) var(--space-5);
--section-gap: var(--space-8);
--page-margin: var(--space-6); /* mobile */
--page-margin-desktop: var(--space-8);
```

### Typography Hierarchy
```css
/* Font imports */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

--font-display: 'DM Sans', sans-serif;
--font-body: 'IBM Plex Sans', sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Scale */
--text-xs:   11px / 1.4  (labels, timestamps)
--text-sm:   13px / 1.5  (table cells, badges)
--text-base: 15px / 1.6  (body text)
--text-md:   17px / 1.5  (subheadings)
--text-lg:   20px / 1.4  (section headings)
--text-xl:   24px / 1.3  (page titles)
--text-2xl:  32px / 1.2  (hero headings)
--text-3xl:  40px / 1.1  (landing hero)
```

### Color Token Usage
```css
/* Only use tokens, never raw hex in components */
--color-brand: #1A6B3C;
--color-accent: #2E86DE;

--color-severity-high: #E84855;
--color-severity-medium: #F9A03F;
--color-severity-low: #4CAF50;
--color-severity-none: #9E9E9E;

--color-status-pending: #6B7280;
--color-status-assigned: #2E86DE;
--color-status-inprogress: #F9A03F;
--color-status-cleaned: #4CAF50;
--color-status-verified: #1A6B3C;
--color-status-needsreview: #E84855;

--color-bg: #F5F7FA;
--color-surface: #FFFFFF;
--color-border: #E5E7EB;
--color-text-primary: #1A1A2E;
--color-text-secondary: #6B7280;
--color-text-disabled: #9CA3AF;
```

### Component Consistency Rules
1. **All buttons** follow: Primary (brand fill), Secondary (outlined), Ghost (text-only), Danger (red fill). Never custom button styles.
2. **All cards** use `--card-padding`, `border-radius: 8px`, `box-shadow: var(--shadow-sm)`, `border: 1px solid var(--color-border)`.
3. **All inputs** use `height: 40px` (sm: 32px, lg: 48px), `border-radius: 4px`, focus ring `2px solid var(--color-accent)`.
4. **All badges/pills** use `border-radius: 999px`, `padding: 2px 8px`, `font-size: var(--text-xs)`, `font-weight: 600`.
5. **All drawers** open from right on desktop (`width: 480px`), from bottom on mobile (`max-height: 85vh`).
6. **All modals** (emergency only; prefer drawers) are centered, max-width 480px, with backdrop.
7. **All tables** use `border-collapse: separate; border-spacing: 0`, alternating row hover state `bg-gray-50`.
8. **Severity colors** are the single source of truth for all incident-related color-coding — never use brand green for severity.

### Interaction Patterns
- **Hover states:** All clickable elements have `cursor: pointer` and a `transition: all 150ms ease`
- **Focus states:** All focusable elements have a visible `outline: 2px solid var(--color-accent)` on focus
- **Active states:** Buttons have a pressed scale transform `scale(0.97)` with `transition: transform 100ms`
- **Loading buttons:** Spinner replaces label content; button becomes non-interactive; width preserved to prevent layout shift
- **Empty → populated transitions:** Data fades in with `animation: fadeIn 200ms ease`
- **Drawer transitions:** `transform: translateX(100%)` → `translateX(0)` with `transition: transform 250ms cubic-bezier(0.4,0,0.2,1)`

---

## 11. 🚀 Implementation Notes

### Priority Build Order

**Phase 0 — Foundation (build first, touch last)**
1. `AppHeader` component (used everywhere)
2. `AuthContext` and login/register flow
3. API client utility with token management and error handling
4. `Toast` notification system
5. `LoadingSkeleton` variants

**Phase 1 — Core Loop (MVP-critical)**
6. `MapContainer` + `SeverityMarker` + `MarkerClusterGroup`
7. Map Home screen (`/`)
8. `ImageUploadZone` component
9. Report Waste screen (`/report`) + API integration
10. `AIResultCard` component
11. Admin Dashboard (`/admin`) — table + map sync
12. `DetailDrawer` component
13. Task assignment API + optimistic UI

**Phase 2 — Route Optimization**
14. Route generation API + POST `/api/routes`
15. Route View screen (`/route/:id`) — polyline + stop list
16. `ApproximateBadge` + fallback UI

**Phase 3 — Verification + Gamification**
17. Cleanup Verification screen (`/task/:id`)
18. After-photo upload + AI verification API
19. `VerificationResultCard`
20. Leaderboard screen + API
21. Points award system + `PointsAwardBanner`

**Phase 4 — Polish + Analytics**
22. Analytics / Hotspot screen
23. `HotspotLayer` on map
24. Profile screen
25. All empty states and error states
26. `ErrorPage404`
27. WCAG accessibility audit pass

### Critical UI Paths (never break these)
1. `/` → click "Report Waste" → submit → see marker on map
2. `/admin` → click incident row → assign crew → generate route
3. `/route/:id` → view stops → start navigation
4. `/task/:id` → upload after-photo → see "Verified" result

### Risky Components (requires extra care)
| Component | Risk | Mitigation |
|---|---|---|
| `MapContainer` | Leaflet SSR incompatibility with Next.js | Dynamic import with `ssr: false` |
| `MarkerClusterGroup` | Performance with >200 markers | Cap viewport fetch; use GIST spatial index |
| `ImageUploadZone` | Mobile browser camera capture variance | Test on iOS Safari; use `accept="image/*" capture="environment"` attribute |
| `RoutPolyline` | GeoJSON coordinate order (lng/lat vs lat/lng) | Leaflet uses lat/lng; GeoJSON uses lng/lat — convert explicitly |
| `AIResultCard` (annotated image) | Bounding box rendering accuracy on different image aspect ratios | Render boxes as SVG overlay on image; scale to displayed image dimensions |
| `DetailDrawer` (mobile) | Bottom-sheet gesture handling on iOS | Use `overscroll-behavior: contain` and `touch-action: pan-y` |
| Polling (30s interval) | Memory leak if component unmounts | Always clear interval in `useEffect` cleanup |

### Simplifications for MVP
1. **Hotspot layer**: Use simple grid-cell frequency counting (not DBSCAN) — faster, demo-stable
2. **Real-time updates**: Use 30s polling (not WebSocket) for admin dashboard
3. **Image annotation**: Display bounding boxes as SVG overlays client-side from API-returned coordinates (do not render server-side)
4. **Route sharing**: Copy URL to clipboard (no email/SMS integration)
5. **Geocoding**: Reverse geocode on pin drag only; forward geocode depot address only — no full address autocomplete
6. **Crew notification**: No push notification; crew views assigned tasks on `/task/:id` or route view
7. **Admin user management**: Admins promote users to crew role via a simple role-change button in user list — no full user management UI required

### Seed Data Requirements (for demo stability)
- **5 users**: 1 admin (`admin@cleangrid.io`), 2 crew, 2 citizens
- **50 incidents**: Across 5 geographic clusters, mixed severities, mixed statuses
- **1 pre-generated route**: 5 stops, stored in DB, accessible at `/route/demo-route-id`
- **Leaderboard data**: Top 5 users with points for visual leaderboard
- **Hotspot zones**: 3 zones pre-computed from seeded incidents

---

*CleanGrid Design Specification v1.0*  
*Generated from PRD v1.0 + UI Mockup Analysis*  
*Ready for implementation by frontend, backend, and AI coding agents*

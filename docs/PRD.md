# PRD: CleanGrid — AI-Powered Smart Waste Management & Mapping System

**Document Version:** 1.0  
**Status:** Final  
**Prepared for:** Design, Engineering, and AI Execution Teams  
**Audience:** Developers, Designers, AI Coding Agents, Technical Judges, Stakeholders  

---

## 1. Overview

### Product Summary
CleanGrid is a web-first, AI-powered smart waste operations platform that enables municipalities, waste management teams, and citizen reporters to detect garbage using image analysis, visualize incidents on an interactive map, intelligently prioritize cleanup tasks, optimize collection routes, and verify cleanup completion — all in a single, cohesive system.

### Problem Being Solved
Waste collection is still primarily schedule-driven and reactive. Municipal teams lack real-time, unified visibility into where waste exists, how severe it is, and what the optimal cleanup sequence is. This leads to overflowing garbage, delayed responses, excessive fuel consumption from suboptimal routes, and poor accountability for cleanup outcomes.

### Why This Matters Now
Global waste volumes exceeded 2 billion tonnes in 2016 and continue to grow with urbanization. Legacy systems with fixed schedules and bin-level sensors fail to address litter outside bins, illegal dumping, and the variability of real-world waste accumulation. Cities that have adopted smarter systems have achieved up to 80% reduction in overflow incidents and 30–60% reduction in unnecessary collection trips. The technology stack needed to build a fully integrated solution — AI image inference, geospatial databases, route optimization APIs — is now mature, accessible, and deployable within hours.

### Core Value Proposition
CleanGrid turns waste from a blind, schedule-based process into a real-time, AI-guided cleanup network. It does not stop at detection. It closes the full operational loop: **waste reported → waste mapped → priority assessed → crew dispatched → cleanup verified → contributor rewarded**.

---

## 2. Problem Analysis

### Root Problem
Waste management systems lack a unified, real-time data layer. The core failure is that no single operational platform connects waste detection, spatial visualization, crew coordination, and outcome verification in one loop.

### Symptoms vs. Causes

| Symptom | Root Cause |
|---|---|
| Overflowing garbage bins | Fixed schedules ignore actual fill status and litter accumulation |
| Delayed cleanup response | No live reporting mechanism; manual complaints are slow |
| Wasted truck routes | Routes based on geography, not actual need distribution |
| Illegal dumping ignored | Bin-sensor systems are blind to waste outside containers |
| Poor accountability | No before/after verification of cleanup completion |
| No prioritization logic | All incidents treated equally regardless of severity, age, or location risk |
| Planners lack data | Historical waste patterns are not captured or analyzed |

### What the Problem Statement Is Really Asking For
The PS asks for a system that does three things at minimum: (1) detect garbage using AI from images, (2) map its location spatially, and (3) optimize the route for collection. However, the deeper ask — made explicit in the pre-PRD and research — is a **full-loop operational platform** that goes from detection to dispatch to verified cleanup. The PS implies all of this through its deliverables and optional features.

### Who Is Affected and How
- **City residents:** Experience dirty streets, health risks from decomposing waste, and flooding from clogged drains.
- **Sanitation crews:** Wasted trips to empty bins or unknown locations; no clear prioritization.
- **Waste management admins:** No live overview; cannot make intelligent dispatch decisions.
- **City planners:** No historical data on recurring problem areas; cannot allocate resources effectively.
- **Volunteer reporters:** No incentive or feedback mechanism after reporting; engagement is one-way.

### Why Existing Approaches Fail
- **Smart bins (IoT sensors):** Expensive hardware; only detect bin fill level, not surrounding litter or illegal dumping.
- **Static GIS route planners:** Useful for navigation but disconnected from live waste data or prioritization.
- **Manual complaint systems:** Inconsistent, slow, ignored, and not geospatially indexed.
- **Generic object detection demos:** Detect trash in images but do not connect to operations, routing, or crew workflows.

---

## 3. Product Vision

### Vision Statement
A world where no street stays dirty longer than it has to — because every waste incident is seen, mapped, prioritized, and acted on in real time.

### Mission Statement
Detect waste quickly, map it clearly, prioritize it intelligently, and route cleanup crews efficiently with a system that can scale from a hackathon demo to a municipal operations product.

### Product Principles
1. **Close the loop.** Every feature must contribute to the full cycle: detect → dispatch → verify.
2. **AI where it matters, determinism everywhere else.** Use AI for vision and prediction; keep routing, scoring, and auth rules deterministic.
3. **Operational over decorative.** Every screen must enable an action, not just inform.
4. **Demo-first, production-minded.** Build to impress in 5 minutes, but architect to survive in production.
5. **No orphaned features.** A feature that doesn't connect to the core loop doesn't ship in MVP.

### What Success Looks Like
A live system where a user uploads a garbage photo, the map immediately shows a new incident pin with a severity label, an admin assigns it, a route is generated through all pending incidents, a crew verifies cleanup with an after-photo, and a leaderboard updates — all without manual backend intervention.

---

## 4. Target Users

### Persona 1: Maya — Municipal Waste Admin
- **Goals:** Maintain clean streets, reduce complaints, keep routes efficient, and report performance metrics to leadership.
- **Pain Points:** No real-time overview of incidents; relies on phone calls or static reports; has no way to objectively prioritize tasks.
- **Behavior:** Spends time in dashboards, triages complaints manually, issues instructions verbally or via messaging tools.
- **Needs from CleanGrid:** A live incident dashboard with severity and age sorting, one-click task assignment, map overview of all active incidents, and route optimization output to share with crews.

### Persona 2: Carlos — Sanitation Crew Supervisor
- **Goals:** Get their team to the right places, in the right order, without backtracking.
- **Pain Points:** Fixed routes often cover areas that are already clean while missing real problem spots; updates come late.
- **Behavior:** Reviews his morning route list, dispatches teams, checks in by radio or phone.
- **Needs from CleanGrid:** Clear optimized route displayed on a map, ordered stop list with addresses, severity context per stop, and ability to mark tasks complete.

### Persona 3: Ravi — Sanitation Field Worker
- **Goals:** Complete assigned stops efficiently, document work done, avoid confusion about which jobs are his.
- **Pain Points:** Gets unclear instructions; no way to prove he cleaned a location; often assigned the same areas repeatedly out of habit.
- **Behavior:** Works from a printed list or a supervisor's call; uses phone for photos.
- **Needs from CleanGrid:** Simple task view on mobile, GPS-navigable route, and easy "mark cleaned + upload photo" action.

### Persona 4: Sofia — Citizen Reporter / Volunteer
- **Goals:** Report waste quickly when she sees it; contribute to cleaner neighborhoods; feel recognized for efforts.
- **Pain Points:** Existing systems are slow to respond; she doesn't know if her report was received or acted on.
- **Behavior:** Takes photos of waste with her phone; shares on social media; attends occasional community clean-ups.
- **Needs from CleanGrid:** Simple upload + auto-pin flow, real-time status on her report, points and recognition for verified cleanups.

### Persona 5: Dr. Priya — City Planner / Operations Analyst
- **Goals:** Understand recurring waste problem zones, justify resource allocation, improve long-term cleanliness strategies.
- **Pain Points:** No historical pattern data; cannot build evidence-based budgets or plans.
- **Behavior:** Works in spreadsheets and GIS tools; produces periodic reports.
- **Needs from CleanGrid:** Hotspot heatmap view, historical trend charts, severity over time, zone-level aggregation.

---

## 5. Goals and Non-Goals

### Goals
- Enable image-based waste detection with AI-generated severity scores.
- Spatially visualize all waste incidents on an interactive real-time map.
- Allow admins to triage, prioritize, and assign cleanup tasks from a dashboard.
- Generate optimized collection routes for a set of pending waste points.
- Provide before/after cleanup proof via image upload and verification.
- Support gamified user participation through points and a leaderboard.
- Predict recurring waste hotspots from historical report data.
- Deliver a complete, polished end-to-end demo with no manual backend steps.
- Architect the system to be production-extensible beyond the hackathon.

### Non-Goals
- Real-time IoT sensor integration (bin fill-level hardware) is not in scope for MVP.
- Native mobile app (iOS/Android) is not in scope; mobile-responsive web is sufficient.
- Drone or autonomous vehicle routing is not in scope.
- Blockchain-based proof of cleaning is not in scope.
- Full natural language processing of citizen text complaints is not in scope.
- Multi-city multi-tenant SaaS management portal is not in V1 scope.
- Integration with existing city ERP or dispatch systems is not in scope for MVP.
- Offline-first PWA capability is not required for MVP (online-only).
- CCTV or public camera feed integration is not in scope.

---

## 6. Key Insights from Research

### Research-Backed Opportunities
- Smart waste systems have demonstrated 30% cost reduction and up to 80% overflow reduction in deployed cities. This validates the problem and the business case.
- AI-based trash detection using YOLO-family models is proven, accessible via pre-trained weights, and fast to integrate — making it a reliable technical anchor.
- Route optimization APIs (OpenRouteService, GraphHopper) are production-grade and free-tier accessible, removing the need to build custom TSP solvers.
- Citizen engagement through gamification is largely untapped in existing waste management platforms — a clear differentiator.
- Hotspot prediction from historical data using clustering or simple ML (Random Forest, SVM) is academically proven and implementable within hackathon scope if core features are complete first.

### Competitor Gaps
- No currently available platform integrates all five of: AI image detection, geospatial mapping, operational task assignment, route optimization, and citizen verification into one workflow.
- Bigbelly, Nordsense, and similar smart bin companies focus on hardware-bound fill sensors — they do not address litter, illegal dumping, or citizen-driven reporting.
- General-purpose AI demos stop at "detection" without connecting to any operational workflow.

### Patterns Worth Using
- Severity scoring based on detected waste volume + confidence threshold is a reliable and actionable output from YOLO inference.
- Heatmap layers over base maps (using Leaflet.heat or Mapbox heatmap layers) are visually impactful with minimal complexity.
- Preloading demo data with seeded incidents and a pre-optimized route ensures demo stability without live API dependencies.
- Decoupling the AI inference service from the core backend API (separate microservice) is both technically sound and architecturally credible for demo purposes.

### Risks Discovered in Research
- Overreaching scope (adding prediction, gamification, and blockchain before core flow works) is the leading cause of hackathon failure.
- AI misclassification rates increase significantly on low-quality mobile images — confidence thresholding and a manual admin override path are required.
- Route optimization APIs may have rate limits on free tiers; fallback to a simplified nearest-neighbor algorithm must be available.
- Cleanup verification using image comparison is technically complex; the MVP approach should use the same detection model to confirm waste absence rather than true semantic comparison.

### Strategic Advantages
- The product's narrative — "from trash found to trash verified, in one platform" — is a story no competitor currently tells.
- The combination of AI, geospatial operations, and citizen engagement positions CleanGrid as a category-defining tool, not just a feature.
- The architecture is modular enough to onboard IoT feeds, mobile apps, or predictive models as post-hackathon extensions without refactoring.

---

## 7. Final Product Direction

### Chosen Solution
A web-first smart waste operations platform with the following core loop: AI-based image classification → geospatial mapping → admin prioritization and task assignment → route optimization → before/after cleanup verification → gamified reward.

### Why This Solution Was Selected Over Alternatives
- **Over "Drones + Blockchain":** That approach is technically infeasible in a 48-hour window and requires hardware the team doesn't have. The chosen approach delivers equivalent wow-factor through software alone.
- **Over "IoT-first platform":** IoT hardware integration requires physical deployment and vendor dependencies that cannot be demonstrated in a hackathon. The image-upload model is equivalent in concept but fully demonstrable.
- **Over "Pure ML data science":** A prediction-only tool has no operational workflow and cannot be demonstrated as a live product. Prediction is included as a layer, not the product.
- **Over "Simple YOLO demo":** A detection demo that stops at an image result has no operational value and no map, routing, or crew coordination. It would not win on impact, feasibility, or technical complexity.

### Core Differentiators
1. **Not just detection — connects detection to dispatch.**
2. **Not just maps — converts incidents into operational tasks.**
3. **Not just routing — prioritizes by severity and age.**
4. **Not just cleanup — verifies cleanup and rewards participation.**
5. **Not just a prototype — designed with production architecture.**

### What Makes It Better Than Competing Ideas
The product closes a loop that no competitor closes. The "before photo → AI detection → map pin → admin assignment → optimized route → after photo → verified cleanup → points awarded" narrative is complete, coherent, and demonstrable end-to-end in under 5 minutes.

---

## 8. Feature Set

### Must Have (MVP — Required for Demo)

#### Feature M1: Image Upload for Waste Reporting
- **Why it exists:** This is the primary input mechanism. Without it, the system has no data.
- **User value:** Allows anyone to report a waste incident from any device with a camera.
- **Behavior:** User navigates to the Report screen. They upload an image from their device or capture via camera (on supported browsers). They optionally drop a pin or allow GPS auto-detection. They submit. The image is sent to the AI inference service. A confirmation with the result is displayed.
- **Dependencies:** File storage (S3-compatible or local), AI inference endpoint, geolocation API or map picker.
- **Complexity:** Low-Medium.
- **Priority:** P0.

#### Feature M2: AI Waste Detection and Severity Classification
- **Why it exists:** Converts raw images into actionable signals without requiring manual assessment.
- **User value:** Immediately tells the reporter and admin how severe a waste incident is.
- **Behavior:** Uploaded image is sent to a YOLOv8-based inference endpoint. The model returns detected classes (garbage, litter, etc.), bounding boxes, and confidence scores. A severity label is computed: Low (confidence < 0.5 or small area), Medium (moderate confidence/area), High (high confidence, large area or multiple detections). If no waste is detected above threshold, return "No waste detected" and do not create an incident.
- **Dependencies:** YOLOv8 model (pre-trained on TACO dataset or equivalent), Python/FastAPI inference service, confidence threshold configuration (default: 0.45).
- **Complexity:** Medium.
- **Priority:** P0.

#### Feature M3: Map Visualization of Waste Incidents
- **Why it exists:** Spatial context is essential for coordination. A list of reports without a map is not actionable.
- **User value:** Gives admins and crews a live visual of where waste exists and how severe it is.
- **Behavior:** All confirmed reports with coordinates are rendered as map markers. Marker color indicates severity: green (low), orange (medium), red (high). Marker clicking opens a popup with image thumbnail, severity label, timestamp, and status. A heatmap toggle overlays density visualization. Clusters appear when zoomed out (markers merge into cluster bubbles with a count).
- **Dependencies:** Leaflet.js or Mapbox GL JS, backend reports endpoint with coordinates, Leaflet.markercluster and Leaflet.heat plugins.
- **Complexity:** Low-Medium.
- **Priority:** P0.

#### Feature M4: Admin Dashboard
- **Why it exists:** Admins need one view to monitor all incidents and make operational decisions.
- **User value:** Single source of truth for the waste management team.
- **Behavior:** Protected route requiring admin authentication. Shows a sortable table of all incidents with columns: ID, image thumbnail, location (address or coordinates), severity score, status (Pending / Assigned / In Progress / Cleaned / Verified), reporter name, timestamp, assigned crew. Admins can filter by status and severity, sort by age or severity, click to open a detail drawer, assign the incident to a crew member (dropdown), change priority, and bulk-select incidents for route generation.
- **Dependencies:** Auth system, backend task management API, crew user list.
- **Complexity:** Medium.
- **Priority:** P0.

#### Feature M5: Route Optimization for Collection Crews
- **Why it exists:** Manual route planning is inefficient. Crews need an ordered, optimized sequence of stops.
- **User value:** Reduces fuel cost, travel time, and cognitive load for crews.
- **Behavior:** Admin selects one or more pending incidents from the dashboard (or selects all within a zone). Clicks "Generate Route." System calls the routing optimization API (OpenRouteService) with the incident coordinates and an optional depot starting point. The API returns an ordered waypoint list and a polyline. The map renders the route as a colored path with numbered stop markers. The crew is shown an ordered stop list with ETA estimates. The route can be exported or shared via a link.
- **Fallback:** If the routing API is unavailable or rate-limited, a nearest-neighbor greedy algorithm runs client-side or server-side using the Haversine formula to compute approximate route ordering.
- **Dependencies:** OpenRouteService API (free tier) or GraphHopper, map polyline rendering, backend route storage.
- **Complexity:** Medium.
- **Priority:** P0.

#### Feature M6: Basic Status Tracking
- **Why it exists:** All stakeholders need to know where a report stands in its lifecycle.
- **User value:** Prevents duplicate reporting, allows crews to claim ownership, and gives reporters feedback.
- **Behavior:** Each report has a status field with the lifecycle: `Pending → Assigned → In Progress → Cleaned → Verified`. Status changes trigger map marker updates (grayed-out markers = cleaned). Admins can move any status manually. Crew members can update to In Progress and Cleaned. Reporters see the status of their own submissions.
- **Dependencies:** Report entity in database, status update API endpoints.
- **Complexity:** Low.
- **Priority:** P0.

---

### Should Have (V1 — Significantly Strengthens Product)

#### Feature S1: Before/After Cleanup Verification
- **Why it exists:** Without verification, "cleaned" is self-reported and unverifiable. This closes the accountability gap.
- **User value:** Builds trust with admins and municipalities; enables accurate reporting of cleanup completion.
- **Behavior:** When a crew member marks a task as Cleaned, they are prompted to upload an "after" photo. The after photo is sent to the same AI inference service. If the model detects no significant waste (below threshold or zero detections), the status auto-updates to "Verified Clean." If waste is still detected, the status becomes "Needs Review" and the admin is flagged. A before/after side-by-side view is available in the incident detail drawer.
- **Dependencies:** AI inference service reuse, image storage, status update API, admin notification.
- **Complexity:** Medium.
- **Priority:** P1.

#### Feature S2: Priority Scoring System
- **Why it exists:** All incidents are not equal. Age and severity should drive urgency.
- **User value:** Admins and routing algorithms can prioritize without manual judgment.
- **Behavior:** Each incident receives a computed Priority Score on a scale of 1–100 using the formula:
  `Priority = (Severity Weight × 40) + (Age Weight × 35) + (Hotspot Bonus × 25)`
  Where:
  - Severity Weight: Low = 0.3, Medium = 0.6, High = 1.0
  - Age Weight: scales linearly from 0 (just reported) to 1.0 (48+ hours old)
  - Hotspot Bonus: 0 (not in hotspot zone), 0.5 (moderate hotspot), 1.0 (high-frequency hotspot)
  Priority Score is recalculated every 30 minutes or on status change. The dashboard displays priority rank. Route generation defaults to prioritizing high-score stops first.
- **Dependencies:** Scoring service/function, hotspot data layer, cron job or on-demand recalculation.
- **Complexity:** Low-Medium.
- **Priority:** P1.

#### Feature S3: Gamification — Points and Leaderboard
- **Why it exists:** Citizen reporting sustains the data pipeline. Without incentive, participation drops off.
- **User value:** Motivates reporters and volunteers; creates community ownership of cleanliness.
- **Behavior:** Citizens earn points for: submitting a report (+10 pts if AI confirms waste), submitting a verified after-photo (+25 pts), having a report lead to completed cleanup (+5 pts bonus). A public leaderboard ranks users by total points with a badge tier system: Cleaner (0–100 pts), Guardian (101–300 pts), Hero (301+ pts). Badges display on user profiles. The leaderboard is visible to all users without login.
- **Dependencies:** User accounts/auth, points ledger table, leaderboard endpoint.
- **Complexity:** Low-Medium.
- **Priority:** P1.

---

### Nice to Have (V2 — Innovation Layer)

#### Feature N1: Garbage Hotspot Prediction
- **Why it exists:** Historical patterns allow proactive deployment instead of purely reactive response.
- **User value:** Planners can schedule preventive collections before overflow occurs.
- **Behavior:** Backend aggregates all historical reports by geospatial grid cell (0.01° lat/lon grid). Cells with 3+ reports in the past 30 days are flagged as hotspot zones. A K-means clustering or DBSCAN pass groups hotspot cells into zones. These zones are rendered as a heatmap overlay layer on the map (togglable). If time allows, a simple time-series analysis predicts recurrence probability per zone using weekly patterns.
- **Assumption:** Sufficient seed data (preloaded sample incidents) will be required at demo time to show meaningful hotspots. Seed data of 30–50 incidents across 5–7 zones will be included in the database initialization script.
- **Dependencies:** Historical reports DB, clustering logic (Python scikit-learn or simple cell-grid aggregation), visualization overlay.
- **Complexity:** Medium.
- **Priority:** P2.

#### Feature N2: Offline-Ready Report Submission (PWA)
- **Why it exists:** Field workers in low-connectivity areas still need to capture incidents.
- **User value:** Increases adoption in real operational settings.
- **Behavior:** Report form functions offline using service workers; queued submissions sync when connection is restored.
- **Dependencies:** PWA manifest, service worker, IndexedDB queue.
- **Complexity:** Medium.
- **Priority:** P3.

#### Feature N3: Real-Time Crew Location Tracking
- **Why it exists:** Supervisors benefit from knowing where crews are relative to assigned tasks.
- **User value:** Enables dynamic rerouting and better dispatch decisions.
- **Behavior:** Crew app publishes GPS location on task acceptance; admin map shows crew pins live.
- **Dependencies:** WebSocket connection, crew app enhancements.
- **Complexity:** Medium-High.
- **Priority:** P3.

---

## 9. Detailed User Flows

### Flow 1: Citizen Waste Reporting

**Trigger:** User sees garbage on the street and opens the CleanGrid app.

**Steps:**
1. User opens the web app; landing page shows the map with existing incident pins.
2. User clicks "Report Waste" button (prominent, top-right of map or sticky bottom button on mobile).
3. Report screen opens with two options: "Upload Photo" or "Take Photo."
4. User selects or captures an image (JPEG/PNG, max 10 MB).
5. Image preview appears. Location field auto-populates from browser geolocation (with permission) or user manually drops a pin on a mini-map.
6. Optional: user adds a text note (max 200 chars).
7. User clicks "Submit Report."
8. System shows a loading spinner with message "Analyzing waste..."
9. AI service processes image (target: < 5 seconds).
10. Result screen shows: detected severity label, confidence %, a bounding-box annotated version of the image, and a confirmation message.
11. Map updates with a new marker at the reported location.
12. User sees: "+10 points added to your profile" (if logged in and waste detected).
13. User is returned to the main map with their new pin visible.

**Edge Cases:**
- No GPS permission granted: display map picker for manual pin placement; do not block submission.
- Image too large (> 10 MB): show inline error "Please upload an image under 10 MB."
- AI detects no waste: show "No waste detected" with confidence %; ask user to retake photo or submit anyway (admin review route, no points awarded).
- Network timeout during submission: show error with retry button; do not lose image.

**Success:** Waste report is in database, map pin is visible, reporter gets confirmation.
**Failure:** AI service down → system falls back to "manual review pending" status, report is still saved.

---

### Flow 2: Admin Incident Triage and Task Assignment

**Trigger:** Admin logs in and reviews the dashboard.

**Steps:**
1. Admin navigates to `/admin` and authenticates.
2. Dashboard loads with a sortable table of all incidents (default sort: Priority Score descending).
3. Admin reviews the map panel (right half of screen) which mirrors table filters.
4. Admin clicks a high-severity, high-priority incident.
5. Detail drawer slides in from the right: shows full image, severity, AI confidence, GPS coordinates, reporter name, age, and current status.
6. Admin selects a crew member from the "Assign To" dropdown (shows crew name and current workload count).
7. Admin clicks "Assign Task." Status updates to "Assigned"; map marker changes color.
8. Admin can bulk-select multiple incidents and click "Generate Optimized Route" for a selected crew.
9. Optimized route appears as an overlay on the map with numbered stops.
10. Admin shares the route link with the crew supervisor.

**Edge Cases:**
- No crew members configured: system shows warning; admin must add at least one crew profile before assigning.
- Duplicate location (two reports within 20 meters of each other): system flags as "Possible Duplicate" and prompts admin to merge or keep both.
- Routing fails (API timeout): fallback nearest-neighbor route is computed client-side and flagged as "Approximate Route."

**Success:** Tasks assigned, route generated, crew notified.
**Failure:** If route API fails and fallback also fails, admin is shown an error with the raw ordered list of stops as plain text.

---

### Flow 3: Crew Cleanup and Verification

**Trigger:** Field worker receives task assignment and navigates to the site.

**Steps:**
1. Field worker opens the CleanGrid crew view (mobile-responsive web).
2. Sees their assigned tasks listed by route order with map pins.
3. Taps the first stop; detail view shows before-photo, address, severity label.
4. Worker taps "Start Cleanup" → status updates to "In Progress."
5. Worker performs the cleanup.
6. Worker taps "Mark as Cleaned" → prompted to upload "after" photo.
7. Worker captures or uploads after photo.
8. System sends after photo to AI service.
9. AI returns result: if waste below threshold → status becomes "Verified Clean," green checkmark shown.
10. If waste still detected → status becomes "Needs Review," flagged for admin.
11. Points are awarded to the original reporter (bonus) and the worker (+25 pts for verified cleanup).

**Edge Cases:**
- Worker marks cleaned without uploading after photo: system requires it; "after photo required" validation message.
- AI service unavailable during verification: status is set to "Pending Verification" with timestamp; admin manually reviews later.
- Worker uploads wrong photo (unrelated image): AI detects no waste → passes verification (acceptable false positive path; admin can flag on review).

**Success:** Incident marked verified; map marker grays out; points awarded; dashboard updates.
**Failure:** Verification stuck in "Needs Review" → admin manually resolves.

---

### Flow 4: Admin Route Optimization

**Trigger:** Admin wants to plan the day's collection runs.

**Steps:**
1. Admin opens the Admin Dashboard.
2. Admin clicks "Plan Routes" in the top navigation.
3. Route planning panel opens showing all Pending/Assigned incidents on the map.
4. Admin optionally inputs the crew depot/start address.
5. Admin selects incidents via map click or table checkbox, or clicks "Select All High Priority."
6. Admin clicks "Generate Route."
7. System calls OpenRouteService (or GraphHopper) with waypoints in priority-score order.
8. Route polyline is drawn on the map; ordered stop list is shown in the panel.
9. Admin sees estimated total distance and approximate time.
10. Admin can assign the route to a specific crew member/vehicle and share a link.

**Edge Cases:**
- More than 25 waypoints selected: system warns "Large routes may take longer to optimize" and splits into sub-routes by geographic cluster automatically.
- Routing API rate limit hit: fallback greedy algorithm activates; result is marked as "Approximate."
- Selected incidents span very large geographic area: system warns admin about route feasibility.

**Success:** Optimized route saved, shareable, rendered on map.
**Failure:** Routing fails entirely → show ordered list of stops with a message "Route visualization unavailable, use stop list."

---

## 10. Functional Requirements

### Report Submission
- **FR-01:** The system shall accept image uploads in JPEG, PNG, or WEBP format with a maximum file size of 10 MB.
- **FR-02:** If the uploaded file exceeds 10 MB or is not an accepted format, the system shall return an error message and not process the file.
- **FR-03:** The system shall accept location data as GPS coordinates (latitude/longitude) from the browser geolocation API or as a manually placed map pin.
- **FR-04:** Location must be provided (GPS or manual pin) before a report can be submitted. If location cannot be determined, the user must place a pin manually.
- **FR-05:** A submitted report with location and image shall be persisted in the database within 3 seconds of user action.
- **FR-06:** The system shall not create an incident record if the AI service returns "no waste detected" and the user does not override to manual review.

### AI Detection
- **FR-07:** The AI inference service shall process each uploaded image and return: waste_detected (boolean), confidence (float 0–1), severity_label (Low | Medium | High | None), bounding_boxes (array, optional for display).
- **FR-08:** Severity shall be computed as: High = confidence ≥ 0.7 OR 3+ detections; Medium = confidence 0.45–0.69 OR 2 detections; Low = confidence 0.25–0.44 OR 1 detection; None = below 0.25.
- **FR-09:** The default confidence detection threshold shall be 0.45, configurable via environment variable.
- **FR-10:** If the AI service is unavailable, the backend shall save the report with status "Pending AI Review" and notify admin via dashboard flag.
- **FR-11:** AI inference shall complete within 10 seconds; if it exceeds 10 seconds, the service shall timeout, return a partial result with confidence = null, and flag for manual review.

### Map Visualization
- **FR-12:** The map shall display all confirmed incidents as markers with color coding: red (High), orange (Medium), green (Low), gray (Cleaned/Verified).
- **FR-13:** Clicking a map marker shall open a popup with: image thumbnail, severity label, status, timestamp, and a "View Details" link.
- **FR-14:** The map shall support a heatmap toggle layer displaying incident density.
- **FR-15:** When more than 10 markers are visible in the viewport, markers shall cluster and display a count badge.
- **FR-16:** The map shall auto-fit its viewport to show all active incidents on initial load.

### Admin Dashboard
- **FR-17:** The admin dashboard shall be accessible only to authenticated users with the `admin` role.
- **FR-18:** The dashboard shall display all incidents in a table sortable by: severity (High→Low), age (oldest first), and priority score (High→Low).
- **FR-19:** Admins shall be able to filter incidents by status, severity, date range, and assigned crew.
- **FR-20:** Admins shall be able to assign an incident to a crew member by selecting from a dropdown of registered crew users.
- **FR-21:** Status changes made by admins shall immediately reflect in the map view and crew view without page refresh (via polling every 30 seconds or WebSocket).
- **FR-22:** Admins shall be able to bulk-select incidents and trigger route generation from the dashboard.

### Route Optimization
- **FR-23:** The route optimization feature shall accept a list of incident IDs and an optional depot location.
- **FR-24:** The system shall call the OpenRouteService Optimization API (or equivalent) with the waypoints and return an ordered stop list and a polyline GeoJSON.
- **FR-25:** If the external routing API fails or is unavailable, the system shall compute a nearest-neighbor greedy route using Haversine distance and mark the result as "Approximate."
- **FR-26:** The generated route shall be rendered as a colored polyline on the map with numbered stop markers.
- **FR-27:** The system shall display estimated total distance (km) and approximate duration for the generated route.
- **FR-28:** Generated routes shall be saved to the database linked to a crew member and a timestamp.

### Status and Verification
- **FR-29:** The incident lifecycle states shall be: `Pending → Assigned → In Progress → Cleaned → Verified | Needs Review`.
- **FR-30:** Transitioning to "Cleaned" state shall require an after-photo upload.
- **FR-31:** The after-photo shall be submitted to the AI inference service; if waste_detected = false below threshold, status transitions to "Verified." Otherwise, it transitions to "Needs Review."
- **FR-32:** Admins shall be able to manually override any status for any incident.

### Gamification
- **FR-33:** Authenticated users shall earn 10 points when a report they submitted results in a confirmed waste detection (AI confidence ≥ threshold).
- **FR-34:** Users who upload a verified after-photo shall earn 25 points.
- **FR-35:** The leaderboard shall display the top 20 users by total points and shall be publicly accessible without login.
- **FR-36:** Badge tiers shall be computed server-side and cached: Cleaner (0–100), Guardian (101–300), Hero (300+).

### Hotspot Prediction
- **FR-37:** The hotspot computation shall aggregate all `Verified` and `Cleaned` incidents from the past 90 days into a 0.001° lat/lon grid.
- **FR-38:** Grid cells with ≥ 3 historical incidents shall be classified as hotspot zones.
- **FR-39:** Hotspot zones shall be rendered as a heatmap overlay on the map, togglable independently of the live incident heatmap.
- **FR-40:** The hotspot layer shall be recomputed nightly via a scheduled job.

---

## 11. Non-Functional Requirements

### Performance
- **NFR-01:** Map initial load (with up to 500 markers) shall complete within 3 seconds on a standard 4G connection.
- **NFR-02:** AI inference shall return a result within 10 seconds for images up to 10 MB.
- **NFR-03:** API endpoints (excluding AI inference) shall respond within 500ms for 95th percentile of requests under normal load.
- **NFR-04:** Route optimization for up to 25 waypoints shall complete within 5 seconds.

### Scalability
- **NFR-05:** The backend API shall be stateless and horizontally scalable behind a load balancer.
- **NFR-06:** The database shall use PostGIS for geospatial queries, enabling indexed spatial searches without full table scans.
- **NFR-07:** The AI inference service shall be independently deployable and scalable as a separate container.

### Reliability
- **NFR-08:** The system shall achieve 99% uptime during the hackathon demo window.
- **NFR-09:** All critical flows (report submission, map load, dashboard) shall have graceful fallbacks in the event of AI service or routing API failure.
- **NFR-10:** No single point of failure shall block the end-to-end demo; the AI result can be mocked, and the route can be fallback-computed.

### Availability
- **NFR-11:** The web application shall be accessible from any modern browser (Chrome, Firefox, Safari, Edge) on desktop and mobile.
- **NFR-12:** No native app installation shall be required.

### Security
- **NFR-13:** Admin routes shall require JWT-based authentication.
- **NFR-14:** All API endpoints shall validate inputs and sanitize data to prevent SQL injection and XSS.
- **NFR-15:** Uploaded images shall be stored with non-guessable names (UUID-based filenames) to prevent enumeration.
- **NFR-16:** HTTPS shall be enforced in production.

### Privacy
- **NFR-17:** GPS coordinates shall only be stored with user consent (explicit geolocation permission or manual pin).
- **NFR-18:** Reporter identity shall not be publicly displayed on map popups; only visible to admins.
- **NFR-19:** No PII beyond email and display name shall be stored in the user record.

### Accessibility
- **NFR-20:** All interactive elements shall be keyboard-navigable.
- **NFR-21:** Color-coded severity markers shall include a text label or accessible tooltip to support color-blind users.
- **NFR-22:** The application shall meet WCAG 2.1 Level AA contrast requirements.
- **NFR-23:** Form inputs shall include ARIA labels.

### Maintainability
- **NFR-24:** All services shall be containerized via Docker.
- **NFR-25:** Environment configuration shall use `.env` files and not be hardcoded in source.
- **NFR-26:** API contracts shall be documented via OpenAPI 3.0 spec (auto-generated by FastAPI).

### Usability
- **NFR-27:** A first-time user should be able to submit a waste report in under 60 seconds without any instruction.
- **NFR-28:** The admin dashboard shall be fully usable on a 1280×800 desktop screen without horizontal scroll.

---

## 12. UX / UI Requirements

### Screens and Navigation

**Primary Navigation (Header):**
- Logo / App Name (CleanGrid)
- Map (default home)
- Report Waste (primary CTA button, always visible)
- Dashboard (admin only, hidden for non-admin)
- Leaderboard
- Login / Profile

---

**Screen 1: Map Home (/)**
- Full-viewport interactive map (Leaflet or Mapbox).
- Incident markers with severity-coded colors.
- Top-right controls: Heatmap Toggle, Hotspot Prediction Toggle, Zoom Controls.
- Floating "Report Waste" button (bottom-center on mobile, top-right on desktop).
- Clicking a marker opens a popup: thumbnail, severity badge, status pill, "View Details" link.
- Loading state: skeleton map with a spinner overlay.
- Empty state: map still shows with a banner "No active incidents. Be the first to report."

**Screen 2: Report Waste (/report)**
- Clean, single-column form.
- Step 1: Image upload (drag-and-drop zone on desktop; file picker on mobile). Image preview with remove button.
- Step 2: Location (toggle between "Use My Location" and "Pick on Map"). Mini-map with draggable pin.
- Step 3: Optional note (textarea, 200 char limit with counter).
- Submit button (disabled until image + location are both provided).
- Post-submit: Result card showing annotated image (bounding boxes), severity badge, confidence %, and points earned.
- Error state: inline field-level errors; toast for network failures.

**Screen 3: Admin Dashboard (/admin)**
- Two-panel layout (desktop): Left = sortable, filterable table; Right = synchronized map.
- Table columns: Priority Score (sortable), Severity (badge), Location, Reporter, Age, Status (pill), Assigned To, Actions.
- Row click: opens right-side detail drawer (not a new page).
- Detail drawer: before/after image pair, full metadata, status history, assign dropdown, priority override.
- Top bar: "Plan Routes" button, filter bar (status, severity, date range, crew).
- Bulk action bar: appears when rows are checked — "Generate Route," "Assign All," "Change Status."
- Map panel: mirrors table filters; clicking map pin selects the corresponding table row.

**Screen 4: Route View (/route/:id)**
- Full-width map with the optimized route polyline.
- Numbered stop markers in route order.
- Right panel: ordered stop list with distance, severity, and address per stop.
- "Start Navigation" button (links to Google Maps / Apple Maps with waypoints).
- Status: shows current stop progress if crew is using it.

**Screen 5: Leaderboard (/leaderboard)**
- Clean ranked list of top 20 users.
- User avatar (initials-based), display name, badge tier icon, total points.
- Logged-in user's own rank shown even if not in top 20.
- Publicly viewable; no login required.

**Screen 6: Profile / Login (/profile)**
- Simple login with email/password.
- Profile shows: total points, badge tier, list of submitted reports and their statuses.

---

### Layout Logic
- Map-centric design: map is the hero element on every screen that shows spatial data.
- Admin dashboard is the only screen with a split-panel layout.
- All modals are replaced with drawers to preserve spatial context.
- Mobile: single-column stacked layout; bottom-sheet replaces right drawers.

### Visual Priorities
1. Incident severity (immediately legible via color + label).
2. Current status (pill badge on every incident card).
3. The map (always present as background context on operational screens).
4. Call-to-action (Report Waste button is always visible and high-contrast).

### Responsiveness
- Breakpoints: Mobile (< 768px), Tablet (768–1024px), Desktop (> 1024px).
- The admin dashboard collapses to a full-width table on mobile with map accessible via a tab toggle.
- Map controls stack vertically on mobile.

### Loading / Empty / Error States
- All data-dependent components show skeleton loaders, not spinners alone.
- Empty states include an illustrative icon and a clear action prompt.
- API errors surface as a dismissable toast with error type and a retry action where applicable.
- AI processing shows an animated status card: "Analyzing image…" → "Waste detected" / "No waste found."

---

## 13. System / Technical Design

### High-Level Architecture

```
[Browser: React/Next.js]
       │
       ├──→ [CDN: Static Assets (Vercel / Cloudflare)]
       │
       └──→ [Backend API: FastAPI]
                  │
                  ├──→ [PostgreSQL + PostGIS Database]
                  │
                  ├──→ [AI Inference Service: FastAPI + YOLOv8]
                  │           │
                  │           └──→ [Object Storage: S3 / Cloudflare R2 / Local]
                  │
                  ├──→ [Route Optimization API: OpenRouteService (external)]
                  │
                  └──→ [Mapping API: Mapbox / Leaflet tiles (external)]
```

### Components

| Component | Role |
|---|---|
| **Frontend (Next.js)** | All user-facing screens, map rendering, report submission, admin dashboard |
| **Backend API (FastAPI)** | Core business logic, auth, CRUD, orchestration |
| **AI Service (FastAPI + YOLOv8)** | Image inference, severity computation, cleanup verification |
| **Database (PostgreSQL + PostGIS)** | All persistent data: users, incidents, routes, scores, hotspots |
| **Object Storage** | Image file storage (before/after photos) |
| **Route Optimization (ORS)** | External API for TSP/VRP-optimized route generation |
| **Map Tiles** | Leaflet.js with OpenStreetMap tiles (free) or Mapbox GL JS |

### Data Flow
1. User submits image + location via frontend.
2. Frontend sends a `multipart/form-data` POST to `/api/reports`.
3. Backend API saves image to object storage; writes a draft report record.
4. Backend API calls AI service (`POST /infer`) with the image URL.
5. AI service runs YOLOv8 inference; returns `{waste_detected, confidence, severity, boxes}`.
6. Backend API updates the report record with AI results; computes initial priority score.
7. Frontend receives the response and updates: (a) map marker, (b) result screen.
8. Admin opens dashboard → GET `/api/reports` with filters → table + map render.
9. Admin triggers route generation → POST `/api/routes` → backend calls ORS API → route saved + returned.
10. Crew updates status → PATCH `/api/reports/:id/status` → real-time update propagates.
11. After-photo uploaded → same AI inference call → verification result written.

### Recommended Tech Stack

| Layer | Technology | Justification |
|---|---|---|
| **Frontend** | Next.js 14 (React) | File-based routing, SSR/SSG, fast iteration, Vercel-native |
| **Map Library** | Leaflet.js + react-leaflet | Free, open-source, battle-tested, OSM tiles |
| **Map Tiles** | OpenStreetMap (default) | Free, no API key needed for hackathon |
| **Map Extras** | Leaflet.markercluster, Leaflet.heat | Clustering and heatmap without additional API |
| **Styling** | Tailwind CSS | Rapid styling, responsive utilities, no CSS files to manage |
| **Backend API** | Python + FastAPI | Fast to build, async support, auto-generates OpenAPI docs, AI ecosystem |
| **AI Runtime** | Ultralytics YOLOv8 | Pre-trained, easy Python integration, strong detection on TACO/trash datasets |
| **Database** | PostgreSQL 15 + PostGIS 3.3 | Geospatial queries, ACID compliance, production-grade |
| **ORM** | SQLAlchemy + Alembic | Type-safe ORM, migration management |
| **Auth** | JWT (python-jose) + bcrypt | Simple, stateless, industry standard |
| **Object Storage** | Cloudflare R2 or AWS S3 (or local `/uploads` for hackathon) | Persistent image storage; local fallback for demo |
| **Route API** | OpenRouteService (free tier) | Handles TSP/VRP, free API key, well-documented |
| **Containerization** | Docker + Docker Compose | Reproducible local and production builds |
| **Deployment** | Vercel (frontend) + Render/Railway (backend) | Fast deploy, free tier available |
| **Version Control** | GitHub | Standard |
| **API Testing** | Postman or Bruno | Contract testing during build |

### Deployment Model
- **Development:** Docker Compose spins up all services locally (frontend, backend, AI service, PostgreSQL).
- **Demo/Production:** Frontend on Vercel. Backend API + AI Service deployed as Docker containers on Render or Railway. PostgreSQL on Railway managed database or Supabase.
- **Images:** Stored in Cloudflare R2 (free tier) with signed URLs, or in local filesystem for hackathon with the assumption of ephemeral storage.

### Integration Points
- **OpenRouteService API:** Used for route optimization. `POST https://api.openrouteservice.org/v2/optimization`. Requires free API key.
- **Browser Geolocation API:** Used for GPS auto-detection on report submission.
- **Leaflet / OpenStreetMap:** Map tiles loaded from `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` — no API key required.
- **Mapbox (optional):** If custom map styling is needed, use Mapbox GL JS with a free-tier token.

### Observability
- FastAPI access logs (stdout) collected by Docker logging driver.
- Frontend error boundary logs unhandled exceptions to console and optionally to Sentry (free tier).
- Backend logs structured JSON with fields: `request_id`, `endpoint`, `user_id`, `status_code`, `latency_ms`.
- AI service logs inference time, confidence, and whether the fallback path was triggered.

---

## 14. Data Model

### Entity: `users`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| email | VARCHAR(255) UNIQUE | Required, validated |
| password_hash | VARCHAR(255) | bcrypt |
| display_name | VARCHAR(100) | Public-facing name |
| role | ENUM(citizen, crew, admin) | Default: citizen |
| total_points | INTEGER | Default: 0 |
| badge_tier | ENUM(Cleaner, Guardian, Hero) | Computed, cached |
| created_at | TIMESTAMPTZ | Auto |
| updated_at | TIMESTAMPTZ | Auto |

### Entity: `incidents`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| reporter_id | UUID (FK → users) | Nullable (anonymous reporting allowed) |
| assigned_to | UUID (FK → users) | Nullable, crew member |
| image_url | TEXT | URL to before-photo in object storage |
| after_image_url | TEXT | Nullable, URL to after-photo |
| location | GEOGRAPHY(POINT, 4326) | PostGIS geospatial point |
| address_text | TEXT | Reverse-geocoded or user-provided |
| note | TEXT | Optional user note (max 200 chars) |
| waste_detected | BOOLEAN | AI result |
| confidence | FLOAT | AI confidence score |
| severity | ENUM(None, Low, Medium, High) | AI-derived |
| bounding_boxes | JSONB | Optional array of box coords |
| status | ENUM(Pending, Assigned, InProgress, Cleaned, Verified, NeedsReview) | Default: Pending |
| priority_score | FLOAT | Computed (0–100) |
| is_hotspot | BOOLEAN | Whether in a known hotspot zone |
| created_at | TIMESTAMPTZ | Auto |
| updated_at | TIMESTAMPTZ | Auto |

**Indexes:** `location` (GIST spatial index), `status`, `severity`, `created_at`, `priority_score`.

### Entity: `routes`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| created_by | UUID (FK → users) | Admin who generated the route |
| assigned_to | UUID (FK → users) | Crew member |
| incident_ids | UUID[] | Ordered array of incident IDs |
| depot_location | GEOGRAPHY(POINT, 4326) | Nullable start point |
| polyline_geojson | JSONB | GeoJSON LineString from ORS |
| total_distance_km | FLOAT | From ORS response |
| estimated_duration_min | INTEGER | From ORS response |
| is_approximate | BOOLEAN | True if fallback algorithm used |
| status | ENUM(Active, Completed, Archived) | Default: Active |
| created_at | TIMESTAMPTZ | Auto |

### Entity: `hotspot_zones`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| center | GEOGRAPHY(POINT, 4326) | Centroid of the zone |
| polygon | GEOGRAPHY(POLYGON, 4326) | Zone boundary |
| incident_count | INTEGER | Number of incidents in period |
| recurrence_score | FLOAT | 0–1 prediction score |
| last_computed_at | TIMESTAMPTZ | When this zone was last updated |

### Entity: `point_transactions`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| user_id | UUID (FK → users) | Recipient |
| incident_id | UUID (FK → incidents) | Related incident |
| points | INTEGER | Positive value |
| reason | ENUM(report_confirmed, cleanup_verified, report_bonus) | |
| created_at | TIMESTAMPTZ | Auto |

### Relationships
- `users` (1) → (many) `incidents` (as reporter and as assigned crew)
- `incidents` (many) ↔ (1) `routes` (via incident_ids array)
- `users` (1) → (many) `point_transactions`
- `hotspot_zones` (1) → (many) `incidents` (via spatial containment, computed)

---

## 15. AI Usage Strategy

### Where AI Is Used
1. **Waste Detection (Core):** YOLOv8 model runs on every uploaded image to detect waste presence, count, bounding boxes, and derived severity score.
2. **Cleanup Verification (Should Have):** The same YOLOv8 model is reused on after-photos to confirm waste absence below threshold.
3. **Hotspot Prediction (Nice to Have):** A geospatial clustering algorithm (DBSCAN on PostGIS data, or grid-cell frequency count) predicts recurring zones. This is rule/stats-based, not deep-learning.

### Where AI Is NOT Used
- Route optimization (handled by ORS algorithm — deterministic TSP solver).
- Priority scoring (deterministic formula with weighted parameters).
- Authentication and authorization (rule-based).
- Task assignment (human admin decision).
- Points and leaderboard (deterministic counting).
- Geocoding (external API, not AI).

### Model Selection and Rationale
**Model:** YOLOv8n or YOLOv8s (Ultralytics).
**Pre-trained on:** COCO (base) + fine-tuned or directly used with TACO (Trash Annotations in Context) dataset weights if available via open repository. If TACO-fine-tuned weights are unavailable at build time, COCO-pre-trained YOLOv8 detects relevant classes (bottle, cup, banana, bag — proxies for trash) with acceptable accuracy for demo purposes.
**Assumption:** Pre-trained COCO weights are used for MVP. Fine-tuned TACO weights can be swapped in as a drop-in replacement without architecture changes.

### Input/Output Design
```json
// POST /infer
Input: { "image_url": "https://storage/images/uuid.jpg" }

// Response
Output: {
  "waste_detected": true,
  "confidence": 0.82,
  "severity": "High",
  "detections": [
    { "class": "bottle", "confidence": 0.82, "box": [x1, y1, x2, y2] },
    { "class": "bag", "confidence": 0.75, "box": [x1, y1, x2, y2] }
  ]
}
```

### Guardrails
- Confidence threshold is configurable via environment variable (`YOLO_CONFIDENCE_THRESHOLD=0.45`); default is 0.45.
- Only classes with high relevance to waste are scored (bottle, cup, bag, banana, can, cardboard). Unrelated COCO classes (person, car, dog) are filtered out of the results.
- If zero relevant-class detections exist above threshold, `waste_detected = false`.
- Maximum 50 detection boxes per image (cap to prevent runaway inference on complex images).

### Hallucination Control
- Output labels are fixed enumerations (Low/Medium/High/None) — no free-text generation.
- Confidence scores are passed through to the UI so admins can contextualize the AI result.
- An explicit "Manual Review" path allows admins to override any AI decision.
- The system never uses AI for legal, safety-critical, or financial decisions — only for waste presence classification.

### Fallback Behavior
- If the AI service is unreachable: the report is saved with `severity = null`, `status = Pending AI Review`, and an admin notification is generated.
- If inference times out (> 10s): same as above.
- Admin can manually set severity on any report, overriding the AI result.

### Evaluation Method
- For the demo: use a prepared set of 10 test images (5 with clear waste, 5 clean/ambiguous) to demonstrate detection accuracy live.
- Post-hackathon: evaluate using standard COCO metrics (mAP@0.5) on the TACO test split.
- Ongoing: track false-positive rate (admin override rate) and false-negative rate (user resubmission rate) from production logs.

---

## 16. Edge Cases and Failure Handling

| Scenario | System Behavior |
|---|---|
| User uploads a non-waste image (e.g., a person, a car) | AI detects no relevant waste classes → "No waste detected" returned; no incident created unless user forces manual submission |
| Two reports submitted for the same location within 20 meters and 10 minutes | Backend flags as `possible_duplicate = true`; admin notified on dashboard; both records kept until admin merges or confirms |
| AI service completely down | Report saved with `status = Pending AI Review`; map marker shown with gray "AI Pending" badge; admin informed via dashboard warning banner |
| Routing API rate-limited | Nearest-neighbor fallback activated automatically; result flagged as "Approximate Route" with a tooltip |
| User submits without GPS permission | Map picker required; form submission blocked until a pin is placed; clear instruction shown |
| Cleanup after-photo shows same waste still present | Status set to "Needs Review"; admin receives notification; points NOT awarded; worker instructed to clean again |
| Image upload fails midway (network drop) | Frontend retries up to 3 times with exponential backoff; if all fail, user sees "Upload failed — try again" with resume option |
| Admin deletes an incident that is part of an active route | Route is flagged as "Outdated"; crew is notified the stop has been removed |
| More than 500 simultaneous active incidents on map | Clustering automatically activates; server paginates map feed API by viewport bounds |
| User earns points but is not logged in | Points are not awarded; report is still accepted; post-submission, user is invited to "Create account to earn points" |

---

## 17. Security and Privacy

### Authentication and Authorization
- JWT tokens are issued on login with a 24-hour expiration.
- Refresh token rotation is implemented with 7-day validity.
- Role-based access control: `citizen`, `crew`, `admin`.
- Admin-only routes (dashboard, bulk actions, crew management) validate the `admin` role on every request at the middleware layer, not just on login.

### Sensitive Data Handling
- Passwords are hashed with bcrypt (cost factor 12) and never stored in plaintext.
- Image URLs use opaque UUIDs (e.g., `https://storage/images/f8a2c1d3-...jpg`) — not sequential IDs that reveal upload count.
- GPS coordinates are stored in the database but never exposed in public-facing API responses (leaderboard, public map).
- In public map responses, coordinates are returned with limited precision (3 decimal places ≈ 111m radius) to protect reporter privacy.

### Least-Privilege Principles
- Citizens: can create reports and update their own profile only.
- Crew: can update status of assigned incidents and upload after-photos only.
- Admins: full CRUD on incidents, routes, and user management.
- AI service: has read-only access to object storage for inference; cannot write to the database.

### Abuse Prevention
- Rate limiting on the report submission endpoint: max 10 reports per IP per hour.
- Image deduplication check: if the same image hash is submitted twice, the second submission is flagged and held for admin review.
- Anonymous reporting is allowed but point awards require a logged-in account.
- CSRF protection via SameSite cookie policy and origin validation on mutations.

### Logging Policy
- Access logs: method, path, status code, latency, user_id (anonymized).
- Error logs: full stack trace, request_id, no PII in error payloads.
- AI inference logs: image UUID, inference time, severity result — no image content in logs.
- Logs retained for 30 days in production; dev logs are stdout only.

---

## 18. Metrics and Success Criteria

### North-Star Metric
**Time from waste report to verified cleanup** — the average duration (in hours) between `incident.created_at` and `incident.status = Verified`. Lower is better.

### Supporting Metrics
| Metric | Definition | Target |
|---|---|---|
| Report-to-detection rate | % of reports where AI detects waste | > 75% |
| Assignment rate | % of Pending incidents assigned within 4 hours | > 80% |
| Cleanup verification rate | % of Cleaned incidents with verified after-photo | > 70% |
| Route efficiency | Avg distance reduction vs naive sequential routing | > 20% |
| AI false positive rate | % of incidents where admin overrides "waste detected" to None | < 15% |
| AI false negative rate | % of reports where admin overrides "no waste" to has waste | < 10% |

### Adoption Metrics
- Daily active reporters (citizen users submitting ≥ 1 report/day).
- Admin dashboard sessions per day.
- Routes generated per day.

### Quality Metrics
- API error rate < 1%.
- AI inference timeout rate < 2%.
- Route generation success rate > 95%.

### Reliability Metrics
- API p95 latency < 500ms.
- AI inference p95 latency < 10s.
- Map initial load < 3s.

### Hackathon Demo Success Criteria
1. User uploads a waste image → AI returns severity result in < 10 seconds.
2. Map marker appears at the correct location immediately after submission.
3. Admin dashboard shows the new incident with correct severity and priority.
4. Route is generated for 5+ pending incidents and rendered as a polyline on the map within 5 seconds.
5. After-photo upload results in "Verified Clean" status update.
6. Leaderboard updates with the reporter's new point balance.
7. All flows complete without a manual backend restart or data seeding during the demo.

---

## 19. Milestone Plan

### Phase 0: Foundation (Hours 0–4)
**Scope:** Environment setup, project scaffold, database schema, auth skeleton.
**Deliverables:**
- Docker Compose with Next.js, FastAPI, PostgreSQL+PostGIS services.
- Database migrations for `users`, `incidents`, `routes`, `point_transactions`.
- JWT auth endpoints: `POST /auth/login`, `POST /auth/register`.
- Basic frontend shell: header, routing, placeholder map page.
- Seed data script: 5 users (1 admin, 2 crew, 2 citizens), 20 sample incidents with coordinates.
**Dependencies:** Docker installed, GitHub repo initialized.

### Phase 1: MVP Core Loop (Hours 4–16)
**Scope:** Image upload, AI detection, map visualization, admin dashboard.
**Deliverables:**
- Image upload endpoint with S3/local storage.
- AI inference service with YOLOv8 pre-trained model wired to `/infer` endpoint.
- Severity classification logic.
- `POST /api/reports` creates incident, calls AI, stores result.
- Map screen renders all incidents as color-coded markers.
- Popup on marker click shows thumbnail, severity, status.
- Admin dashboard with sortable table + map sync.
- Task assignment (incident → crew member).
- Status update endpoints.
**Dependencies:** Phase 0 complete.

### Phase 2: Route Optimization (Hours 16–22)
**Scope:** Route generation, polyline rendering, fallback algorithm.
**Deliverables:**
- `POST /api/routes` endpoint calling ORS API.
- Nearest-neighbor fallback algorithm.
- Route polyline rendering on map.
- Numbered stop markers.
- Distance + ETA display.
- "Plan Routes" flow in admin dashboard.
**Dependencies:** Phase 1 complete, ORS API key obtained.

### Phase 3: Verification and Gamification (Hours 22–30)
**Scope:** Before/after cleanup proof, points, leaderboard.
**Deliverables:**
- After-photo upload flow in crew view.
- AI verification reuse for cleanup confirmation.
- `Verified` and `Needs Review` status states.
- Points award on report confirmation and verified cleanup.
- `GET /api/leaderboard` endpoint.
- Leaderboard screen.
- Badge tier computation.
**Dependencies:** Phase 2 complete.

### Phase 4: Hotspot Prediction and Polish (Hours 30–42)
**Scope:** Hotspot heatmap, priority scoring, UX polish, demo prep.
**Deliverables:**
- Grid-cell hotspot aggregation from historical data.
- Hotspot heatmap layer (togglable).
- Priority score computation and display.
- Full UX polish pass: loading states, empty states, error states.
- Demo run-through with preloaded data.
- Fallback paths tested (AI down, route API down).
- README with setup instructions.
**Dependencies:** Phase 3 complete.

### Phase 5: Production Hardening (Post-Hackathon)
**Scope:** Rate limiting, real auth hardening, multi-zone support, mobile optimization.
**Deliverables:**
- Rate limiting middleware.
- Refresh token rotation.
- Mobile-responsive audit.
- CI/CD pipeline (GitHub Actions → Render deploy).
- API documentation published.
- Monitoring (Sentry + structured logging).

---

## 20. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation | Fallback |
|---|---|---|---|---|
| AI model quality is poor on real-world trash photos | High — core feature fails | Medium | Use YOLOv8 with TACO or COCO weights; set threshold at 0.45 | Pre-annotated demo images ready; manual severity entry for demo |
| ORS routing API is rate-limited or down | Medium — route feature fails | Low-Medium | Cache API key; monitor rate limits; implement nearest-neighbor fallback | Run demo with pre-generated route stored in DB |
| Scope creep destroys MVP timeline | High — nothing works | High | Freeze feature scope at Phase 1; extras only after core loop is stable | Use pre-PRD's strict MVP definition |
| GPS geolocation permission blocked | Low — affects reporter flow | Medium | Manual map pin picker as default; GPS is opt-in enhancement | Map picker always available |
| Cleanup verification AI unreliable | Medium — verification feature feels broken | Medium | Reuse detection model with a lower threshold; fall back to admin manual review | "Pending Verification" state is acceptable fallback |
| PostGIS geospatial query performance | Low — acceptable at hackathon scale | Low | Add GIST indexes on `location` field | Bounding box pre-filter before spatial query |
| Demo data is insufficient to show hotspots | Low — one feature looks weak | Medium | Include 50+ seeded incidents across 5 zones in DB init script | Disable hotspot feature if not ready; it is Nice-to-Have |
| Frontend-backend integration takes too long | High — demo is incomplete | Medium | Agree on API contract at Phase 0; use mock data in frontend during backend development | Frontend can run against seeded mock API (JSON server) |

---

## 21. Testing Strategy

### Unit Tests
- AI service: Test severity classification logic with fixture images. Verify that confidence thresholding produces correct `Low/Medium/High/None` labels.
- Priority score formula: Unit test the scoring function with edge inputs (age = 0, severity = High, hotspot = true).
- Route fallback: Unit test nearest-neighbor algorithm with known coordinate sets and verify output order.
- Points calculation: Unit test all point award triggers and amounts.

### Integration Tests
- `POST /api/reports`: End-to-end test with a real image upload → AI inference → database write → response.
- `POST /api/routes`: Integration test with ORS mock → polyline returned → stored in DB.
- `PATCH /api/reports/:id/status` with after-photo: Test verification flow with mocked AI response for both "clean" and "still dirty" scenarios.

### End-to-End Tests
- Use Playwright or Cypress for:
  - Full report submission flow (upload → result → map pin appears).
  - Admin login → incident sort → task assignment.
  - Route generation → polyline on map.
  - Cleanup verification → status change → leaderboard update.

### UX Validation
- Run the 5-minute demo script with someone unfamiliar with the product.
- Confirm all error states are triggerable and informative.
- Test on Chrome Mobile (iOS and Android simulation in DevTools).

### AI Evaluation
- Prepare a test set of 20 images: 10 with visible waste (varying severity), 10 clean/irrelevant.
- Run inference on all 20; record precision and recall.
- Target: ≥ 80% precision on waste-present images, ≤ 20% false positive rate on clean images.

### Acceptance Criteria
- All 7 demo success criteria in Section 18 pass without manual intervention.
- No unhandled 500 errors appear in the browser console during the demo flow.
- All three role types (citizen, crew, admin) can complete their primary flow without confusion.

---

## 22. Analytics / Telemetry

### Events to Track
| Event | Properties | Purpose |
|---|---|---|
| `report_submitted` | user_id, has_gps, image_size_kb | Understand submission quality |
| `ai_inference_completed` | severity, confidence, duration_ms, model_version | Monitor AI performance |
| `ai_inference_failed` | error_type, fallback_triggered | Track service reliability |
| `incident_assigned` | incident_id, admin_id, crew_id, priority_score | Measure dispatch efficiency |
| `route_generated` | stop_count, is_approximate, distance_km, duration_ms | Track routing usage |
| `cleanup_verified` | incident_id, worker_id, result (verified/needs_review) | Track verification accuracy |
| `points_awarded` | user_id, points, reason | Monitor gamification engagement |
| `leaderboard_viewed` | user_id (nullable) | Measure engagement with social feature |
| `admin_override` | incident_id, field, old_value, new_value | Track AI errors for model improvement |

### Funnel Stages
1. User opens app (session start)
2. User clicks "Report Waste" (intent)
3. User uploads image (image submission)
4. AI result returned (AI conversion)
5. Incident pinned on map (data creation)
6. Incident assigned by admin (operational conversion)
7. Route generated (routing usage)
8. Cleanup completed and verified (outcome)

### Product Learning Goals
- What % of submitted images result in a confirmed waste detection? (AI quality signal)
- What is the average time from submission to assignment? (Admin response speed)
- What % of reports lead to verified cleanup? (Operational effectiveness)
- Which features are used most in the demo? (Feature value validation)

---

## 23. Open Questions / Assumptions

### Assumptions Made
1. **COCO pre-trained YOLOv8 is sufficient for demo purposes.** The COCO dataset includes trash-adjacent classes (bottle, cup, bag). This may produce occasional false positives on non-waste objects but is acceptable for hackathon validation. Fine-tuned TACO weights are the production path.
2. **Browser geolocation is available on demo devices.** The demo will be conducted on a modern device with GPS/IP geolocation support. Manual pin fallback is available regardless.
3. **OpenRouteService free tier is sufficient for demo volume.** The free tier allows up to 40 route optimization requests per day. Demo usage will not exceed this.
4. **Seed data will be pre-loaded at demo time.** To show hotspots and a meaningful leaderboard, a DB seed script will create 50 incidents across 5 zones and 5 users before the demo.
5. **Object storage for images.** For the hackathon, local file storage with a static file server is acceptable. Cloudflare R2 or AWS S3 is the production path.
6. **Single-tenant architecture is sufficient.** Multi-city multi-tenant support is a post-hackathon concern.
7. **No real crew mobile app is required.** The crew view is a mobile-responsive web page, not a native app.
8. **Anonymous reporting is supported.** Users do not need to be logged in to submit a report; points require a logged-in account.

### Open Questions
1. Should the hotspot prediction use simple grid-cell frequency counting (deterministic, fast, demo-reliable) or DBSCAN clustering (more accurate, but requires scikit-learn and more setup time)?
   **Assumed decision:** Grid-cell frequency for MVP/demo; DBSCAN for V2.
2. Should the admin be able to create crew user accounts from within the dashboard, or must crew register themselves and be promoted by an admin?
   **Assumed decision:** Crew register themselves; admin promotes to `crew` role from the dashboard.
3. What is the maximum number of waypoints the fallback nearest-neighbor algorithm needs to handle?
   **Assumed decision:** Cap at 50 waypoints in the fallback; beyond 50, show a warning and suggest splitting the route.
4. Should citizens be allowed to comment on incidents (discussion thread), or only see status updates?
   **Assumed decision:** Status-only for MVP; comments are a V2 feature.

---

## 24. Future Roadmap

### Next Phase Features
- Native mobile apps (React Native) with offline-first report submission.
- Real-time crew location tracking on admin map.
- IoT bin sensor integration (MQTT/HTTP feed from smart bins to augment image-based reports).
- Social reporting: share incidents on social media with a deep link to the CleanGrid pin.
- Multilingual UI (priority languages: Spanish, Hindi, French, Portuguese).
- Advanced hotspot prediction with time-series modeling (Prophet or LSTM on historical data).
- Push notifications for status updates and cleanup assignments.

### Scaling Path
- Move AI inference to AWS Lambda + SageMaker or Google Cloud Run for auto-scaling.
- Introduce Kafka or Redis Streams for real-time event processing (status changes, point awards) beyond polling.
- Migrate to multi-tenant architecture: each municipality gets an isolated database schema or tenant-scoped partition.
- Add Redis caching for leaderboard and hotspot layer (invalidate nightly or on threshold events).
- Kubernetes deployment for horizontal scaling of backend and AI service.

### Monetization Opportunities
- **SaaS subscription:** Municipal governments pay a monthly fee per active zone or per crew account.
- **Premium analytics:** Advanced hotspot trend reports, waste tonnage forecasting, budget planning dashboards.
- **White-label:** Private waste haulers operate CleanGrid under their own brand.
- **Data insights:** Aggregate, anonymized waste trend data sold to NGOs, urban planners, and research institutions.
- **Sponsored rewards:** Recycling or sustainability brands sponsor point redemption rewards (coupons, credits).

### Production Roadmap
1. **Pilot (Month 1–2):** Deploy on a university campus or municipal zone. Onboard 1 admin, 5 crew, 50 citizen reporters. Collect real incident data. Measure north-star metric baseline.
2. **Refinement (Month 2–4):** Fine-tune YOLOv8 on collected real-world data. Improve hotspot model with 90-day data. Add mobile app. Integrate 1 partner municipality.
3. **Expansion (Month 4–8):** Multi-zone, multi-crew support. Launch SaaS pricing. Onboard 3–5 paying municipalities.
4. **Scale (Month 8–18):** Multi-country support. IoT integration. Series A fundraise targeting $10M+ potential savings for city partners as primary ROI narrative.

---

## 25. Final Implementation Notes

### What Must Be Built First
The single most important thing to prove at any stage is the core loop: **image upload → AI detection → map pin → route → cleanup verified**. This loop must work end-to-end before any other feature is added. Build it in this exact order and do not move to Phase 2 until Phase 1 is demo-stable.

### What Should Be Avoided
- **Do not build a custom AI model from scratch.** Use pre-trained YOLOv8. Training takes time and the result will be worse than a fine-tuned existing model.
- **Do not implement blockchain, AR, or drone integration.** These add zero value to the demo and consume all available time.
- **Do not start gamification before the core loop is proven.** Points mean nothing if the map doesn't work.
- **Do not over-engineer the routing.** The nearest-neighbor fallback is good enough to demonstrate the concept. ORS handles the real optimization.
- **Do not hard-code API keys.** Use `.env` files from the first commit.
- **Do not use `useState` polling for the admin dashboard in production.** Use WebSockets or SSE in V2 — polling every 30 seconds is acceptable for demo.

### What Will Make This Project Stand Out
1. **A fully closed loop, live, with no manual backend steps.** Most competing teams will show either detection OR a map. Showing detection → map → route → verified cleanup in one live flow is the differentiator.
2. **A clean, operational UI that feels like a real product.** Not a Jupyter notebook demo — a working web application with real UX.
3. **The "before/after" verification moment** is visually compelling and conceptually unique. No other team in a typical hackathon will have this.
4. **A credible production architecture story.** When judges ask "how would this scale?", the answer is immediate and specific: PostGIS, containerized AI, microservices, ORS, multi-tenant SaaS.

### Minimum Version That Still Delivers Strong Value
If time is severely constrained, the minimum valuable demo consists of:
1. Image upload → AI severity result displayed.
2. Map showing one or more incident markers from that upload.
3. Admin dashboard listing the incident.
4. A pre-generated optimized route shown on the map (can use cached/seeded data).

This four-step demo, even without live route generation or cleanup verification, tells a complete and compelling story if delivered with confidence and with clear problem-to-solution framing. Build this version first and expand from there.

---

*PRD version 1.0 — CleanGrid — AI-Powered Smart Waste Management & Mapping System*  
*Prepared to serve as the single source of truth for design, development, AI coding agents, and stakeholder communication.*

```
frontend/
README.md
package.json
next.config.js
tailwind.config.ts
tsconfig.json
src/
  app/
    (map)/
      page.tsx                    # Map home screen (main landing)
      layout.tsx                  # Layout for map routes
    report/
      page.tsx                    # Report waste submission
      layout.tsx                  # Layout for report routes
    admin/
      page.tsx                    # Admin dashboard
      layout.tsx                  # Admin layout with auth guard
    route/
      [id]/
        page.tsx                  # Route view page
        layout.tsx                # Route layout
    leaderboard/
      page.tsx                    # Leaderboard page
      layout.tsx                  # Leaderboard layout
    profile/
      page.tsx                    # User profile
      layout.tsx                  # Profile layout
    globals.css                   # Global styles
    layout.tsx                    # Root layout
    page.tsx                      # Home page (redirects to map)
  components/
    map/
      IncidentMap.tsx             # Main Leaflet map component
      IncidentMarker.tsx          # Severity-coded incident marker
      RoutePolyline.tsx           # Route overlay component
      HeatmapLayer.tsx            # Heatmap overlay
      MarkerClusterGroup.tsx      # Marker clustering
      LayerToggleBar.tsx          # Map layer controls
      MapControls.tsx             # Zoom/pan controls
    admin/
      IncidentTable.tsx           # Admin incident table
      IncidentDrawer.tsx          # Right-side detail panel
      BulkActionBar.tsx           # Bulk selection actions
      FilterBar.tsx               # Admin filters
      StatsBar.tsx                # Admin KPIs
      AssignDropdown.tsx          # Crew assignment dropdown
    report/
      ImageUploader.tsx           # Drag-drop image upload
      LocationPicker.tsx          # GPS + manual pin location
      AIResultCard.tsx            # AI analysis results
      ReportForm.tsx              # Complete report form
    ui/                           # shadcn/ui components (auto-generated)
      button.tsx
      table.tsx
      drawer.tsx
      badge.tsx
      toast.tsx
      ... (other shadcn components)
    common/
      LoadingSkeleton.tsx         # Loading states
      ErrorBoundary.tsx           # Error handling
      Header.tsx                  # App header
      Footer.tsx                  # App footer
  lib/
    stores/
      auth.ts                     # Zustand auth store
      map.ts                      # Map state/filters store
      incidents.ts                # Incident data store
    api/
      client.ts                   # API client configuration
      incidents.ts                # Incident API calls
      auth.ts                     # Auth API calls
      routes.ts                   # Route API calls
      leaderboard.ts              # Leaderboard API calls
    utils/
      api.ts                      # API utilities
      auth.ts                     # Auth utilities
      map.ts                      # Map utilities
      validation.ts               # Form validation
      constants.ts                # App constants
  types/
    auth.ts                      # Auth type definitions
    incident.ts                  # Incident type definitions
    route.ts                     # Route type definitions
    api.ts                       # API response types
  public/
    icons/
      marker-icons/              # Custom marker images
    images/
      placeholder.jpg            # Default image
    leaflet/                     # Leaflet assets if needed
```

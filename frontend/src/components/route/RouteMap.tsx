"use client";

import { useEffect, useRef } from "react";
import dynamic from "next/dynamic";
import L from "leaflet";

// Dynamic imports to avoid SSR issues
const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false }
);

const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false }
);

const Polyline = dynamic(
  () => import("react-leaflet").then((mod) => mod.Polyline),
  { ssr: false }
);

const Marker = dynamic(
  () => import("react-leaflet").then((mod) => mod.Marker),
  { ssr: false }
);

const Popup = dynamic(
  () => import("react-leaflet").then((mod) => mod.Popup),
  { ssr: false }
);

interface RouteMapProps {
  route?: {
    id: string;
    polyline?: string | null;
    stops: Array<{
      id: string;
      stop_order: number;
      status: string;
      incident: {
        id: string;
        location: { lat: number; lon: number } | null;
        severity: string | null;
        status: string;
        address_text: string | null;
        created_at: string;
      };
    }>;
  };
  className?: string;
}

function RouteMap({ route, className }: RouteMapProps) {
  const mapRef = useRef<L.Map | null>(null);

  // Parse polyline if available
  const polylinePositions = route?.polyline ? parsePolyline(route.polyline) : [];

  // Create numbered icon for markers
  const createNumberedIcon = (stopOrder: number) => {
    return L.divIcon({
      className: "custom-div-icon",
      html: `<div class="flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full font-bold text-xs shadow-lg">${stopOrder}</div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });
  };

  useEffect(() => {
    if (mapRef.current && route) {
      // Fit map to show all stops
      const bounds = L.latLngBounds(
        route.stops
          .filter(stop => stop.incident.location)
          .map(stop => [stop.incident.location!.lat, stop.incident.location!.lon])
      );

      if (bounds.isValid()) {
        mapRef.current.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [route]);

  if (!route) {
    return (
      <div className={`bg-gray-100 rounded-lg p-4 ${className || ""}`}>
        <div className="text-center text-gray-500">
          No route data available
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-lg overflow-hidden ${className || ""}`}>
      <MapContainer
        center={[40.7128, -74.0060]} // Default to NYC
        zoom={12}
        className="h-96 w-full"
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Route polyline */}
        {polylinePositions.length > 0 && (
          <Polyline
            positions={polylinePositions}
            color="#3B82F6"
            weight={4}
            opacity={0.7}
          />
        )}

        {/* Stop markers */}
        {route.stops.map((stop) => {
          if (!stop.incident.location) return null;

          return (
            <Marker
              key={stop.id}
              position={[stop.incident.location.lat, stop.incident.location.lon]}
              icon={createNumberedIcon(stop.stop_order)}
            >
              <Popup>
                <div className="p-2 min-w-48">
                  <h3 className="font-bold text-lg mb-2">Stop #{stop.stop_order}</h3>
                  <div className="space-y-1">
                    <p className="text-sm"><strong>Status:</strong> {stop.status}</p>
                    <p className="text-sm"><strong>Severity:</strong> {stop.incident.severity || 'Unknown'}</p>
                    <p className="text-sm"><strong>Address:</strong> {stop.incident.address_text || 'No address'}</p>
                    <p className="text-xs text-gray-500">
                      <strong>Reported:</strong> {new Date(stop.incident.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}

// Helper function to parse polyline string (simplified version)
function parsePolyline(polylineStr: string): [number, number][] {
  try {
    // This is a simplified parser - in production you'd want a proper polyline decoder
    // For now, return empty array if polyline is not properly formatted
    if (!polylineStr || polylineStr === 'null') {
      return [];
    }

    // Try to parse as GeoJSON
    if (polylineStr.startsWith('{')) {
      const geoJson = JSON.parse(polylineStr);
      if (geoJson.type === 'LineString' && geoJson.coordinates) {
        return geoJson.coordinates.map((coord: number[]) => [coord[1], coord[0]]); // [lat, lon]
      }
    }

    return [];
  } catch (error) {
    console.error('Error parsing polyline:', error);
    return [];
  }
}

export default RouteMap;

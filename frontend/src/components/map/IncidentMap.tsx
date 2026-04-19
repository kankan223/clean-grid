'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { Skeleton } from '@/components/ui/skeleton';

// Dynamic import with SSR disabled to prevent window object errors
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);

const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);

const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false }
);

const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
);

interface Incident {
  id: string;
  lat: number;
  lng: number;
  severity: 'Low' | 'Medium' | 'High' | 'None';
  status: 'Pending' | 'Assigned' | 'InProgress' | 'Cleaned' | 'Verified' | 'NeedsReview';
  imageUrl: string;
  createdAt: string;
  address?: string;
}

interface IncidentMapProps {
  incidents: Incident[];
  center?: [number, number];
  zoom?: number;
  onMarkerClick?: (incident: Incident) => void;
  className?: string;
}

function LocationFlyTo({ position }: { position: [number, number] | null }) {
  const map = useMap();

  useEffect(() => {
    if (position) {
      map.flyTo(position, 14);
    }
  }, [map, position]);

  return null;
}

export default function IncidentMap({
  incidents,
  center = [40.7128, -74.0060],
  zoom = 12,
  onMarkerClick,
  className = 'h-full w-full',
}: IncidentMapProps) {
  const [isClient, setIsClient] = useState(false);
  const [userPosition, setUserPosition] = useState<[number, number] | null>(null);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient || !navigator.geolocation) {
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserPosition([position.coords.latitude, position.coords.longitude]);
      },
      () => {
        // Keep fallback center when geolocation is denied/unavailable/times out.
        setUserPosition(null);
      },
      {
        enableHighAccuracy: true,
        timeout: 8000,
        maximumAge: 0,
      }
    );
  }, [isClient]);

  // Create severity-colored marker icons
  const getSeverityIcon = (severity: string) => {
    const severityColors: Record<string, string> = {
      'High': '#dc2626',     // Red
      'Medium': '#ea580c',   // Orange
      'Low': '#16a34a',      // Green
      'None': '#6b7280',     // Gray
    };

    const color = severityColors[severity] || severityColors['None'];

    return L.divIcon({
      className: 'custom-severity-marker',
      html: `
        <div style="
          background-color: ${color};
          color: white;
          border-radius: 50%;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 14px;
          border: 3px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">
          ●
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      popupAnchor: [0, -16],
    });
  };

  return (
    <div className={className} style={{ minHeight: '400px' }}>
      {isClient ? (
        <MapContainer
          center={center}
          zoom={zoom}
          className="h-full w-full"
        >
          <LocationFlyTo position={userPosition} />

          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {incidents.map((incident) => (
            <Marker
              key={incident.id}
              position={[incident.lat, incident.lng]}
              icon={getSeverityIcon(incident.severity)}
              eventHandlers={{
                click: () => onMarkerClick?.(incident),
              }}
            >
              <Popup>
                <div className="p-2 min-w-[200px]">
                  <div className="font-semibold text-sm mb-1">
                    {incident.severity} Severity
                  </div>
                  <div className="text-xs text-gray-600 mb-1">
                    Status: {incident.status}
                  </div>
                  {incident.address && (
                    <div className="text-xs text-gray-600 mb-1">
                      {incident.address}
                    </div>
                  )}
                  {incident.imageUrl && (
                    <img
                      src={incident.imageUrl}
                      alt="Incident"
                      className="w-full h-24 object-cover rounded mb-1"
                    />
                  )}
                  <div className="text-xs text-gray-500">
                    Reported: {new Date(incident.createdAt).toLocaleDateString()}
                  </div>
                  <div className="mt-2">
                    <button
                      onClick={() => onMarkerClick?.(incident)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      View Details →
                    </button>
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      ) : (
        <Skeleton className="h-full w-full" />
      )}
    </div>
  );
}

'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';

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

// Severity color mapping
const severityColors = {
  High: '#E84855',
  Medium: '#F9A03F',
  Low: '#4CAF50',
  None: '#9E9E9E',
  Verified: '#9E9E9E', // Cleaned/Verified
  NeedsReview: '#FF9800',
};

// Status opacity mapping
const statusOpacity = {
  Pending: 1.0,
  Assigned: 0.9,
  InProgress: 0.7,
  Cleaned: 0.5,
  Verified: 0.3,
  NeedsReview: 0.8,
};

export default function IncidentMap({
  incidents,
  center = [40.7128, -74.0060],
  zoom = 12,
  onMarkerClick,
  className = 'h-full w-full',
}: IncidentMapProps) {
  const [mapReady, setMapReady] = useState(false);
  const mapRef = useRef<any>(null);

  // Auto-fit map to show all incidents
  useEffect(() => {
    if (mapReady && mapRef.current && incidents.length > 0) {
      // Note: fitBounds will be handled by the MapContainer component
    }
  }, [incidents, mapReady]);

  // Create custom icon for severity
  const createCustomIcon = (severity: string, status: string) => {
    const color = severityColors[severity as keyof typeof severityColors] || '#9E9E9E';
    const opacity = statusOpacity[status as keyof typeof statusOpacity] || 1.0;
    
    return {
      className: 'custom-incident-marker',
      html: `
        <div style="
          background-color: ${color};
          opacity: ${opacity};
          width: 12px;
          height: 12px;
          border-radius: 50%;
          border: 2px solid white;
        "></div>
      `,
      iconSize: [20, 20],
      iconAnchor: [10, 10],
    };
  };

  if (!mapReady) {
    return (
      <div className={`${className} bg-gray-100 animate-pulse flex items-center justify-center`}>
        <div className="text-gray-500">Loading map...</div>
      </div>
    );
  }

  return (
    <div className={className} style={{ minHeight: '400px' }}>
      <MapContainer
        center={center}
        zoom={zoom}
        className="h-full w-full"
        ref={mapRef}
        whenReady={() => setMapReady(true)}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {incidents.map((incident) => (
          <Marker
            key={incident.id}
            position={[incident.lat, incident.lng]}
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
    </div>
  );
}

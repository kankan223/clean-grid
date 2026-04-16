'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { LatLngExpression } from 'leaflet';

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
  center?: LatLngExpression;
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
  const [L, setL] = useState<any>(null);
  const mapRef = useRef<any>(null);

  // Load Leaflet only on client side
  useEffect(() => {
    import('leaflet').then((leaflet) => {
      setL(leaflet.default);
      setMapReady(true);
      
      // Fix for default markers in React
      delete (leaflet.default.Icon.Default.prototype as any)._getIconUrl;
      leaflet.default.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      });
    });
  }, []);

  // Auto-fit map to show all incidents
  useEffect(() => {
    if (mapReady && L && mapRef.current && incidents.length > 0) {
      const bounds = new L.LatLngBounds(
        incidents.map(incident => [incident.lat, incident.lng])
      );
      mapRef.current.fitBounds(bounds, { padding: [20, 20] });
    }
  }, [incidents, mapReady, L]);

  // Create custom icon for severity
  const createCustomIcon = (severity: string, status: string) => {
    if (!L) return null;
    
    const color = severityColors[severity as keyof typeof severityColors] || '#9E9E9E';
    const opacity = statusOpacity[status as keyof typeof statusOpacity] || 1.0;
    
    return L.divIcon({
      className: 'custom-incident-marker',
      html: `
        <div style="
          background-color: ${color};
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid white;
          opacity: ${opacity};
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        "></div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
      popupAnchor: [0, -12],
    });
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
        
        {incidents.map((incident) => {
          const customIcon = createCustomIcon(incident.severity, incident.status);
          
          return (
            <Marker
              key={incident.id}
              position={[incident.lat, incident.lng]}
              icon={customIcon}
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
                    {new Date(incident.createdAt).toLocaleString()}
                  </div>
                  {onMarkerClick && (
                    <button
                      onClick={() => onMarkerClick(incident)}
                      className="mt-2 text-xs bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                    >
                      View Details
                    </button>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}

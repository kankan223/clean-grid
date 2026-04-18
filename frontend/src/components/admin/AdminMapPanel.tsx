"use client";

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';

// Dynamic import for Leaflet components
const IncidentMap = dynamic(
  () => import("@/components/map/IncidentMap"),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 border-t-transparent mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Loading map...</p>
        </div>
      </div>
    )
  }
);

interface AdminMapPanelProps {
  className?: string;
  incidents: any[];
}

export function AdminMapPanel({ className = "", incidents }: AdminMapPanelProps) {
  const [mapKey, setMapKey] = useState(0);
  
  // Force map re-render when incidents change significantly
  useEffect(() => {
    setMapKey(prev => prev + 1);
  }, [incidents.length]);
  
  return (
    <div className={`relative h-full bg-gray-50 ${className}`}>
      <div className="absolute top-2 left-2 z-10 bg-white rounded-lg shadow-md px-3 py-2">
        <div className="text-sm font-medium text-gray-900">Live Map</div>
        <div className="text-xs text-gray-600">
          {incidents.length} incidents
        </div>
      </div>
      
      {/* Map Container */}
      <div className="h-full">
        <IncidentMap
          key={mapKey}
          incidents={incidents}
          center={[40.7128, -74.0060]} // Default to NYC
          zoom={12}
          className="h-full w-full"
        />
      </div>
    </div>
  );
}

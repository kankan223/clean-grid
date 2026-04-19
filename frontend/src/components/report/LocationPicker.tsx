/**
 * LocationPicker - CleanGrid Phase 1
 * Interactive mini-map with draggable pin for location selection
 */

'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import L from 'leaflet';
import { useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/toast';

// Dynamic imports to avoid SSR issues
const MapContainer = dynamic(
  () => import('react-leaflet').then(mod => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then(mod => mod.TileLayer),
  { ssr: false }
);
const Marker = dynamic(
  () => import('react-leaflet').then(mod => mod.Marker),
  { ssr: false,loading: () => null }
);

// Create marker icon once to avoid recreation
const createPickerIcon = () => {
  return L.divIcon({
    className: 'location-picker-marker',
    html: '<div style="background-color: #3b82f6; width: 32px; height: 40px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); border: 3px solid white; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"><div style="transform: rotate(45deg); font-size: 18px;">📍</div></div>',
    iconSize: [32, 40],
    iconAnchor: [16, 40],
    popupAnchor: [0, -40],
  });
};

const GEOLOCATION_OPTIONS = {
  enableHighAccuracy: false,
  timeout: 45000,
  maximumAge: 5 * 60 * 1000,
};

function MapPositionUpdater({ position }: { position: [number, number] }) {
  const map = useMap();

  useEffect(() => {
    map.setView(position, map.getZoom(), { animate: true });
  }, [map, position]);

  return null;
}

interface LocationPickerProps {
  onLocationChange: (lat: number, lng: number) => void;
  initialLocation?: { lat: number; lng: number };
  className?: string;
}

const LocationPicker: React.FC<LocationPickerProps> = ({ 
  onLocationChange, 
  initialLocation,
  className = ''
}) => {
  const { toast } = useToast();
  const [position, setPosition] = useState(initialLocation || { lat: 40.7128, lng: -74.0060 }); // NYC default
  const [isGeolocating, setIsGeolocating] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const [address, setAddress] = useState<string>('');

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Handle GPS geolocation
  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      toast({
        title: 'Geolocation unavailable',
        description: 'Your browser does not support geolocation.',
        variant: 'error',
      });
      return;
    }

    setIsGeolocating(true);
    
    navigator.geolocation.getCurrentPosition(
      // Success callback
      (position) => {
        const { latitude, longitude } = position.coords;
        setPosition({ lat: latitude, lng: longitude });
        setIsGeolocating(false);
        
        // Update parent
        onLocationChange(latitude, longitude);
      },
      
      // Error callback
      (error) => {
        console.error('Geolocation error:', error);
        setIsGeolocating(false);
        
        let errorMessage = 'Could not get your location. Please place the pin manually.';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location permission denied. Please enable location access in your browser settings.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information is unavailable. Please place the pin manually.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out. Please try again or place the pin manually.';
            break;
        }
        
        toast({
          title: 'Unable to get your location',
          description: errorMessage,
          variant: 'error',
        });
      },
      
      // Options
      GEOLOCATION_OPTIONS
    );
  };

  const handleMarkerDragEnd = (e: any) => {
    const { lat, lng } = e.target.getLatLng();
    setPosition({ lat, lng });
    onLocationChange(lat, lng);
  };

  // Update position when props change
  useEffect(() => {
    if (initialLocation) {
      setPosition(initialLocation);
    }
  }, [initialLocation]);

  return (
    <div className={`location-picker ${className}`}>
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">
            📍 Select Location
          </h3>
          
          <button
            type="button"
            onClick={handleUseMyLocation}
            disabled={isGeolocating}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isGeolocating ? (
              <>
                <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 border-t-transparent"></div>
                <span className="ml-2">Getting location...</span>
              </>
            ) : (
              <>
                🗺️ Use My Location
              </>
            )}
          </button>
        </div>

        {address && (
          <div className="text-sm text-gray-600 bg-gray-100 p-2 rounded">
            📍 {address}
          </div>
        )}
      </div>

      <div className="h-64 bg-gray-100 rounded-lg overflow-hidden border-2 border-gray-300">
        {isClient ? (
          <MapContainer
            center={[position.lat, position.lng]}
            zoom={13}
            className="h-full"
          >
            <MapPositionUpdater position={[position.lat, position.lng]} />
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            <Marker
              position={[position.lat, position.lng]}
              draggable={true}
              icon={createPickerIcon()}
              eventHandlers={{
                dragend: handleMarkerDragEnd,
              }}
            />
          </MapContainer>
        ) : (
          <div className="h-full p-4">
            <Skeleton className="h-full w-full" />
          </div>
        )}
      </div>

      <div className="mt-2 text-sm text-gray-600">
        <p>
          Drag the pin to the exact location, or click &quot;Use My Location&quot; for GPS.
        </p>
      </div>
    </div>
  );
};

export default LocationPicker;

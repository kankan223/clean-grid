/**
 * LocationPicker - CleanGrid Phase 1
 * Interactive mini-map with draggable pin for location selection
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { LatLngExpression } from 'leaflet';

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
  const [position, setPosition] = useState(initialLocation || { lat: 40.7128, lng: -74.0060 }); // NYC default
  const [isGeolocating, setIsGeolocating] = useState(false);
  const [address, setAddress] = useState<string>('');
  const mapRef = useRef<any>(null);

  // Handle GPS geolocation
  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
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
        onLocationChange({ lat: latitude, lng: longitude });
      },
      
      // Error callback
      (error) => {
        console.error('Geolocation error:', error);
        setIsGeolocating(false);
        alert('Could not get your location. Please place the pin manually.');
      },
      
      // Options
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
      }
    );
  };

  // Handle manual pin placement
  const handleMapClick = (e: any) => {
    const { lat, lng } = e.latlng;
    setPosition({ lat, lng });
    onLocationChange({ lat, lng });
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
        <MapContainer
          center={[position.lat, position.lng]}
          zoom={13}
          className="h-full"
          ref={mapRef}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          <Marker
            position={[position.lat, position.lng]}
            draggable={true}
            eventHandlers={{
              dragend: handleMapClick,
            }}
          >
            <div className="custom-marker">
              📍
            </div>
          </Marker>
        </MapContainer>
      </div>

      <div className="mt-2 text-sm text-gray-600">
        <p>
          Drag the pin to the exact location, or click "Use My Location" for GPS.
        </p>
      </div>
    </div>
  );
};

export default LocationPicker;

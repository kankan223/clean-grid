/**
 * SeverityMarker - CleanGrid Phase 1
 * Color-coded map markers based on incident severity
 */

'use client';

import { DivIcon } from 'react-leaflet';
import { IncidentSeverity } from '@/types/incident';

interface SeverityMarkerProps {
  incident: {
    id: string;
    severity?: string;
    location: {
      lat: number;
      lng: number;
    };
    status: string;
  };
}

const SeverityMarker: React.FC<SeverityMarkerProps> = ({ incident }) => {
  // Severity color mapping (per design.md)
  const severityColors = {
    [IncidentSeverity.HIGH]: '#dc2626',      // Red
    [IncidentSeverity.MEDIUM]: '#ea580c',   // Orange  
    [IncidentSeverity.LOW]: '#16a34a',     // Green
    [IncidentSeverity.NONE]: '#6b7280',    // Gray
  };

  const getSeverityColor = (severity?: string): string => {
    switch (severity) {
      case IncidentSeverity.HIGH:
        return severityColors[IncidentSeverity.HIGH];
      case IncidentSeverity.MEDIUM:
        return severityColors[IncidentSeverity.MEDIUM];
      case IncidentSeverity.LOW:
        return severityColors[IncidentSeverity.LOW];
      case IncidentSeverity.NONE:
        return severityColors[IncidentSeverity.NONE];
      default:
        return severityColors[IncidentSeverity.NONE]; // Default to gray
    }
  };

  const iconUrl = (severity?: string): string => {
    const color = getSeverityColor(severity);
    const svgIcon = `
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="32" viewBox="0 0 24 32">
        <circle cx="12" cy="16" r="10" fill="${color}" stroke="#fff" stroke-width="2"/>
        <circle cx="12" cy="8" r="3" fill="#fff"/>
      </svg>
    `;
    return `data:image/svg+xml;base64,${btoa(svgIcon)}`;
  };

  const createCustomIcon = (): DivIcon => {
    return new DivIcon({
      iconUrl: iconUrl(incident.severity),
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      className: `severity-marker severity-${incident.severity || 'none'}`,
    });
  };

  // Format popup content
  const formatPopupContent = (): string => {
    const severityBadge = incident.severity ? 
      `<span class="inline-block px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(incident.severity)} text-white">
        ${incident.severity.toUpperCase()}
      </span>` : '';

    const confidenceText = incident.severity && incident.severity !== IncidentSeverity.NONE ?
      `<div class="text-sm text-gray-600 mt-1">
        Confidence: <span class="font-medium">${Math.round((incident.confidence || 0) * 100)}%</span>
      </div>` : '';

    return `
      <div class="p-3 min-w-[200px]">
        <div class="font-medium text-gray-900 mb-2">${incident.status}</div>
        
        ${severityBadge}
        
        ${confidenceText}
        
        <div class="text-xs text-gray-500 mt-2">
          Reported: ${new Date(incident.created_at).toLocaleDateString()}
        </div>
        
        ${incident.address_text ? `
          <div class="text-xs text-gray-600 mt-1">
            📍 ${incident.address_text}
          </div>
        ` : ''}
        
        <div class="mt-2">
          <a 
            href="/incidents/${incident.id}" 
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View Details →
          </a>
        </div>
      </div>
    `;
  };

  if (!incident.location) {
    return null;
  }

  return (
    <>
      {createCustomIcon()}
    </>
  );
};

export default SeverityMarker;

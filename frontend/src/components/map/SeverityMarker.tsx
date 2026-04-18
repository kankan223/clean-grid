/**
 * SeverityMarker - CleanGrid Phase 1
 * Color-coded map markers based on incident severity
 */
'use client';

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
  const severityColors: Record<IncidentSeverity, string> = {
    [IncidentSeverity.HIGH]: '#dc2626',      // Red
    [IncidentSeverity.MEDIUM]: '#ea580c',   // Orange  
    [IncidentSeverity.LOW]: '#16a34a',     // Green
    [IncidentSeverity.NONE]: '#6b7280',    // Gray
  };

  const getSeverityColor = (severity?: string): string => {
    return severityColors[severity as IncidentSeverity || IncidentSeverity.NONE];
  };

  const color = getSeverityColor(incident.severity);
  
  return (
    <div
      style={{
        backgroundColor: color,
        color: 'white',
        borderRadius: '50%',
        width: '24px',
        height: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        fontSize: '12px',
      }}
      className={`severity-marker severity-${incident.severity || 'none'}`}
    >
      {incident.severity ? incident.severity.charAt(0).toUpperCase() : 'N'}
    </div>
  );
};

export default SeverityMarker;

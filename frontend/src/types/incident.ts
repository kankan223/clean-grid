/**
 * Incident types - CleanGrid Phase 1
 * Type definitions for incident data and severity levels
 */

export enum IncidentSeverity {
  NONE = 'None',
  LOW = 'Low',
  MEDIUM = 'Medium',
  HIGH = 'High'
}

export interface Incident {
  id: string;
  reporter_id?: string;
  assigned_to?: string;
  image_url: string;
  after_image_url?: string;
  location: {
    lat: number;
    lng: number;
  };
  address_text?: string;
  note?: string;
  waste_detected?: boolean;
  confidence?: number;
  severity?: string;
  bounding_boxes?: Array<{
    label: string;
    confidence: number;
    box: number[];
  }>;
  status: string;
  priority_score?: number;
  is_hotspot: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Report types - CleanGrid Phase 1
 * Type definitions for reporting functionality
 */

export interface ReportCreate {
  lat: number;
  lng: number;
  note?: string;
}

export interface ReportResponse {
  report_id: string;
  status: string;
  message: string;
}

export interface ReportListResponse {
  incidents: any[];
  total: number;
  offset: number;
  limit: number;
}

export interface Location {
  lat: number;
  lng: number;
}

export interface AIAnalysisResult {
  status: string;
  message?: string;
  incident_id?: string;
  waste_detected?: boolean;
  severity?: string;
  confidence?: number;
  error?: string;
}

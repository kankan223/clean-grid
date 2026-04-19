"use client";

import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface IncidentEvent {
  type: string;
  data: {
    incident_id: string;
    status: string;
    severity: string;
    location?: {
      lat: number;
      lng: number;
    };
  };
  timestamp: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useIncidentStream() {
  const queryClient = useQueryClient();
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const connect = useCallback(() => {
    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    
    try {
      const eventSource = new EventSource(`${API_BASE_URL}/api/events/incidents`, {
        withCredentials: true,
      });
      eventSourceRef.current = eventSource;
      
      eventSource.onopen = () => {
        console.log('SSE connection opened');
        // Clear any pending reconnect timeout
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };
      
      eventSource.onmessage = (event) => {
        try {
          const incidentEvent: IncidentEvent = JSON.parse(event.data);
          
          console.log('Received incident event:', incidentEvent);
          
          // Invalidate relevant queries to trigger refetch
          if (incidentEvent.type === 'incident_created' || incidentEvent.type === 'incident_updated') {
            queryClient.invalidateQueries({ queryKey: ['incidents'] });
            queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
            
            // Optional: Show toast notification
            if (incidentEvent.type === 'incident_created') {
              // You could integrate with a toast system here
              console.log('New incident reported:', incidentEvent.data.incident_id);
            }
          }
        } catch (error) {
          console.error('Error parsing SSE event:', error);
        }
      };
      
      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        eventSource.close();
        eventSourceRef.current = null;

        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        
        // Attempt to reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect SSE...');
          connect();
        }, 5000);
      };
      
    } catch (error) {
      console.error('Failed to create SSE connection:', error);

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      // Retry after 5 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 5000);
    }
  }, [queryClient]);
  
  useEffect(() => {
    // Start connection
    connect();
    
    // Cleanup on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);
  
  // Expose reconnect function for manual reconnection
  const reconnect = useCallback(() => {
    connect();
  }, [connect]);
  
  return { reconnect };
}

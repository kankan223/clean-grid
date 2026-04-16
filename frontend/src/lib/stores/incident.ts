import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Types
export interface Incident {
  id: string;
  status: string;
  severity: string;
  priority_score: number;
  location: {
    lat: number;
    lng: number;
  };
  created_at: string;
  age: string;
  reporter_name: string;
  assigned_to?: string;
  image_url?: string;
  ai_confidence?: number;
  note?: string;
}

export interface CrewMember {
  id: string;
  name: string;
  email: string;
  role: string;
  current_workload: number;
}

export interface IncidentFilters {
  status?: string;
  severity?: string;
  assigned_to?: string;
  sort: 'created_at' | 'priority_score' | 'severity';
  order: 'asc' | 'desc';
}

export interface IncidentState {
  // Data
  incidents: Incident[];
  crewMembers: CrewMember[];
  activeIncidentId: string | null;
  
  // Pagination
  currentPage: number;
  totalPages: number;
  total: number;
  limit: number;
  
  // Filtering
  filters: IncidentFilters;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  
  // Selection
  selectedIncidentIds: string[];
  
  // Actions
  setIncidents: (incidents: Incident[]) => void;
  setCrewMembers: (crew: CrewMember[]) => void;
  setActiveIncidentId: (id: string | null) => void;
  setCurrentPage: (page: number) => void;
  setFilters: (filters: Partial<IncidentFilters>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedIncidentIds: (ids: string[]) => void;
  toggleIncidentSelection: (id: string) => void;
  selectAllIncidents: () => void;
  clearSelection: () => void;
  assignIncident: (incidentId: string, crewId: string) => Promise<void>;
  refreshIncidents: () => Promise<void>;
}

// API Functions
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchIncidents(
  filters: IncidentFilters,
  page: number = 1,
  limit: number = 20
): Promise<{ incidents: Incident[]; total: number }> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: ((page - 1) * limit).toString(),
    sort: filters.sort,
    order: filters.order,
    ...(filters.status && { status: filters.status }),
    ...(filters.severity && { severity: filters.severity }),
    ...(filters.assigned_to && { assigned_to: filters.assigned_to }),
  });

  const response = await fetch(`${API_BASE}/api/admin/incidents?${params}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Include cookies for auth
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch incidents: ${response.statusText}`);
  }

  return response.json();
}

async function fetchCrewMembers(): Promise<CrewMember[]> {
  const response = await fetch(`${API_BASE}/api/admin/users?role=crew`, {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch crew members: ${response.statusText}`);
  }

  const data = await response.json();
  return data.crew;
}

async function assignIncident(incidentId: string, crewId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/admin/incidents/${incidentId}/assign`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ assigned_to: crewId }),
  });

  if (!response.ok) {
    throw new Error(`Failed to assign incident: ${response.statusText}`);
  }
}

// Store
export const useIncidentStore = create<IncidentState>()(
  devtools(
    (set, get) => ({
      // Initial State
      incidents: [],
      crewMembers: [],
      activeIncidentId: null,
      currentPage: 1,
      totalPages: 1,
      total: 0,
      limit: 20,
      filters: {
        sort: 'created_at',
        order: 'desc',
      },
      isLoading: false,
      error: null,
      selectedIncidentIds: [],

      // Actions
      setIncidents: (incidents) => set({ incidents }),
      
      setCrewMembers: (crewMembers) => set({ crewMembers }),
      
      setActiveIncidentId: (id) => set({ activeIncidentId: id }),
      
      setCurrentPage: (page) => set({ currentPage: page }),
      
      setFilters: (newFilters) => set((state) => ({
        filters: { ...state.filters, ...newFilters },
        currentPage: 1, // Reset to first page when filters change
      })),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      setError: (error) => set({ error }),
      
      setSelectedIncidentIds: (ids) => set({ selectedIncidentIds: ids }),
      
      toggleIncidentSelection: (id) => set((state) => ({
        selectedIncidentIds: state.selectedIncidentIds.includes(id)
          ? state.selectedIncidentIds.filter((selectedId) => selectedId !== id)
          : [...state.selectedIncidentIds, id],
      })),
      
      selectAllIncidents: () => set((state) => ({
        selectedIncidentIds: state.incidents.map((incident) => incident.id),
      })),
      
      clearSelection: () => set({ selectedIncidentIds: [] }),
      
      assignIncident: async (incidentId, crewId) => {
        try {
          set({ isLoading: true, error: null });
          
          // Optimistic update
          set((state) => ({
            incidents: state.incidents.map((incident) =>
              incident.id === incidentId
                ? {
                    ...incident,
                    assigned_to: crewId,
                    status: 'Assigned',
                  }
                : incident
            ),
          }));
          
          await assignIncident(incidentId, crewId);
          
          // Refresh data to get latest state
          await get().refreshIncidents();
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Assignment failed' });
          // Revert optimistic update on error
          await get().refreshIncidents();
        } finally {
          set({ isLoading: false });
        }
      },
      
      refreshIncidents: async () => {
        try {
          set({ isLoading: true, error: null });
          const { filters, currentPage, limit } = get();
          const data = await fetchIncidents(filters, currentPage, limit);
          
          set((state) => ({
            incidents: data.incidents,
            total: data.total,
            totalPages: Math.ceil(data.total / limit),
            isLoading: false,
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to refresh incidents',
            isLoading: false,
          });
        }
      },
    }),
    {
      name: 'incident-store',
    }
  )
);

// Initial data loading
export const initializeIncidentStore = async () => {
  const store = useIncidentStore.getState();
  
  // Load crew members
  try {
    const crew = await fetchCrewMembers();
    store.setCrewMembers(crew);
  } catch (error) {
    console.error('Failed to load crew members:', error);
  }
  
  // Load initial incidents
  await store.refreshIncidents();
};

'use client';

import { useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/lib/stores/auth';
import { useIncidentStore, initializeIncidentStore, Incident } from '@/lib/stores/incident';
import { IncidentTable } from '@/components/admin/IncidentTable';
import { DetailDrawer } from '@/components/admin/DetailDrawer';
import { AdminMapPanel } from '@/components/admin/AdminMapPanel';
import { useIncidentStream } from '@/hooks/useIncidentStream';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RefreshCw, Filter } from 'lucide-react';

interface AdminStats {
  active: number;
  inProgress: number;
  verifiedToday: number;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const queryClient = useQueryClient();
  
  // Initialize SSE for real-time updates
  useIncidentStream();
  
  // Initialize incident store
  useEffect(() => {
    initializeIncidentStore();
  }, []);

  // TanStack Query for incidents
  const {
    data: incidents = [],
    isLoading: incidentsLoading,
    error: incidentsError,
    refetch: refetchIncidents
  } = useQuery({
    queryKey: ['incidents'],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004';
      const response = await fetch(`${apiUrl}/api/incidents?limit=100`, {
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch incidents');
      }
      
      const data = await response.json();
      return data.incidents || [];
    },
    refetchInterval: 30000, // Poll every 30 seconds as fallback
  });
  
  // TanStack Query for admin stats
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    refetch: refetchStats
  } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004';
      const response = await fetch(`${apiUrl}/api/incidents/stats`, {
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch stats');
      }
      
      const data = await response.json();
      return data;
    },
    refetchInterval: 30000, // Poll every 30 seconds as fallback
  });
  
  // Mutation for updating incident status
  const updateIncidentMutation = useMutation({
    mutationFn: async ({ incidentId, status }: { incidentId: string; status: string }) => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004';
      const response = await fetch(`${apiUrl}/api/admin/incidents/${incidentId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update incident status');
      }
      
      return response.json();
    },
    onSuccess: () => {
      // Invalidate queries to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] });
    },
  });
  
  const {
    setActiveIncidentId,
    activeIncidentId,
  } = useIncidentStore();

  const handleRowClick = (incident: Incident) => {
    setSelectedIncident(incident);
    setActiveIncidentId(incident.id);
    setIsDrawerOpen(true);
  };

  const handleDrawerClose = () => {
    setIsDrawerOpen(false);
    setSelectedIncident(null);
    setActiveIncidentId(null);
  };

  const handleRefresh = async () => {
    await Promise.all([
      refetchIncidents(),
      refetchStats()
    ]);
  };

  return (
    <div className="admin-dashboard h-screen flex flex-col">
      {/* Admin Stats Bar */}
      <Card className="relative z-40 m-4">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-xl font-bold">Admin Dashboard</CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={incidentsLoading || statsLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${(incidentsLoading || statsLoading) ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </CardHeader>
        <CardContent>
          {stats ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="text-2xl font-bold text-blue-600">{stats.active || 0}</div>
                <div className="text-sm text-gray-600">Active</div>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <div className="text-2xl font-bold text-yellow-600">{stats.inProgress || 0}</div>
                <div className="text-sm text-gray-600">In Progress</div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="text-2xl font-bold text-green-600">{stats.verified || 0}</div>
                <div className="text-sm text-gray-600">Verified Today</div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 border-t-transparent"></div>
              <p className="mt-4 text-gray-600">Loading admin stats...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main Content Area - Split Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Incidents Table */}
        <div className="w-3/5 p-4 overflow-hidden">
          {/* Error State */}
          {incidentsError && (
            <Card className="relative z-40 border-red-200 bg-red-50 mb-4">
              <CardContent className="pt-6">
                <div className="flex items-center text-red-800">
                  <Filter className="h-4 w-4 mr-2" />
                  <span>Error: {incidentsError.message}</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefresh}
                  className="mt-2"
                >
                  Retry
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Incidents Table */}
          <Card className="relative z-30 h-full">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Incident Management</CardTitle>
            </CardHeader>
            <CardContent className="p-0 h-full overflow-hidden">
              <IncidentTable 
                incidents={incidents}
                isLoading={incidentsLoading}
                onRowClick={handleRowClick}
                onStatusUpdate={(incidentId, status) => updateIncidentMutation.mutate({ incidentId, status })}
              />
            </CardContent>
          </Card>
        </div>
        
        {/* Right Panel - Synchronized Map */}
        <div className="w-2/5 p-4 pl-0">
          <Card className="relative z-30 h-full">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold">Live Map View</CardTitle>
            </CardHeader>
            <CardContent className="p-0 h-full">
              <AdminMapPanel className="h-full" incidents={incidents} />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Detail Drawer */}
      <DetailDrawer
        incident={selectedIncident}
        isOpen={isDrawerOpen}
        onClose={handleDrawerClose}
      />
    </div>
  );
}

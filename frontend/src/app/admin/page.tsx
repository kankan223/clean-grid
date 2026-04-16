'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/stores/auth';
import { useIncidentStore, initializeIncidentStore, Incident } from '@/lib/stores/incident';
import { IncidentTable } from '@/components/admin/IncidentTable';
import { DetailDrawer } from '@/components/admin/DetailDrawer';
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
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const {
    incidents,
    isLoading,
    error,
    refreshIncidents,
    setActiveIncidentId,
    activeIncidentId,
  } = useIncidentStore();

  useEffect(() => {
    // Initialize store and load data
    initializeIncidentStore();
    fetchAdminStats();
  }, []);

  const fetchAdminStats = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/stats`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch admin stats:', error);
    }
  };

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
    await fetchAdminStats();
    await refreshIncidents();
  };

  return (
    <div className="space-y-6">
      {/* Admin Stats Bar */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-xl font-bold">Admin Dashboard</CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </CardHeader>
        <CardContent>
          {stats ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="text-2xl font-bold text-blue-600">{stats.active}</div>
                <div className="text-sm text-gray-600">Active</div>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <div className="text-2xl font-bold text-yellow-600">{stats.inProgress}</div>
                <div className="text-sm text-gray-600">In Progress</div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="text-2xl font-bold text-green-600">{stats.verifiedToday}</div>
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

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center text-red-800">
              <Filter className="h-4 w-4 mr-2" />
              <span>Error: {error}</span>
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
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Incident Management</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <IncidentTable onRowClick={handleRowClick} />
        </CardContent>
      </Card>

      {/* Detail Drawer */}
      <DetailDrawer
        incident={selectedIncident}
        isOpen={isDrawerOpen}
        onClose={handleDrawerClose}
      />
    </div>
  );
}

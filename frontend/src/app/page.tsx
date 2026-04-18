"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, MapPin, Users, TrendingUp, Loader2 } from "lucide-react";
import { ReportWasteFAB } from "@/components/map/ReportWasteFAB";

// Dynamic import with SSR disabled for Leaflet
const IncidentMap = dynamic(
  () => import("@/components/map/IncidentMap"),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading map...</p>
        </div>
      </div>
    )
  }
);

interface Incident {
  id: string;
  lat: number;
  lng: number;
  severity: 'Low' | 'Medium' | 'High' | 'None';
  status: 'Pending' | 'Assigned' | 'InProgress' | 'Cleaned' | 'Verified' | 'NeedsReview';
  imageUrl: string;
  createdAt: string;
  address?: string;
  reporterName?: string;
}

interface DashboardStats {
  total: number;
  pending: number;
  assigned: number;
  inProgress: number;
  cleaned: number;
  verified: number;
}

export default function Home() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchIncidents();
    fetchStats();
    
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      fetchIncidents();
      fetchStats();
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const fetchIncidents = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004'}/api/incidents?status=active&limit=100`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setIncidents(data.incidents || []);
      } else if (response.status !== 401) {
        setError('Failed to load incidents');
      }
    } catch (err) {
      setError('Failed to load incidents');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004'}/api/incidents/stats`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      // Stats are optional, don't show error
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'High': return 'bg-red-100 text-red-800 border-red-200';
      case 'Medium': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Assigned': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'InProgress': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'Cleaned': return 'bg-green-100 text-green-800 border-green-200';
      case 'Verified': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'NeedsReview': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading && incidents.length === 0) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading CleanGrid...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-[calc(100vh-4rem)]">
      {/* Map Container */}
      <div className="h-full">
        <IncidentMap 
          incidents={incidents}
          center={[40.7128, -74.0060]} // Default to NYC
          zoom={12}
        />
      </div>

      {/* Report Waste FAB */}
      <ReportWasteFAB />

      {/* Stats Overlay */}
      {stats && (
        <div className="absolute top-4 left-4 z-30">
          <Card className="bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Live Statistics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                  <span className="font-medium">{stats.pending}</span>
                  <span className="text-muted-foreground">Pending</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-blue-500" />
                  <span className="font-medium">{stats.assigned}</span>
                  <span className="text-muted-foreground">Assigned</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-purple-500" />
                  <span className="font-medium">{stats.inProgress}</span>
                  <span className="text-muted-foreground">In Progress</span>
                </div>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="font-medium">{stats.verified}</span>
                  <span className="text-muted-foreground">Verified</span>
                </div>
              </div>
              <div className="pt-2 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Total Reports</span>
                  <Badge variant="secondary">{stats.total}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="absolute top-4 right-4 z-30">
          <Card className="bg-destructive/10 border-destructive/20">
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm">{error}</span>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-2"
                onClick={fetchIncidents}
              >
                Retry
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Empty State */}
      {!loading && incidents.length === 0 && !error && (
        <div className="absolute inset-0 flex items-center justify-center z-30">
          <Card className="max-w-md mx-4">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center gap-2">
                <MapPin className="h-6 w-6" />
                No Active Incidents
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-4">
              <p className="text-muted-foreground">
                Be the first to report waste in your area and help keep our community clean!
              </p>
              <Link href="/report" className="w-full">
                <Button className="w-full">
                  <MapPin className="h-4 w-4 mr-2" />
                  Report Waste
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

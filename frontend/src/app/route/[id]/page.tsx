"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import RouteMap from "@/components/route/RouteMap";
import StopListPanel from "@/components/route/StopListPanel";

interface Route {
  id: string;
  crew_id: string;
  crew: {
    id: string;
    email: string;
    display_name: string;
    role: string;
  };
  status: string;
  total_distance_meters: number;
  total_duration_seconds: number;
  optimization_method: string;
  polyline: string | null;
  metadata_json: string | null;
  stops: Array<{
    id: string;
    incident_id: string;
    stop_order: number;
    status: string;
    estimated_arrival: string | null;
    actual_arrival: string | null;
    notes: string | null;
    incident: {
      id: string;
      location: { lat: number; lon: number } | null;
      severity: string | null;
      status: string;
      address_text: string | null;
      created_at: string;
    };
  }>;
  created_at: string;
  updated_at: string;
}

const fetchRoute = async (routeId: string): Promise<Route> => {
  const response = await fetch(`/api/routes/${routeId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch route: ${response.statusText}`);
  }
  return response.json();
};

const formatDistance = (meters: number): string => {
  if (meters < 1000) {
    return `${meters}m`;
  }
  return `${(meters / 1000).toFixed(1)}km`;
};

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
};

const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'bg-gray-100 text-gray-800';
    case 'active':
      return 'bg-blue-100 text-blue-800';
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'cancelled':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export default function RouteDetailPage() {
  const params = useParams();
  const routeId = params.id as string;

  const {
    data: route,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["route", routeId],
    queryFn: () => fetchRoute(routeId),
    enabled: !!routeId,
  });

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Route Details</h1>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Route Map Skeleton */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Route Map</CardTitle>
              </CardHeader>
              <CardContent className="h-96">
                <Skeleton className="h-full w-full" />
              </CardContent>
            </Card>
          </div>

          {/* Stop List Skeleton */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Route Stops</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="border rounded-lg p-4">
                      <Skeleton className="h-4 w-16 mb-3" />
                      <div className="space-y-2">
                        <Skeleton className="h-3 w-full" />
                        <Skeleton className="h-3 w-3/4" />
                        <Skeleton className="h-3 w-1/4" />
                      </div>
                      <Skeleton className="h-3 w-full" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Route Details</h1>
        </div>
        
        <Alert variant="destructive">
          <AlertDescription>
            Failed to load route: {error instanceof Error ? error.message : 'Unknown error'}
          </AlertDescription>
        </Alert>
        
        <div className="mt-4">
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (!route) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Route Not Found</h1>
        </div>
        
        <Alert variant="destructive">
          <AlertDescription>
            The requested route could not be found.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Route Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Route Details</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Route ID</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-mono text-sm">{route.id.slice(0, 8)}...</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Status</CardTitle>
            </CardHeader>
            <CardContent>
              <Badge className={getStatusColor(route.status)}>
                {route.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Assigned Crew</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <p className="font-medium">{route.crew.display_name}</p>
                <p className="text-sm text-gray-600">{route.crew.email}</p>
                <Badge variant="outline" className="mt-1">
                  {route.crew.role}
                </Badge>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Distance & Duration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-600">Distance:</span>
                  <span className="font-medium">{formatDistance(route.total_distance_meters)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Duration:</span>
                  <span className="font-medium">{formatDuration(route.total_duration_seconds)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Method:</span>
                  <Badge variant="secondary" className="text-xs">
                    {route.optimization_method.toUpperCase()}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Route Map and Stops */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Route Map */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Route Map</CardTitle>
              <CardHeader>
                <div className="flex items-center space-x-2 text-sm">
                  <Badge className={getStatusColor(route.status)}>
                    {route.stops.length} stops
                  </Badge>
                  {route.polyline && (
                    <Badge variant="secondary" className="text-xs">
                      Has Polyline
                    </Badge>
                  )}
                </div>
              </CardHeader>
            </CardHeader>
            <CardContent className="p-0">
              <RouteMap route={route} className="h-96" />
            </CardContent>
          </Card>
        </div>

        {/* Stop List */}
        <div className="lg:col-span-1">
          <StopListPanel stops={route.stops} />
        </div>
      </div>

      {/* Route Actions */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Route Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4">
              {route.status === 'pending' && (
                <Button onClick={() => {
                  // TODO: Implement start route action
                  console.log('Start route:', route.id);
                }}>
                  Start Route
                </Button>
              )}
              
              {route.status === 'active' && (
                <Button 
                  variant="outline"
                  onClick={() => {
                    // TODO: Implement complete route action
                    console.log('Complete route:', route.id);
                  }}
                >
                  Complete Route
                </Button>
              )}
              
              <Button 
                variant="outline"
                onClick={() => {
                  // TODO: Implement export route action
                  console.log('Export route:', route.id);
                }}
              >
                Export
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

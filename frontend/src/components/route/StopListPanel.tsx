"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface Stop {
  id: string;
  stop_order: number;
  status: string;
  estimated_arrival: string | null;
  actual_arrival: string | null;
  notes: string | null;
  incident: {
    id: string;
    severity: string | null;
    status: string;
    address_text: string | null;
    created_at: string;
  };
}

interface StopListPanelProps {
  stops: Stop[];
  className?: string;
}

const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'pending':
      return 'bg-gray-100 text-gray-800';
    case 'in_progress':
      return 'bg-blue-100 text-blue-800';
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'skipped':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getSeverityColor = (severity: string | null): string => {
  switch (severity?.toLowerCase()) {
    case 'high':
      return 'bg-red-100 text-red-800';
    case 'medium':
      return 'bg-orange-100 text-orange-800';
    case 'low':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

function StopListPanel({ stops, className }: StopListPanelProps) {
  const formatTime = (timeString: string | null): string => {
    if (!timeString) return 'Not scheduled';
    return new Date(timeString).toLocaleString();
  };

  if (!stops || stops.length === 0) {
    return (
      <Card className={`w-full ${className || ""}`}>
        <CardHeader>
          <CardTitle>Route Stops</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-gray-500 py-8">
            No stops available for this route
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`w-full ${className || ""}`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Route Stops</span>
          <Badge variant="secondary">{stops.length} stops</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {stops.map((stop) => (
            <div
              key={stop.id}
              className="border rounded-lg p-4 space-y-3 hover:bg-gray-50 transition-colors"
            >
              {/* Stop Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-10 h-10 bg-blue-500 text-white rounded-full font-bold">
                    {stop.stop_order}
                  </div>
                  <div>
                    <h4 className="font-semibold">Stop #{stop.stop_order}</h4>
                    <Badge className={getStatusColor(stop.status)}>
                      {stop.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  ID: {stop.id.slice(0, 8)}...
                </div>
              </div>

              {/* Incident Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h5 className="font-medium mb-2">Incident Details</h5>
                  <div className="space-y-1">
                    <div>
                      <span className="text-gray-600">Status:</span>
                      <span className="ml-2">{stop.incident.status}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Severity:</span>
                      <span className="ml-2">
                        <Badge className={getSeverityColor(stop.incident.severity)}>
                          {stop.incident.severity || 'Unknown'}
                        </Badge>
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Address:</span>
                      <span className="ml-2">{stop.incident.address_text || 'No address'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Reported:</span>
                      <span className="ml-2">
                        {new Date(stop.incident.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Timing Information */}
                <div>
                  <h5 className="font-medium mb-2">Timing</h5>
                  <div className="space-y-1">
                    <div>
                      <span className="text-gray-600">Estimated Arrival:</span>
                      <span className="ml-2">{formatTime(stop.estimated_arrival)}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Actual Arrival:</span>
                      <span className="ml-2">{formatTime(stop.actual_arrival)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Notes */}
              {stop.notes && (
                <div className="border-t pt-3">
                  <h5 className="font-medium mb-2">Notes</h5>
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                    {stop.notes}
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="border-t pt-3">
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      // TODO: Implement mark as complete action
                      console.log('Mark stop as complete:', stop.id);
                    }}
                  >
                    Mark Complete
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      // TODO: Implement add notes action
                      console.log('Add notes for stop:', stop.id);
                    }}
                  >
                    Add Notes
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default StopListPanel;

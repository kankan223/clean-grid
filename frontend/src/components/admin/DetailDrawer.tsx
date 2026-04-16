"use client";

import React, { useEffect, useState } from 'react';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from '@/components/ui/drawer';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { X, MapPin, Clock, User, AlertTriangle } from 'lucide-react';
import { useIncidentStore, Incident, CrewMember } from '@/lib/stores/incident';

interface DetailDrawerProps {
  incident: Incident | null;
  isOpen: boolean;
  onClose: () => void;
}

// Status Timeline Component
const StatusTimeline = ({ status, created_at, updated_at }: {
  status: string;
  created_at: string;
  updated_at: string;
}) => {
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      Pending: 'bg-gray-100 text-gray-800',
      Assigned: 'bg-blue-100 text-blue-800',
      'In Progress': 'bg-yellow-100 text-yellow-800',
      Cleaned: 'bg-green-100 text-green-800',
      Verified: 'bg-emerald-100 text-emerald-800',
      'Needs Review': 'bg-red-100 text-red-800',
    };
    return colors[status] || colors.Pending;
  };

  return (
    <div className="flex items-start gap-3">
      <div className={`w-3 h-3 rounded-full mt-1 ${getStatusColor(status).split(' ')[0]}`} />
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-medium">{status}</span>
          <span className="text-sm text-gray-500">
            {new Date(updated_at).toLocaleDateString()}
          </span>
        </div>
        <div className="text-xs text-gray-500">
          {new Date(created_at).toLocaleString()}
        </div>
      </div>
    </div>
  );
};

// Severity Badge Component (reused from table)
const SeverityBadge = ({ severity }: { severity: string }) => {
  const variants: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; color: string }> = {
    High: { variant: 'destructive', color: 'text-red-600' },
    Medium: { variant: 'default', color: 'text-orange-600' },
    Low: { variant: 'secondary', color: 'text-green-600' },
    None: { variant: 'outline', color: 'text-gray-600' },
  };

  const config = variants[severity] || variants.None;

  return (
    <Badge variant={config.variant} className={config.color}>
      {severity || 'None'}
    </Badge>
  );
};

export const DetailDrawer: React.FC<DetailDrawerProps> = ({
  incident,
  isOpen,
  onClose,
}) => {
  const { crewMembers, assignIncident, isLoading } = useIncidentStore();
  const [selectedCrewId, setSelectedCrewId] = useState<string>('');
  const [isAssigning, setIsAssigning] = useState(false);

  useEffect(() => {
    if (incident) {
      setSelectedCrewId(incident.assigned_to || '');
    }
  }, [incident]);

  const handleAssign = async () => {
    if (!incident || !selectedCrewId) return;

    setIsAssigning(true);
    try {
      await assignIncident(incident.id, selectedCrewId);
      onClose();
    } catch (error) {
      console.error('Assignment failed:', error);
    } finally {
      setIsAssigning(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!incident) return;
    // TODO: Implement status change API call
    console.log('Status change:', newStatus);
  };

  if (!incident) return null;

  return (
    <Drawer open={isOpen} onOpenChange={onClose}>
      <DrawerContent className="w-[480px]">
        <DrawerHeader className="flex items-center justify-between">
          <DrawerTitle>Incident Details</DrawerTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        </DrawerHeader>

        <div className="flex flex-col h-full overflow-y-auto">
          {/* Before Image */}
          {incident.image_url && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Before Image</h3>
              <div className="relative rounded-lg overflow-hidden border">
                <img
                  src={incident.image_url}
                  alt="Incident"
                  className="w-full h-64 object-cover"
                />
                {incident.ai_confidence && (
                  <div className="absolute top-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-xs">
                    {Math.round(incident.ai_confidence * 100)}% confidence
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="space-y-4 mb-6">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-gray-500" />
              <span className="text-sm">
                {incident.location.lat.toFixed(6)}, {incident.location.lng.toFixed(6)}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-gray-500" />
              <span className="text-sm">
                Reported {new Date(incident.created_at).toLocaleString()}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-gray-500" />
              <span className="text-sm">{incident.reporter_name}</span>
            </div>

            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-gray-500" />
              <SeverityBadge severity={incident.severity || 'None'} />
              <span className="text-sm text-gray-600">
                Priority: {incident.priority_score || 0}
              </span>
            </div>

            {incident.note && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Note</h4>
                <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                  {incident.note}
                </p>
              </div>
            )}
          </div>

          <Separator />

          {/* Status Timeline */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Status Timeline</h3>
            <div className="space-y-3">
              <StatusTimeline
                status={incident.status}
                created_at={incident.created_at}
                updated_at={incident.updated_at || incident.created_at}
              />
            </div>
          </div>

          <Separator />

          {/* Assignment Section */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Assignment</h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-700">Assign to Crew Member</label>
                <Select value={selectedCrewId} onValueChange={setSelectedCrewId}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select crew member..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Unassigned</SelectItem>
                    {crewMembers.map((crew) => (
                      <SelectItem key={crew.id} value={crew.id}>
                        <div className="flex items-center justify-between w-full">
                          <span>{crew.name}</span>
                          <Badge variant="outline" className="ml-2">
                            {crew.current_workload} active
                          </Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={handleAssign}
                disabled={!selectedCrewId || isAssigning || isLoading}
                className="w-full"
              >
                {isAssigning ? 'Assigning...' : 'Assign Incident'}
              </Button>
            </div>
          </div>

          {/* Status Actions */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Status Actions</h3>
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleStatusChange('In Progress')}
                disabled={incident.status === 'In Progress'}
              >
                Mark In Progress
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleStatusChange('Cleaned')}
                disabled={incident.status === 'Cleaned'}
              >
                Mark Cleaned
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleStatusChange('Verified')}
                disabled={incident.status === 'Verified'}
              >
                Mark Verified
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleStatusChange('Needs Review')}
                disabled={incident.status === 'Needs Review'}
              >
                Needs Review
              </Button>
            </div>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
};

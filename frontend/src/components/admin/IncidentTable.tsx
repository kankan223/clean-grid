"use client";

import React, { useEffect, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { ArrowUpDown, ArrowUp, ArrowDown, MoreHorizontal } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useIncidentStore, Incident } from '@/lib/stores/incident';

// Severity Badge Component
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

// Status Pill Component
const StatusPill = ({ status }: { status: string }) => {
  const variants: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; color: string }> = {
    Pending: { variant: 'outline', color: 'text-gray-600' },
    Assigned: { variant: 'default', color: 'text-blue-600' },
    'In Progress': { variant: 'default', color: 'text-yellow-600' },
    Cleaned: { variant: 'secondary', color: 'text-green-600' },
    Verified: { variant: 'secondary', color: 'text-emerald-600' },
    'Needs Review': { variant: 'destructive', color: 'text-red-600' },
  };

  const config = variants[status] || variants.Pending;

  return (
    <Badge variant={config.variant} className={config.color}>
      {status}
    </Badge>
  );
};

// Priority Score Component
const PriorityScore = ({ score }: { score: number }) => {
  const getColor = (score: number) => {
    if (score >= 80) return 'text-red-600 font-bold';
    if (score >= 60) return 'text-orange-600 font-semibold';
    if (score >= 40) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <span className={`text-sm ${getColor(score)}`}>
      {score}
    </span>
  );
};

// Sort Icon Component
const SortIcon = ({ column, currentSort, currentOrder }: {
  column: string;
  currentSort: string;
  currentOrder: 'asc' | 'desc';
}) => {
  if (currentSort !== column) {
    return <ArrowUpDown className="h-4 w-4" />;
  }
  return currentOrder === 'asc' ? (
    <ArrowUp className="h-4 w-4" />
  ) : (
    <ArrowDown className="h-4 w-4" />
  );
};

interface IncidentTableProps {
  incidents?: Incident[];
  isLoading?: boolean;
  onRowClick?: (incident: Incident) => void;
  onStatusUpdate?: (incidentId: string, status: string) => void;
}

export const IncidentTable: React.FC<IncidentTableProps> = ({ 
  incidents = [], 
  isLoading = false, 
  onRowClick, 
  onStatusUpdate 
}) => {
  const {
    crewMembers,
    selectedIncidentIds,
    filters,
    setFilters,
    setSelectedIncidentIds,
    toggleIncidentSelection,
    clearSelection,
    refreshIncidents,
  } = useIncidentStore();
  const [activeIncidentId, setActiveIncidentId] = useState<string | null>(null);
  const [sortField, setSortField] = useState<'created_at' | 'priority_score' | 'severity'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const allSelected = incidents.length > 0 && incidents.every((incident) => selectedIncidentIds.includes(incident.id));

  const handleSort = (column: 'created_at' | 'priority_score' | 'severity') => {
    const newOrder = sortOrder === 'desc' ? 'asc' : 'desc';
    setSortField(column);
    setSortOrder(newOrder);
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIncidentIds(incidents.map((incident) => incident.id));
    } else {
      clearSelection();
    }
  };

  const handleRowClick = (incident: Incident) => {
    setActiveIncidentId(incident.id);
    if (onRowClick) {
      onRowClick(incident);
    }
  };

  const getCrewMemberName = (crewId: string) => {
    const crew = crewMembers.find(member => member.id === crewId);
    return crew ? crew.name : 'Unassigned';
  };

  if (isLoading && incidents.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Bulk Actions Bar */}
      {selectedIncidentIds.length > 0 && (
        <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border">
          <span className="text-sm text-gray-600">
            {selectedIncidentIds.length} selected
          </span>
          <Button variant="outline" size="sm">
            Generate Route
          </Button>
          <Button variant="outline" size="sm">
            Assign All
          </Button>
          <Button variant="outline" size="sm">
            Change Status
          </Button>
        </div>
      )}

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">
                <Checkbox
                  checked={allSelected}
                  onCheckedChange={handleSelectAll}
                  aria-label="Select all"
                />
              </TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort('priority_score')}
              >
                <div className="flex items-center gap-2">
                  Priority
                  <SortIcon 
                    column="priority_score" 
                    currentSort={filters.sort} 
                    currentOrder={filters.order} 
                  />
                </div>
              </TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort('severity')}
              >
                <div className="flex items-center gap-2">
                  Severity
                  <SortIcon 
                    column="severity" 
                    currentSort={filters.sort} 
                    currentOrder={filters.order} 
                  />
                </div>
              </TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Reporter</TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort('created_at')}
              >
                <div className="flex items-center gap-2">
                  Age
                  <SortIcon 
                    column="created_at" 
                    currentSort={filters.sort} 
                    currentOrder={filters.order} 
                  />
                </div>
              </TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Assigned To</TableHead>
              <TableHead className="w-12">
                <span className="sr-only">Actions</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {incidents.map((incident) => (
              <TableRow
                key={incident.id}
                className={`cursor-pointer hover:bg-gray-50 ${
                  activeIncidentId === incident.id ? 'bg-blue-50' : ''
                }`}
                onClick={() => handleRowClick(incident)}
              >
                <TableCell>
                  <Checkbox
                    checked={selectedIncidentIds.includes(incident.id)}
                    onCheckedChange={() => toggleIncidentSelection(incident.id)}
                    onClick={(e) => e.stopPropagation()}
                    aria-label={`Select incident ${incident.id}`}
                  />
                </TableCell>
                <TableCell>
                  <PriorityScore score={incident.priority_score || 0} />
                </TableCell>
                <TableCell>
                  <SeverityBadge severity={incident.severity || 'None'} />
                </TableCell>
                <TableCell>
                  <div className="text-sm text-gray-600">
                    {incident.location.lat.toFixed(4)}, {incident.location.lng.toFixed(4)}
                  </div>
                </TableCell>
                <TableCell className="text-sm">
                  {incident.reporter_name}
                </TableCell>
                <TableCell className="text-sm text-gray-600">
                  {incident.age}
                </TableCell>
                <TableCell>
                  {onStatusUpdate ? (
                    <select
                      value={incident.status}
                      onChange={(e) => onStatusUpdate(incident.id, e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      className="text-sm border rounded px-2 py-1"
                    >
                      <option value="pending">Pending</option>
                      <option value="assigned">Assigned</option>
                      <option value="in_progress">In Progress</option>
                      <option value="cleaned">Cleaned</option>
                      <option value="verified">Verified</option>
                      <option value="needs_review">Needs Review</option>
                    </select>
                  ) : (
                    <StatusPill status={incident.status} />
                  )}
                </TableCell>
                <TableCell className="text-sm">
                  {incident.assigned_to ? getCrewMemberName(incident.assigned_to) : 'Unassigned'}
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger>
                      <Button
                        variant="ghost"
                        className="h-8 w-8 p-0"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>View Details</DropdownMenuItem>
                      <DropdownMenuItem>Edit</DropdownMenuItem>
                      <DropdownMenuItem>Delete</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Empty State */}
      {!isLoading && incidents.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No incidents found</p>
          <p className="text-gray-400 text-sm mt-2">
            Try adjusting your filters or check back later.
          </p>
        </div>
      )}
    </div>
  );
};

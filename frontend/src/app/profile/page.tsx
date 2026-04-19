"use client";

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, User, Award, MapPin, Calendar, CheckCircle, Clock, XCircle } from 'lucide-react';
import Link from 'next/link';

interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  role: string;
  total_points: number;
  badge_tier?: string;
  created_at: string;
}

interface UserReport {
  id: string;
  status: string;
  severity: string;
  created_at: string;
  location: {
    lat: number;
    lng: number;
  };
  note?: string;
  image_url?: string;
}

const StatusBadge = ({ status }: { status: string }) => {
  const variants: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; color: string; icon: React.ComponentType<{ className?: string }> }> = {
    pending: { variant: 'outline', color: 'text-gray-600', icon: Clock },
    assigned: { variant: 'default', color: 'text-blue-600', icon: Calendar },
    in_progress: { variant: 'default', color: 'text-yellow-600', icon: Clock },
    cleaned: { variant: 'secondary', color: 'text-green-600', icon: CheckCircle },
    verified: { variant: 'secondary', color: 'text-emerald-600', icon: CheckCircle },
    needs_review: { variant: 'destructive', color: 'text-red-600', icon: XCircle },
  };

  const config = variants[status] || variants.pending;
  const Icon = config.icon;

  return (
    <div className="flex items-center space-x-1">
      <Icon className="h-3 w-3" />
      <Badge variant={config.variant} className={config.color}>
        {status.replace('_', ' ')}
      </Badge>
    </div>
  );
};

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

export default function ProfilePage() {
  const {
    data: user,
    isLoading: userLoading,
    error: userError
  } = useQuery<UserProfile>({
    queryKey: ['user-profile'],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/users/me`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user profile');
      }

      return response.json();
    },
  });

  const {
    data: reports = [],
    isLoading: reportsLoading,
    error: reportsError
  } = useQuery<UserReport[]>({
    queryKey: ['user-reports'],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/users/me/reports`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user reports');
      }

      const data = await response.json();
      return data.reports || [];
    },
  });

  if (userLoading || reportsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto" />
          <p className="mt-2">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (userError || reportsError) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-red-600">Error loading profile</p>
              <p className="text-sm text-gray-600 mt-2">
                {userError?.message || reportsError?.message}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-gray-600">Please log in to view your profile</p>
              <Link href="/login">
                <Button className="mt-4">
                  Login
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
          <p className="mt-2 text-gray-600">Manage your account and view your contribution history</p>
        </div>

        {/* User Info Card */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-center space-x-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <User className="h-8 w-8" />
              </div>
              <div>
                <CardTitle className="text-2xl">{user.display_name}</CardTitle>
                <CardDescription>{user.email}</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="flex items-center justify-center space-x-2">
                  <Award className="h-6 w-6 text-yellow-600" />
                  <span className="text-3xl font-bold text-gray-900">{user.total_points}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">Total Points</p>
              </div>
              
              <div className="text-center">
                <Badge variant="outline" className="text-lg px-4 py-2">
                  {user.badge_tier || 'Citizen'}
                </Badge>
                <p className="text-sm text-gray-600 mt-1">Badge Tier</p>
              </div>
              
              <div className="text-center">
                <Badge variant="secondary" className="text-lg px-4 py-2">
                  {user.role}
                </Badge>
                <p className="text-sm text-gray-600 mt-1">Role</p>
              </div>
            </div>
            
            <div className="mt-6 pt-6 border-t">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Calendar className="h-4 w-4" />
                <span>Member since {new Date(user.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Reports History */}
        <Card>
          <CardHeader>
            <CardTitle>My Reports</CardTitle>
            <CardDescription>
              History of waste reports you&apos;ve submitted
            </CardDescription>
          </CardHeader>
          <CardContent>
            {reports.length === 0 ? (
              <div className="text-center py-8">
                <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">You haven&apos;t submitted any reports yet</p>
                <Link href="/report">
                  <Button>Submit Your First Report</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {reports.map((report) => (
                  <div key={report.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <StatusBadge status={report.status} />
                        <SeverityBadge severity={report.severity} />
                      </div>
                      <div className="text-sm text-gray-600">
                        {new Date(report.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-sm text-gray-600 mb-2">
                      <MapPin className="h-4 w-4" />
                      <span>
                        {report.location.lat.toFixed(4)}, {report.location.lng.toFixed(4)}
                      </span>
                    </div>
                    
                    {report.note && (
                      <p className="text-sm text-gray-700 mb-2">{report.note}</p>
                    )}
                    
                    <div className="flex items-center space-x-2">
                      <Link href={`/report/${report.id}`}>
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

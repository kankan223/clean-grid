"use client";

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, Trophy, Medal, Award, Crown, Users } from 'lucide-react';
import Link from 'next/link';

interface LeaderboardEntry {
  rank: number;
  user: {
    id: string;
    display_name: string;
    email: string;
    role: string;
  };
  total_points: number;
  badge_tier?: string;
  reports_count: number;
  verifications_count: number;
}

const getRankIcon = (rank: number) => {
  switch (rank) {
    case 1:
      return <Crown className="h-5 w-5 text-yellow-500" />;
    case 2:
      return <Medal className="h-5 w-5 text-gray-400" />;
    case 3:
      return <Award className="h-5 w-5 text-amber-600" />;
    default:
      return <span className="text-lg font-bold text-gray-600">#{rank}</span>;
  }
};

const getBadgeColor = (tier?: string) => {
  switch (tier) {
    case 'Hero':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    case 'Guardian':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'Cleaner':
      return 'bg-green-100 text-green-800 border-green-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export default function LeaderboardPage() {
  const {
    data: leaderboard = [],
    isLoading,
    error
  } = useQuery<LeaderboardEntry[]>({
    queryKey: ['leaderboard'],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004';
      const response = await fetch(`${apiUrl}/api/leaderboard`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch leaderboard');
      }

      return response.json();
    },
    refetchInterval: 60000, // Refresh every minute
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto" />
          <p className="mt-2">Loading leaderboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-red-600">Error loading leaderboard</p>
              <p className="text-sm text-gray-600 mt-2">{error.message}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <Trophy className="h-8 w-8" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Community Leaderboard</h1>
          <p className="mt-2 text-gray-600">
            Celebrating our top contributors in keeping the city clean
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Users className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{leaderboard.length}</p>
                  <p className="text-sm text-gray-600">Active Contributors</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Trophy className="h-8 w-8 text-yellow-600" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {leaderboard[0]?.total_points || 0}
                  </p>
                  <p className="text-sm text-gray-600">Top Score</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Award className="h-8 w-8 text-green-600" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">
                    {leaderboard.reduce((sum, entry) => sum + entry.total_points, 0)}
                  </p>
                  <p className="text-sm text-gray-600">Total Points</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Leaderboard Table */}
        <Card>
          <CardHeader>
            <CardTitle>Top Contributors</CardTitle>
            <CardDescription>
              Ranked by total points earned from reports and verifications
            </CardDescription>
          </CardHeader>
          <CardContent>
            {leaderboard.length === 0 ? (
              <div className="text-center py-8">
                <Trophy className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">No contributors yet</p>
                <Link href="/report">
                  <Button>Be the First to Report</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {leaderboard.map((entry) => (
                  <div
                    key={entry.user.id}
                    className={`flex items-center justify-between p-4 rounded-lg border ${
                      entry.rank <= 3 ? 'bg-gradient-to-r from-yellow-50 to-transparent' : ''
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      {/* Rank */}
                      <div className="flex items-center justify-center w-12">
                        {getRankIcon(entry.rank)}
                      </div>
                      
                      {/* User Info */}
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold text-gray-900">
                            {entry.user.display_name}
                          </h3>
                          {entry.badge_tier && (
                            <Badge className={getBadgeColor(entry.badge_tier)}>
                              {entry.badge_tier}
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600">{entry.user.email}</p>
                      </div>
                    </div>
                    
                    {/* Stats */}
                    <div className="flex items-center space-x-6">
                      <div className="text-center">
                        <p className="text-lg font-bold text-gray-900">{entry.total_points}</p>
                        <p className="text-xs text-gray-600">Points</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-gray-900">{entry.reports_count}</p>
                        <p className="text-xs text-gray-600">Reports</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-gray-900">{entry.verifications_count}</p>
                        <p className="text-xs text-gray-600">Verifications</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Call to Action */}
        <div className="mt-8 text-center">
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Want to climb the leaderboard?
              </h3>
              <p className="text-gray-600 mb-4">
                Report waste in your area and verify cleanups to earn points!
              </p>
              <Link href="/report">
                <Button>
                  Report Waste Now
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

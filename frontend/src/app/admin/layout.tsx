'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth, useAuthInitializing } from '@/lib/stores/auth';
import { Loader2 } from 'lucide-react';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const { user, isAuthenticated } = useAuth();
  const isInitializing = useAuthInitializing();
  const router = useRouter();

  useEffect(() => {
    // Wait for initialization to complete
    if (isInitializing) {
      return;
    }

    // Check authentication and role
    if (!isAuthenticated || !user) {
      // Redirect to login page
      router.push('/login');
      return;
    }

    if (user.role !== 'admin') {
      // Show access denied and redirect
      alert('Access Denied: Admin role required to access this page.');
      router.push('/');
      return;
    }
  }, [user, isAuthenticated, isInitializing, router]);

  // Show loading spinner while initializing
  if (isInitializing) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // If we reach here, user is authenticated admin
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        {/* Admin Sidebar */}
        <div className="w-64 bg-gray-900 min-h-screen">
          <div className="p-4">
            <h2 className="text-white text-xl font-bold mb-6">Admin Panel</h2>
            <nav className="space-y-2">
              <a
                href="/admin"
                className="block px-3 py-2 text-gray-300 hover:bg-gray-700 hover:text-white rounded-md"
              >
                Dashboard
              </a>
              <a
                href="/admin/incidents"
                className="block px-3 py-2 text-gray-300 hover:bg-gray-700 hover:text-white rounded-md"
              >
                Incidents
              </a>
              <a
                href="/admin/crews"
                className="block px-3 py-2 text-gray-300 hover:bg-gray-700 hover:text-white rounded-md"
              >
                Crews
              </a>
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <main className="flex-1">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

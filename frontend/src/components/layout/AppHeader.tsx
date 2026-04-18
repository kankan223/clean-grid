"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Map, 
  FileText, 
  Trophy, 
  User, 
  Settings, 
  Trash2,
  Menu,
  X,
  Award
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/lib/stores/auth";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
  requireAuth?: boolean;
}

export function AppHeader() {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems: NavItem[] = [
    {
      href: "/",
      label: "Map",
      icon: Map,
    },
    {
      href: "/report",
      label: "Report",
      icon: FileText,
    },
    {
      href: "/leaderboard",
      label: "Leaderboard",
      icon: Trophy,
    },
    {
      href: "/profile",
      label: "Profile",
      icon: User,
      requireAuth: true,
    },
    {
      href: "/admin",
      label: "Admin",
      icon: Settings,
      adminOnly: true,
    },
  ];

  const filteredNavItems = navItems.filter(item => 
    !item.adminOnly || (user?.role === 'admin')
  ).filter(item => 
    !item.requireAuth || user
  );

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Trash2 className="h-4 w-4" />
          </div>
          <span className="text-lg font-bold">CleanGrid</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-1">
          {filteredNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href} className="flex items-center space-x-2">
                <Button
                  variant={isActive(item.href) ? "secondary" : "ghost"}
                  size="sm"
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Button>
              </Link>
            );
          })}
        </nav>

        {/* User Section */}
        <div className="flex items-center space-x-2">
          {isAuthenticated ? (
            <>
              <div className="hidden md:flex items-center space-x-2">
                <div className="flex items-center space-x-1">
                  <Award className="h-4 w-4 text-yellow-600" />
                  <span className="text-sm font-medium">{user?.total_points || 0}</span>
                </div>
                <Badge variant="outline" className="text-xs">
                  {user?.role}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {user?.email}
                </span>
              </div>
              <Button variant="outline" size="sm" onClick={logout}>
                <User className="h-4 w-4 mr-2" />
                <span className="hidden md:inline">Logout</span>
              </Button>
            </>
          ) : (
            <div className="flex items-center space-x-2">
              <Link href="/register">
                <Button variant="ghost" size="sm">
                  Register
                </Button>
              </Link>
              <Link href="/login">
                <Button size="sm">
                  <User className="h-4 w-4 mr-2" />
                  Login
                </Button>
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle */}
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="h-4 w-4" />
            ) : (
              <Menu className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="border-t bg-background md:hidden">
          <nav className="container py-4 space-y-2">
            {filteredNavItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link 
                    key={item.href}
                    href={item.href} 
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center space-x-2"
                  >
                    <Button
                      variant={isActive(item.href) ? "secondary" : "ghost"}
                      size="sm"
                      className="w-full justify-start"
                    >
                      <Icon className="h-4 w-4" />
                      <span>{item.label}</span>
                    </Button>
                  </Link>
              );
            })}
            {isAuthenticated ? (
              <div className="pt-2 border-t">
                <div className="flex items-center justify-between px-2 py-1">
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1">
                      <Award className="h-4 w-4 text-yellow-600" />
                      <span className="text-sm font-medium">{user?.total_points || 0}</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {user?.role}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {user?.email}
                    </span>
                  </div>
                  <Button variant="outline" size="sm" onClick={logout}>
                    <User className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </div>
              </div>
            ) : (
              <div className="pt-2 border-t space-y-2">
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="ghost" size="sm" className="w-full justify-start">
                    <User className="h-4 w-4 mr-2" />
                    Login
                  </Button>
                </Link>
                <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="ghost" size="sm" className="w-full justify-start">
                    Register
                  </Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}

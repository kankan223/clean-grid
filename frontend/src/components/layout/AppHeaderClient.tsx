"use client";

import { AppHeader } from "@/components/layout/AppHeader";
import { AuthProvider } from "@/lib/stores/auth";

interface AppHeaderClientProps {
  children: React.ReactNode;
}

export function AppHeaderClient({ children }: AppHeaderClientProps) {
  return (
    <AuthProvider>
      <AppHeader />
      {children}
    </AuthProvider>
  );
}

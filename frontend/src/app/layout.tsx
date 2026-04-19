import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import "leaflet/dist/leaflet.css";
import { cn } from "@/lib/utils";
import { AppHeaderClient } from "@/components/layout/AppHeaderClient";
import { QueryProvider } from "@/providers/QueryProvider";
import { ToastViewport } from "@/components/ui/toast";

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: "CleanGrid - Smart Waste Management",
  description: "AI-powered waste detection, mapping, and cleanup coordination system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans", inter.variable)}>
      <body className={`${inter.variable} antialiased min-h-screen bg-background`}>
        <QueryProvider>
          <AppHeaderClient>
            <main className="flex-1">
              {children}
            </main>
          </AppHeaderClient>
          <ToastViewport />
        </QueryProvider>
      </body>
    </html>
  );
}

"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Plus, Camera } from "lucide-react";
import { useState } from "react";

export function ReportWasteFAB() {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-40 md:bottom-8 md:right-8">
      <Link href="/report">
        <Button
          size="lg"
          className="h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 bg-primary text-primary-foreground"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <div className="relative">
            <Camera className="h-6 w-6" />
            {isHovered && (
              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                Report Waste
              </div>
            )}
          </div>
        </Button>
      </Link>
    </div>
  );
}

#!/bin/bash

# CleanGrid Frontend Setup Script
# This script sets up the complete Next.js 14 frontend with all dependencies

set -e

echo "=== CleanGrid Frontend Setup ==="

# 1. Create Next.js 14 app with TypeScript, Tailwind, App Router
echo "1. Creating Next.js 14 app..."
npx create-next-app@14 frontend --typescript --tailwind --app --eslint --src-dir --import-alias "@/*"

# 2. Navigate to frontend directory
cd frontend

# 3. Install shadcn/ui and initialize
echo "2. Installing shadcn/ui..."
npx shadcn-ui@latest init -d

# 4. Install required shadcn components
echo "3. Installing shadcn components..."
npx shadcn-ui@latest add table
npx shadcn-ui@latest add drawer
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add select
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add card
npx shadcn-ui@latest add skeleton

# 5. Install state management libraries
echo "4. Installing state management..."
npm install zustand @tanstack/react-query

# 6. Install mapping libraries
echo "5. Installing mapping libraries..."
npm install leaflet react-leaflet
npm install --save-dev @types/leaflet

# 7. Install additional Leaflet plugins
echo "6. Installing Leaflet plugins..."
npm install leaflet.markercluster leaflet.heat
npm install --save-dev @types/leaflet.markercluster

# 8. Install additional utilities
echo "7. Installing utilities..."
npm install clsx tailwind-merge class-variance-authority
npm install lucide-react

# 9. Install HTTP client
echo "8. Installing HTTP client..."
npm install axios

# 10. Create project structure
echo "9. Creating project structure..."
mkdir -p src/components/map
mkdir -p src/components/admin
mkdir -p src/components/report
mkdir -p src/lib/stores
mkdir -p src/lib/api
mkdir -p src/lib/utils

echo "=== Frontend setup complete! ==="
echo "Next: Configure Leaflet SSR fix and create initial stores"

#!/bin/bash

# CleanGrid Development Environment Stop Script
# Gracefully stops all services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] $1${NC}"
}

print_status "Stopping CleanGrid Development Environment..."

# Stop services using PID files if they exist
if [ -f "logs/ai-service.pid" ]; then
    AI_PID=$(cat logs/ai-service.pid)
    if ps -p $AI_PID > /dev/null 2>&1; then
        print_status "Stopping AI Service (PID: $AI_PID)..."
        kill $AI_PID
        print_success "AI Service stopped"
    else
        print_warning "AI Service process not found"
    fi
    rm -f logs/ai-service.pid
fi

if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        print_status "Stopping Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        print_success "Backend stopped"
    else
        print_warning "Backend process not found"
    fi
    rm -f logs/backend.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        print_status "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        print_success "Frontend stopped"
    else
        print_warning "Frontend process not found"
    fi
    rm -f logs/frontend.pid
fi

# Also try to kill processes on specific ports (fallback)
print_status "Checking for remaining processes on ports..."

# Kill processes on ports 8001, 8000, 3000
for port in 8001 8000 3000; do
    PID=$(lsof -ti:$port 2>/dev/null || echo "")
    if [ ! -z "$PID" ]; then
        print_status "Killing process on port $port (PID: $PID)..."
        kill -9 $PID 2>/dev/null || true
    fi
done

# Stop Docker containers
print_status "Stopping Docker containers..."
docker compose down db redis 2>/dev/null || true

print_success "All services stopped!"
echo ""
echo "=================================="
echo "CLEANGRID SERVICES STOPPED"
echo "=================================="
echo "To restart: ./start-dev.sh"
echo ""

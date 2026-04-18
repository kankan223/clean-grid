#!/bin/bash

# CleanGrid Development Environment Startup Script
# Automatically starts all services in correct order with proper cleanup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service PIDs storage
AI_PID=""
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup function for graceful shutdown
cleanup() {
    print_status "Shutting down services..."
    
    # Kill background processes by PID
    if [ ! -z "$AI_PID" ]; then
        kill $AI_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Additional cleanup - kill any remaining processes on our ports
    for port in 3000 8000 8001; do
        if lsof -ti:$port > /dev/null 2>&1; then
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    
    print_success "All services stopped"
    exit 0
}

# Set trap for cleanup on script termination
trap cleanup SIGINT SIGTERM

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Starting CleanGrid Development Environment..."

# Step 0.1: Create logs directory immediately (CRITICAL FIX)
mkdir -p logs
print_success "Logs directory created"

# Step 0: Aggressive Port Cleanup
print_status "Cleaning up existing processes..."
for port in 3000 8000 8001; do
    if lsof -ti:$port > /dev/null 2>&1; then
        print_warning "Killing process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

# Step 0.2: Clear Next.js build cache to prevent Turbopack CSS issues
print_status "Clearing Next.js build cache..."
if [ -d "frontend/.next" ]; then
    rm -rf frontend/.next
    print_success "Build cache cleared"
fi

# Step 1: Start Infrastructure (db, redis)
print_status "Starting infrastructure services..."
docker compose up -d db redis

# Wait for database to be ready
print_status "Waiting for database to be ready..."
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U cleangrid > /dev/null 2>&1; then
        print_success "Database is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Database failed to start after 30 seconds"
        exit 1
    fi
    sleep 1
done

# Wait for Redis to be ready
print_status "Waiting for Redis to be ready..."
for i in {1..10}; do
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is ready!"
        break
    fi
    if [ $i -eq 10 ]; then
        print_error "Redis failed to start after 10 seconds"
        exit 1
    fi
    sleep 1
done

# Step 2: Ensure Backend Virtual Environment (CRITICAL FIX)
print_status "Setting up backend virtual environment..."
cd backend

# Remove broken venv if it exists but is empty
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    print_status "Removing broken virtual environment..."
    rm -rf venv
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating backend virtual environment..."
    python3 -m venv venv || {
        print_error "Failed to create virtual environment"
        exit 1
    }
fi

# Activate and install dependencies
source venv/bin/activate || {
    print_error "Failed to activate virtual environment"
    exit 1
}

# Install setuptools first to fix shapely build issues
pip install --upgrade pip setuptools wheel > ../logs/backend-install.log 2>&1 || {
    print_error "Failed to install pip setuptools"
    exit 1
}

# Install pkg_resources first (needed for shapely)
pip install setuptools >> ../logs/backend-install.log 2>&1 || {
    print_error "Failed to install setuptools"
    exit 1
}

# Try to install shapely with system packages if available, otherwise skip
if pip install shapely >> ../logs/backend-install.log 2>&1; then
    print_success "Shapely installed successfully"
else
    print_warning "Shapely installation failed, but continuing without it"
    echo "Shapely is optional for basic functionality" >> ../logs/backend-install.log
fi

# Install remaining dependencies, ignoring shapely if it fails
pip install -r requirements.txt >> ../logs/backend-install.log 2>&1 || {
    print_warning "Some dependencies failed, but continuing..."
}
export PYTHONPATH=.
cd ..

# Step 2.1: Run Database Migrations
print_status "Running database migrations..."
cd backend
source venv/bin/activate
export PYTHONPATH=.

if ! alembic upgrade head; then
    print_error "Database migration failed"
    exit 1
fi
print_success "Database migrations completed"

# Step 3: Seed Database
print_status "Seeding database with default admin user..."
if ! python seed/seed.py; then
    print_error "Database seeding failed"
    exit 1
fi
print_success "Database seeding completed"
cd ..

# Step 4: Ensure AI Service Virtual Environment (CRITICAL FIX)
print_status "Setting up AI Service virtual environment..."
cd ai-service

# Remove broken venv if it exists but is empty
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    print_status "Removing broken AI Service virtual environment..."
    rm -rf venv
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating AI Service virtual environment..."
    python3 -m venv venv || {
        print_error "Failed to create AI Service virtual environment"
        exit 1
    }
fi

# Activate and install dependencies
source venv/bin/activate || {
    print_error "Failed to activate AI Service virtual environment"
    exit 1
}

# Install setuptools first to fix potential build issues
pip install --upgrade pip setuptools wheel > ../logs/ai-service-install.log 2>&1 || {
    print_error "Failed to install pip setuptools for AI Service"
    exit 1
}

# Install dependencies
pip install -r requirements.txt >> ../logs/ai-service-install.log 2>&1 || {
    print_error "Failed to install AI Service dependencies"
    exit 1
}

# Start AI Service in background
print_status "Starting AI Service on port 8001..."
python app/main.py > ../logs/ai-service.log 2>&1 &
AI_PID=$!
cd ..

# Wait for AI Service to be ready
print_status "Waiting for AI Service to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "AI Service is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        print_warning "AI Service might still be starting..."
        break
    fi
    sleep 1
done

# Step 5: Start Backend (port 8000)
print_status "Starting Backend on port 8000..."
cd backend
source venv/bin/activate
export PYTHONPATH=.

# Start Backend in background
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)" > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for Backend to be ready
print_status "Waiting for Backend to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        print_warning "Backend might still be starting..."
        break
    fi
    sleep 1
done

# Step 6: Start Frontend (port 3000)
print_status "Starting Frontend on port 3000..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install > ../logs/frontend-install.log 2>&1
fi

# Start Frontend in background
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for Frontend to be ready
print_status "Waiting for Frontend to be ready..."
for i in {1..20}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is ready!"
        break
    fi
    if [ $i -eq 20 ]; then
        print_warning "Frontend might still be starting..."
        break
    fi
    sleep 1
done

# Step 7: Display service status
print_success "CleanGrid Development Environment is ready!"
echo ""
echo "=================================="
echo "CLEANGRID SERVICES STATUS"
echo "=================================="
echo "Database:  http://localhost:5432 (PostgreSQL + PostGIS)"
echo "Redis:     http://localhost:6379"
echo "AI Service: http://localhost:8001"
echo "Backend:    http://localhost:8000"
echo "Frontend:   http://localhost:3000"
echo "API Docs:   http://localhost:8000/docs"
echo ""
echo "=================================="
echo "SERVICE LOGS"
echo "=================================="
echo "AI Service:  tail -f logs/ai-service.log"
echo "Backend:     tail -f logs/backend.log"
echo "Frontend:    tail -f logs/frontend.log"
echo ""
echo "=================================="
echo "STOPPING SERVICES"
echo "=================================="
echo "To stop all services: Press Ctrl+C"
echo "To restart: ./start-dev.sh"
echo ""
echo "=================================="
echo "USEFUL COMMANDS"
echo "=================================="
echo "Check status: curl http://localhost:8000/health"
echo "API tests:   curl http://localhost:8000/api/admin/admin/health"
echo "Database:    docker compose exec db psql -U cleangrid cleangrid"
echo ""

# Show live logs from all services
print_status "Showing live logs from all services (Ctrl+C to stop watching)..."
tail -f logs/ai-service.log logs/backend.log logs/frontend.log

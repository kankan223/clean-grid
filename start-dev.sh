#!/bin/bash

# CleanGrid Development Environment Startup Script
# Automatically starts all services in the correct order

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Starting CleanGrid Development Environment..."

# Step 1: Check and start Docker containers (db, redis)
print_status "Checking Docker containers..."

# Check if db and redis are running
DB_RUNNING=$(docker compose ps -q db 2>/dev/null || echo "")
REDIS_RUNNING=$(docker compose ps -q redis 2>/dev/null || echo "")

if [ -z "$DB_RUNNING" ] || [ -z "$REDIS_RUNNING" ]; then
    print_warning "Database or Redis not running. Starting Docker containers..."
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
else
    print_success "Database and Redis are already running"
fi

# Step 2: Run database migrations
print_status "Running database migrations..."
cd backend
source venv/bin/activate
export PYTHONPATH=.

if ! alembic upgrade head; then
    print_error "Database migration failed"
    exit 1
fi
print_success "Database migrations completed"

# Step 3: Start AI Service (port 8001)
print_status "Starting AI Service on port 8001..."
cd ../ai-service
if [ ! -d "venv" ]; then
    print_status "Creating AI Service virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Start AI Service in background
python app/main.py > ../logs/ai-service.log 2>&1 &
AI_PID=$!
echo $AI_PID > ../logs/ai-service.pid
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

# Step 4: Start Backend (port 8004)
print_status "Starting Backend on port 8004..."
cd backend
source venv/bin/activate
export PYTHONPATH=.

# Start Backend in background
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8004, reload=True)" > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
cd ..

# Wait for Backend to be ready
print_status "Waiting for Backend to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:8004/health > /dev/null 2>&1; then
        print_success "Backend is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        print_warning "Backend might still be starting..."
        break
    fi
    sleep 1
done

# Step 5: Start Frontend (port 3000)
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
echo $FRONTEND_PID > ../logs/frontend.pid
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

# Create logs directory if it doesn't exist
mkdir -p logs

# Step 6: Display service status and logs
print_success "CleanGrid Development Environment is ready!"
echo ""
echo "=================================="
echo "CLEANGRID SERVICES STATUS"
echo "=================================="
echo "Database:  http://localhost:5432 (PostgreSQL + PostGIS)"
echo "Redis:     http://localhost:6379"
echo "AI Service: http://localhost:8001"
echo "Backend:    http://localhost:8004"
echo "Frontend:   http://localhost:3000"
echo "API Docs:   http://localhost:8004/docs"
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
echo "To stop all services: ./stop-dev.sh"
echo "To restart: ./start-dev.sh"
echo ""
echo "=================================="
echo "USEFUL COMMANDS"
echo "=================================="
echo "Check status: curl http://localhost:8004/health"
echo "API tests:   curl http://localhost:8004/api/admin/admin/health"
echo "Database:    docker compose exec db psql -U cleangrid cleangrid"
echo ""

# Show live logs from all services
print_status "Showing live logs from all services (Ctrl+C to stop watching)..."
tail -f logs/ai-service.log logs/backend.log logs/frontend.log

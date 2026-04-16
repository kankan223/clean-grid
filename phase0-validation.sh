#!/bin/bash

# CleanGrid Phase 0 Validation Gate
# Complete validation of all Phase 0 components

set -e

echo "=== CleanGrid Phase 0 Validation Gate ==="
echo "This script validates all Phase 0 components before proceeding to Phase 1"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}Step $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# Step 1: Environment Setup
print_step "1" "Setting up environment files"
echo "Copying .env.example files..."
cp .env.example .env 2>/dev/null || echo ".env already exists"
cp ai-service/.env.example ai-service/.env 2>/dev/null || echo "ai-service/.env already exists"

# Generate JWT secret key if not present
if ! grep -q "JWT_SECRET_KEY=your-super-secret" .env; then
    echo "JWT_SECRET_KEY already configured"
else
    echo "Generating JWT secret key..."
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-super-secret-jwt-key-here-32-chars-minimum/$SECRET_KEY/" .env
    print_success "JWT secret key generated"
fi

# Step 2: Frontend Setup
print_step "2" "Setting up frontend dependencies"
echo "Running frontend setup script..."
chmod +x frontend-fix.sh
./frontend-fix.sh

# Step 3: Docker Build and Start
print_step "3" "Building and starting Docker containers"
echo "Building all containers..."
docker compose build --no-cache

echo "Starting containers in detached mode..."
docker compose up -d

# Step 4: Wait for containers to be ready
print_step "4" "Waiting for containers to be healthy"
echo "Waiting 30 seconds for containers to initialize..."
sleep 30

# Check container health
echo "Checking container status..."
docker compose ps

# Step 5: Database Validation
print_step "5" "Testing database connection"
echo "Running database test inside backend container..."
docker compose exec backend python test_db.py

if [ $? -eq 0 ]; then
    print_success "Database tests passed"
else
    print_error "Database tests failed"
    exit 1
fi

# Step 6: AI Service Validation
print_step "6" "Testing AI Service"
echo "Checking AI Service logs for model loading..."
docker compose logs ai-service | tail -10

echo "Testing AI Service health endpoint..."
curl -f http://localhost:8001/health || {
    print_error "AI Service health check failed"
    docker compose logs ai-service
    exit 1
}

print_success "AI Service is healthy"

# Step 7: Backend Validation
print_step "7" "Testing Backend API"
echo "Testing Backend health endpoint..."
curl -f http://localhost:8000/health || {
    print_error "Backend health check failed"
    docker compose logs backend
    exit 1
}

print_success "Backend API is healthy"

# Step 8: Frontend Validation
print_step "8" "Testing Frontend"
echo "Testing Frontend is serving..."
curl -f http://localhost:3000 > /dev/null || {
    print_error "Frontend is not responding"
    docker compose logs frontend
    exit 1
}

print_success "Frontend is serving"

# Step 9: Service URLs Summary
print_step "9" "Service URLs for Manual Verification"
echo ""
echo -e "${GREEN}=== CLEANGRID SERVICES ARE RUNNING ===${NC}"
echo ""
echo -e "${BLUE}Frontend Application:${NC}"
echo "   URL: http://localhost:3000"
echo "   Purpose: Main web application with Leaflet map"
echo ""
echo -e "${BLUE}Backend API Documentation:${NC}"
echo "   URL: http://localhost:8000/docs"
echo "   Purpose: FastAPI interactive docs"
echo "   Health: http://localhost:8000/health"
echo ""
echo -e "${BLUE}AI Service Documentation:${NC}"
echo "   URL: http://localhost:8001/docs"
echo "   Purpose: YOLOv8n inference API"
echo "   Health: http://localhost:8001/health"
echo ""
echo -e "${BLUE}Database:${NC}"
echo "   Host: localhost:5432"
echo "   Database: cleangrid"
echo "   User: cleangrid"
echo ""
echo -e "${BLUE}Redis:${NC}"
echo "   Host: localhost:6379"
echo ""

# Step 10: Manual Testing Instructions
print_step "10" "Manual Testing Instructions"
echo ""
echo "Please manually verify the following:"
echo ""
echo "1. FRONTEND (http://localhost:3000):"
echo "   - Page loads without errors"
echo "   - No TypeScript errors in browser console"
echo "   - Leaflet map should initialize (even without data)"
echo ""
echo "2. BACKEND (http://localhost:8000/docs):"
echo "   - Swagger UI loads"
echo "   - Try the /health endpoint"
echo "   - Check that authentication endpoints are visible"
echo ""
echo "3. AI SERVICE (http://localhost:8001/docs):"
echo "   - Swagger UI loads"
echo "   - Try the /health endpoint (should show model_loaded: true)"
echo "   - Test /infer endpoint with a sample image URL"
echo ""

# Step 11: Debugging Commands
print_step "11" "Debugging Commands (if needed)"
echo ""
echo "View logs for a specific service:"
echo "  docker compose logs [frontend|backend|ai-service|db|redis]"
echo ""
echo "Restart a specific service:"
echo "  docker compose restart [service-name]"
echo ""
echo "Stop all services:"
echo "  docker compose down"
echo ""

echo -e "${GREEN}=== PHASE 0 VALIDATION COMPLETE ===${NC}"
echo ""
echo "If all services are working correctly, you can now proceed to Phase 1!"
echo ""
echo "Next steps:"
echo "1. Run database migrations: docker compose exec backend alembic upgrade head"
echo "2. Seed initial data: docker compose exec backend python seed/seed.py"
echo "3. Start Phase 1 development"

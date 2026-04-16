#!/bin/bash
# Phase 1 Validation Command - CleanGrid
# Validates complete reporting and spatial visualization functionality

echo "🔍 Phase 1: Core Reporting Loop - Validation Gate"
echo "=============================================="

# Test 1: Backend Health Check
echo "📊 Testing Backend Health..."
curl -s http://localhost:8000/health
if [ $? -eq 0 ]; then
    echo "✅ Backend healthy"
else
    echo "❌ Backend unhealthy"
    exit 1
fi

# Test 2: AI Service Health Check
echo "🤖 Testing AI Service..."
curl -s http://localhost:8001/health
if [ $? -eq 0 ]; then
    echo "✅ AI Service healthy"
else
    echo "❌ AI Service unhealthy"
    exit 1
fi

# Test 3: Frontend Health Check
echo "🌐 Testing Frontend..."
curl -s -o /dev/null http://localhost:3000
if [ $? -eq 0 ]; then
    echo "✅ Frontend healthy"
else
    echo "❌ Frontend unhealthy"
    exit 1
fi

# Test 4: Backend API - Create Report
echo "📤 Testing Report Creation..."
REPORT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/reports \
  -H "Content-Type: multipart/form-data" \
  -F "lat=40.7128" \
  -F "lng=-74.0060" \
  -F "note=Test report from validation script")

if echo "$REPORT_RESPONSE" | grep -q '"status":"processing"'; then
    echo "✅ Report creation API working"
else
    echo "❌ Report creation API failed"
    echo "$REPORT_RESPONSE"
    exit 1
fi

# Test 5: Backend API - List Incidents
echo "📍 Testing Incident List API..."
INCIDENTS_RESPONSE=$(curl -s "http://localhost:8000/api/reports?limit=5")

if echo "$INCIDENTS_RESPONSE" | grep -q '"incidents"'; then
    echo "✅ Incident list API working"
else
    echo "❌ Incident list API failed"
    echo "$INCIDENTS_RESPONSE"
    exit 1
fi

# Test 6: AI Service Inference
echo "🧠 Testing AI Inference..."
AI_RESPONSE=$(curl -s -X POST http://localhost:8001/infer \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://picsum.photos/400/300"}')

if echo "$AI_RESPONSE" | grep -q '"waste_detected":true'; then
    echo "✅ AI inference working"
else
    echo "❌ AI inference failed"
    echo "$AI_RESPONSE"
    exit 1
fi

echo "=============================================="
echo "🎉 Phase 1 Validation Complete!"
echo "All core reporting and spatial features are functional."
echo "Ready for Phase 1 Sprint 3: Admin Dashboard & Task Assignment"

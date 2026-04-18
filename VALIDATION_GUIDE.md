# 🧪 Quick Validation Guide — Fixes Applied

**Date:** April 19, 2026  
**Issues Fixed:** 6 critical infrastructure problems  

---

## ✅ How to Validate All Fixes

### 1. Clean Startup Test
```bash
# Kill any lingering processes
pkill -f "npm|python|uvicorn"
sleep 2

# Run the startup script
cd /home/ken/Projects/Waste_detection_bot
./start-dev.sh
```

**Expected Output:**
- ✅ `[HH:MM:SS] Database is ready!`
- ✅ `[HH:MM:SS] Redis is ready!`
- ✅ `[HH:MM:SS] Shapely installed successfully`
- ✅ `[HH:MM:SS] Backend dependencies installed`
- ✅ `[HH:MM:SS] Database migrations completed`
- ✅ `[HH:MM:SS] Database seeding completed`
- ✅ `[HH:MM:SS] AI Service is ready!`
- ✅ `[HH:MM:SS] Backend is ready!`
- ✅ `[HH:MM:SS] Frontend is ready!`
- ✅ `[HH:MM:SS] CleanGrid Development Environment is ready!`

**⏱️ Total Time:** ~2-3 minutes

---

### 2. Verify Database Migration (PostGIS)

```bash
# In a new terminal
docker compose exec db psql -U cleangrid cleangrid -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
"
```

**Expected Tables:**
- ✅ users
- ✅ incidents
- ✅ point_transactions
- ✅ **routes** (NEW!)

**Check PostGIS Location Column:**
```bash
docker compose exec db psql -U cleangrid cleangrid -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'incidents' 
AND column_name = 'location';
"
```

**Expected Output:**
- ✅ column_name: `location`
- ✅ data_type: `geography`

**Check GIST Spatial Index:**
```bash
docker compose exec db psql -U cleangrid cleangrid -c "
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'incidents' 
AND indexname LIKE '%location%';
"
```

**Expected Output:**
- ✅ Index name contains `location`
- ✅ Index type: `GIST`

---

### 3. Verify Frontend Auto-Starts

**Check Process:**
```bash
ps aux | grep "npm run dev" | grep -v grep
```

**Expected Output:**
- ✅ One running process for `npm run dev`
- ✅ Working directory: `.../Waste_detection_bot/frontend`

**Check HTTP Response:**
```bash
curl -s http://localhost:3000 | head -20
```

**Expected Output:**
- ✅ HTML response (Next.js page)
- ✅ Status 200 OK
- ✅ Contains: `<!DOCTYPE html>` or `<html>`

---

### 4. Verify Backend API

**Health Check:**
```bash
curl -s http://localhost:8000/health | jq .
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-19T00:46:XX.XXXXXX",
  "services": {
    "database": "connected",
    "redis": "connected",
    "ai_service": "connected"
  }
}
```

**Swagger UI:**
```bash
curl -I http://localhost:8000/docs
```

**Expected Output:**
- ✅ Status: 200 OK
- ✅ Content-Type: text/html

---

### 5. Verify AI Service

**Health Check:**
```bash
curl -s http://localhost:8001/health | jq .
```

**Expected Output:**
- ✅ Status code 200
- ✅ Response contains: `healthy` or `ok`

---

### 6. Test Core Flows

#### 6.1 User Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword123!",
    "display_name": "Test User"
  }'
```

**Expected:**
- ✅ Status 200 or 201
- ✅ Response includes: user_id, email, token

#### 6.2 Admin Login (Default Credentials)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@cleangrid.io",
    "password": "CleanGrid@2024"
  }'
```

**Expected:**
- ✅ Status 200
- ✅ Response includes: access_token, refresh_token
- ✅ Cookies set (HttpOnly)

#### 6.3 Get Incidents List
```bash
curl -s http://localhost:8000/api/incidents?limit=5 | jq '.data | length'
```

**Expected:**
- ✅ Status 200
- ✅ Returns array of incidents
- ✅ Count ≥ 1 (from seeding)

---

## ✨ Troubleshooting

### If Database Migration Fails

**Check logs:**
```bash
tail -50 logs/backend-install.log
```

**Verify database is running:**
```bash
docker compose ps | grep db
```

**Reset database (if needed):**
```bash
docker compose down -v
docker compose up -d db redis
```

### If Frontend Won't Start

**Check logs:**
```bash
tail -50 logs/frontend.log
```

**Clear cache and rebuild:**
```bash
rm -rf frontend/.next frontend/node_modules
cd frontend && npm install && npm run dev
```

### If Dependencies Won't Install

**Check which package failed:**
```bash
tail -100 logs/backend-install.log | grep -i "error\|failed"
```

**Reinstall manually:**
```bash
cd backend
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Validation Checklist

- [ ] `./start-dev.sh` completes without errors
- [ ] Database migrations run successfully
- [ ] Frontend starts automatically (no manual npm run dev needed)
- [ ] All 5 services show ready status
- [ ] Database contains `routes` table
- [ ] Database location column is GEOGRAPHY type
- [ ] GIST index exists on incidents.location
- [ ] Backend API responds at http://localhost:8000/docs
- [ ] Frontend loads at http://localhost:3000
- [ ] AI Service health check passes
- [ ] Admin login works with default credentials
- [ ] At least 1 incident visible in GET /api/incidents

---

## 🎯 Success Criteria

✅ **All Items Checked** = Phase 2 Infrastructure Validated  
✅ **Ready to Proceed** = Begin Phase 4 or Phase 2.5 work

---

*Prepared by: GitHub Copilot*  
*For: Ken + Team*  
*Date: April 19, 2026*

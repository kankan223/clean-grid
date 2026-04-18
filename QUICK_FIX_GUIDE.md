# ⚡ QUICK FIX GUIDE - Get CleanGrid Running NOW

## 🚨 THE PROBLEM

Your system has **empty virtual environments**. They exist but have NO packages installed:
- Backend venv: ❌ No FastAPI
- AI Service venv: ❌ No PyTorch
- Result: Everything crashes on startup

## ✅ THE SOLUTION (Copy & Paste Ready)

### Step 1: Navigate to Project Root
```bash
cd /home/ken/Projects/Waste_detection_bot
```

### Step 2: Run One Command
```bash
chmod +x start-dev.sh && ./start-dev.sh
```

**That's it.** The script will:
1. Clean up zombie ports
2. Initialize backend venv + install 30 packages ✅
3. Initialize AI venv + install PyTorch (1.2GB first time) ✅
4. Run database migrations ✅
5. Start all 3 services automatically ✅

**Time:** 5-7 minutes first run (PyTorch download), then 30 seconds.

---

## 📊 What You'll See

### While Running:
```
[16:45:00] Ports cleaned
[16:45:05] PostgreSQL is ready
[16:45:08] Redis is ready
[16:45:12] ✅ Backend venv created
[16:45:30] ✅ Backend dependencies installed
[16:45:45] ✅ Database migrations complete
[16:46:10] ✅ AI Service venv created
[16:48:30] ✅ AI Service dependencies installed
[16:48:35] ✅ AI Service started
[16:49:00] ✅ Backend started
[16:49:15] ✅ Frontend started

✅ All services started successfully!

🌐 Frontend:     http://localhost:3000
🔧 Backend API:  http://localhost:8000
🤖 AI Service:   http://localhost:8001
```

### When Done:
- ✅ Open http://localhost:3000 (map loads)
- ✅ Click "Report Waste" button
- ✅ Upload an image
- ✅ AI analyzes it in <5 seconds
- ✅ Marker appears on map

---

## 🧪 Quick Validation Tests (5 minutes)

After the script finishes, run these in a NEW terminal:

```bash
# Test 1: Backend health
curl -s http://localhost:8000/health | jq '.status'
# Expected: "healthy"

# Test 2: AI Service health
curl -s http://localhost:8001/health | jq '.status'
# Expected: "healthy"

# Test 3: Database
docker compose exec -T db psql -U cleangrid cleangrid -c "SELECT COUNT(*) FROM incidents;"
# Expected: 43

# Test 4: Redis
docker compose exec -T redis redis-cli ping
# Expected: PONG
```

---

## 🆘 If Something Fails

### "Port X already in use"
```bash
lsof -ti:3000,8000,8001 | xargs kill -9
./start-dev.sh
```

### "PyTorch takes too long"
Normal on first run (1.2GB download + compile). Go grab coffee ☕
- First run: 5-7 minutes
- Subsequent: 30 seconds

### "Cannot connect to database"
```bash
# Check Docker is running
docker ps | grep postgres
# Should show: postgres:15 container

# If missing, run:
docker compose up -d db redis
# Then try again
```

### Any ModuleNotFoundError after running script
```bash
# The pip install might have failed. Try manually:
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../ai-service && source venv/bin/activate && pip install -r requirements.txt
```

---

## 📋 Error Summary (for reference)

| Issue | Status | Root Cause |
|-------|--------|-----------|
| Backend FastAPI not installed | 🔴 CRITICAL | `pip install` never ran |
| AI PyTorch not installed | 🔴 CRITICAL | `pip install` never ran |
| All endpoints return 404 | 🔴 CRITICAL | Services not running |
| Geolocation silently fails | ⚠️ FIXED | FormData header issue (already fixed) |
| CORS blocking localhost:3001 | ⚠️ FIXED | Already updated in code |

---

## ✨ After System is Up

You can now:
- 🗺️ Report waste incidents
- 🤖 Get AI analysis in <5s
- 👨‍💼 Access admin dashboard
- 🏆 View leaderboard
- 📱 Test full end-to-end flow
- 🧪 Begin Phase 3 development

---

## 📞 Support

All backend and AI errors are dependency-related and will be fixed by the `start-dev.sh` script.

If issues persist after running the script, check:
1. `logs/backend-install.log` - Backend pip errors
2. `logs/ai-service-install.log` - AI pip errors  
3. `logs/backend.log` - Runtime errors
4. `logs/ai-service.log` - Runtime errors

Run commands to view:
```bash
tail -f logs/backend.log
tail -f logs/ai-service.log
tail -f logs/frontend.log
```

---

**Status:** Ready to go! Run `./start-dev.sh` now. ⚡

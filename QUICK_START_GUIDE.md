# 🚀 Quick Start - After Bug Fixes

## Immediate Next Steps

### 1. Start Fresh Services
```bash
# Kill any running services
pkill -f "python.*uvicorn\|python.*main.py\|npm run dev" || true

# Remove old virtual environments
rm -rf backend/venv ai-service/venv

# Start all services
./start-dev.sh
```

### 2. Verify All Services
```bash
# Check AI Service
curl http://localhost:8001/health

# Check Backend  
curl http://localhost:8000/health

# Check Frontend
curl -I http://localhost:3000
```

### 3. Test Database Connection
```bash
# Test PostgreSQL
docker compose exec db psql -U cleangrid cleangrid -c "SELECT 1;"

# Test Redis
docker compose exec redis redis-cli ping
```

---

## Common Tasks

### View Logs
```bash
# AI Service logs
tail -f logs/ai-service.log

# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# All logs
tail -f logs/*.log
```

### Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| AI Service | http://localhost:8001 | Inference |

### Database Access
```bash
# Connect to PostgreSQL
docker compose exec db psql -U cleangrid cleangrid

# Connect to Redis
docker compose exec redis redis-cli
```

---

## Configuration

### Environment Variables
All configuration is in `.env` file:
```bash
# View current config
cat .env

# Edit config
nano .env

# Reload services after changes
./start-dev.sh
```

### AI Service Config
Location: `ai-service/.env`
```properties
YOLO_MODEL_PATH=/app/models/yolov8n.pt
YOLO_CONFIDENCE_THRESHOLD=0.45
RELEVANT_CLASSES=bottle,cup,bag,banana,can,backpack,suitcase
AI_SERVICE_PORT=8001
AI_SERVICE_HOST=0.0.0.0
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Services Won't Start
```bash
# Check if ports are in use
lsof -i :8000  # Backend
lsof -i :8001  # AI Service
lsof -i :3000  # Frontend

# Kill processes if needed
kill -9 <PID>

# Try again
./start-dev.sh
```

### Configuration Errors
```bash
# Test configuration loading
cd ai-service
source venv/bin/activate
python -c "from app.config import settings; print(settings.RELEVANT_CLASSES)"
```

### Database Connection Issues
```bash
# Check database
docker compose exec db pg_isready

# Check Redis
docker compose exec redis redis-cli ping

# Restart containers
docker compose restart db redis
```

---

## Testing

### Test AI Service Config
```bash
cd ai-service
source venv/bin/activate

# Load config
python -c "
from app.config import settings
print('RELEVANT_CLASSES:', settings.RELEVANT_CLASSES)
print('AI_SERVICE_PORT:', settings.AI_SERVICE_PORT)
print('INFERENCE_IMAGE_SIZE:', settings.INFERENCE_IMAGE_SIZE)
print('AUTO_DOWNLOAD_MODEL:', settings.AUTO_DOWNLOAD_MODEL)
"
```

### Test Severity Functions
```bash
python -c "
from app.severity import compute_severity

detections = [
    {'label': 'bottle', 'confidence': 0.8, 'box': [10, 20, 100, 120]},
    {'label': 'cup', 'confidence': 0.75, 'box': [30, 40, 90, 110]},
]

waste_detected, severity, confidence = compute_severity(detections)
print(f'Waste: {waste_detected}, Severity: {severity}, Confidence: {confidence}')
"
```

---

## Documentation

### Read These First
1. **COMPLETE_FIX_REPORT.md** - Executive summary of all fixes
2. **SYSTEM_FIX_CHECKLIST.md** - Verification tests
3. **QUICK_REFERENCE_CHANGES.md** - What was changed

### Detailed References
- **AI_SERVICE_BUG_REPORT.md** - Bug analysis
- **AI_SERVICE_FIX_SUMMARY.md** - Technical details
- **DETAILED_CHANGE_LOG.md** - All changes

### Code Documentation
- `ai-service/app/config.py` - Configuration with detailed comments
- `ai-service/app/severity.py` - Severity scoring functions
- `ai-service/.env` - Environment variable documentation

---

## Quick Commands

```bash
# Start everything
./start-dev.sh

# Stop everything
./stop-dev.sh

# View all service logs
tail -f logs/*.log

# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Access database
docker compose exec db psql -U cleangrid cleangrid

# Access Redis
docker compose exec redis redis-cli

# Run tests
./start-dev.sh  # Auto-runs tests on startup

# Clean up
pkill -f "python.*uvicorn\|python.*main.py\|npm run dev"
rm -rf backend/venv ai-service/venv
```

---

## What's Working

✅ All services running  
✅ AI Service configuration loaded correctly  
✅ Severity scoring working  
✅ Inference engine initialized  
✅ Backend API responding  
✅ Frontend compiling  
✅ Database connected  
✅ Redis connected  
✅ All tests passing  

---

## What's Next

- Start developing new features
- Test with real waste detection images
- Integrate with camera systems
- Deploy to production
- Monitor performance

---

## Support

If you encounter issues:
1. Check logs: `tail -f logs/*.log`
2. Review: `COMPLETE_FIX_REPORT.md`
3. Test config: `python -c "from app.config import settings; print(settings)"`
4. Restart services: `pkill -f ...; ./start-dev.sh`

---

## Success Indicators

When everything is working, you should see:
```
[TIME] Starting CleanGrid Development Environment...
[TIME] Database is ready!
[TIME] Redis is ready!
[TIME] Backend dependencies installed
[TIME] AI Service dependencies installed
[TIME] AI Service is ready!
[TIME] Backend is ready!
[TIME] Frontend is ready!
[TIME] CleanGrid Development Environment is ready!
```

And curl to health endpoints should return:
```json
AI Service: {"status":"healthy","model_loaded":true,"version":"1.0.0"}
Backend: {"status":"healthy","version":"1.0.0","phase":"0 - Validation"}
```

---

**You're all set! The system is ready to use. 🎉**

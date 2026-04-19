# 🗑️ CleanGrid — AI-Powered Smart Waste Management System

**Transforming waste management from reactive schedules to real-time, AI-guided cleanup operations**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-red.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 Vision

CleanGrid is a web-first, AI-powered smart waste operations platform that enables municipalities, waste management teams, and citizen reporters to:

- **🤖 Detect** garbage using AI image analysis
- **📍 Visualize** incidents on an interactive map  
- **⚡ Prioritize** cleanup tasks intelligently
- **🚛 Optimize** collection routes dynamically
- **✅ Verify** cleanup completion with before/after proof

The platform closes the full operational loop: **waste reported → waste mapped → priority assessed → crew dispatched → cleanup verified → contributor rewarded**.

---

## ✨ Key Features

### 🚀 Phase 1: Core Reporting Loop (100% Complete)
- **AI-Powered Detection**: YOLOv8n image analysis with severity scoring
- **Interactive Mapping**: PostGIS-powered map with clustering and heatmaps
- **Real-time Updates**: Server-sent events for live incident tracking
- **Citizen Reporting**: Mobile-responsive report submission with photo upload
- **Gamification**: Points system with leaderboards and achievement badges

### 🔐 Phase 2: Authentication & Admin (In Progress)
- **Secure Authentication**: Stateless JWT with HttpOnly cookies
- **Role-Based Access**: Citizen, Crew, and Admin role management
- **Admin Dashboard**: Real-time statistics and incident management
- **Token Rotation**: Refresh token system with Redis blacklisting
- **Protected Routes**: Server-side admin guards with proper redirects

---

## 🏗️ Technical Architecture

### Frontend Stack
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand + TanStack Query (React Query v5)
- **Mapping**: Leaflet.js + react-leaflet with OpenStreetMap tiles
- **Deployment**: Vercel (one-command deployment)

### Backend Stack  
- **Framework**: FastAPI with async/await patterns
- **Database**: PostgreSQL 15 + PostGIS 3.3 for spatial queries
- **ORM**: SQLAlchemy 2.0 async with Alembic migrations
- **Authentication**: JWT + bcrypt with HttpOnly Secure cookies
- **Caching**: Redis 7 for session management and rate limiting

### AI Service
- **Model**: YOLOv8n (Ultralytics) for object detection
- **Architecture**: Isolated microservice with FastAPI
- **Inference**: CPU-optimized with GPU support option
- **Classes**: Bottle, cup, bag, banana, can, backpack, suitcase

### Infrastructure
- **Containerization**: Docker Compose with multi-stage builds
- **File Storage**: Cloudflare R2 (S3-compatible, no egress fees)
- **Routing API**: OpenRouteService with nearest-neighbor fallback
- **Monitoring**: Structured logging with health checks

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Clone & Setup
```bash
git clone https://github.com/kankan223/clean-grid.git
cd clean-grid
```

### 2. Environment Configuration
```bash
# Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit with your configuration
# Backend: Database URL, Redis URL, JWT secrets
# Frontend: API URL, Next.js settings
```

### 3. Start Development Stack

**Option 1: Unified Startup Script (Recommended)**
```bash
# Start all services automatically in correct order
./start-dev.sh

# Stop all services
./stop-dev.sh
```

**Option 2: Manual Startup**
```bash
# Start infrastructure
docker compose up -d postgres redis ai-service

# Run migrations and start backend
cd backend
source venv/bin/activate
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. python app/main.py

# Start frontend (in separate terminal)
cd frontend
npm run dev
```

### 4. Database Setup
```bash
# Run database migrations
cd backend
source venv/bin/activate
PYTHONPATH=. alembic upgrade head

# Seed with sample data (optional)
python seed/seed_incidents.py
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs
- **Admin Dashboard**: http://localhost:3000/admin
- **AI Service**: http://localhost:8001

---

## 🔐 Security Architecture

### Authentication System
CleanGrid uses a **stateless JWT + HttpOnly cookie** system:

- **Access Tokens**: 15-minute expiry, stored in HttpOnly cookies
- **Refresh Tokens**: 7-day expiry with rotation and Redis blacklisting
- **Cookie Security**: Secure + SameSite=Strict + HttpOnly flags
- **Password Security**: bcrypt hashing with cost factor 12

### Role-Based Access Control
- **Citizen**: Can report incidents and view public data
- **Crew**: Can manage assigned incidents and view restricted data
- **Admin**: Full system access with dashboard and user management

### API Security
- **CORS**: Configured for frontend domain
- **Rate Limiting**: Redis-based request throttling
- **Input Validation**: Pydantic schemas for all endpoints
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

---

## 🛡️ Development Guardrails

### Anti-Hallucination Rules (NEVER VIOLATE)
1. **Database**: Use SQLAlchemy 2.0 async, NOT Prisma
2. **Maps**: Use Leaflet.js + OpenStreetMap, NOT Mapbox
3. **Real-time**: Use Server-Sent Events, NOT WebSockets
4. **Routing**: Use OpenRouteService API, NOT custom TSP solver
5. **Next.js**: Dynamic Leaflet import with `ssr: false`
6. **Auth**: Use HttpOnly cookies, NOT localStorage JWTs
7. **AI**: Use YOLOv8n, NOT heavy models
8. **Storage**: Use Cloudflare R2, NOT AWS S3
9. **State**: Use Zustand, NOT Redux
10. **API Calls**: Use TanStack Query, NOT useEffect fetching

### Implementation Boundaries
- **MVP Scope**: Core loop only (Report → AI → Map → Assign → Route → Verify)
- **No IoT**: Smart bin hardware integration out of scope
- **No Native Apps**: Mobile-responsive web only
- **No Blockchain**: Points use simple database ledger
- **No Drone Routing**: Ground vehicle routing only

---

## 📚 Documentation Structure

- **`README.md`** - This file (master documentation)
- **`docs/PRD.md`** - Product Requirements Document
- **`docs/tech-stake.md`** - Technical architecture decisions
- **`project-brain.md`** - Working memory and guardrails
- **`implementation-roadmap.md`** - Detailed implementation plan

---

## 🤝 Contributing

### Development Workflow
1. **Read the Guardrails**: Review `project-brain.md` Section 4
2. **Check Current Phase**: See `implementation-roadmap.md` for active tasks
3. **Follow Architecture**: Adhere to `tech-stake.md` stack decisions
4. **Test Thoroughly**: Run validation scripts before committing

### Code Quality
- All database changes must include Alembic migrations
- All API endpoints must have Pydantic validation
- All frontend components must be responsive
- All AI models must be tested with sample images

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Ultralytics** - YOLOv8n model and training framework
- **OpenStreetMap** - Free map tiles and geocoding service
- **OpenRouteService** - Route optimization API
- **FastAPI** - Modern, fast web framework for building APIs
- **Next.js** - React framework with server-side rendering

---

## 📞 Support

For questions, issues, or contributions:

- 📧 **Email**: support@cleangrid.dev
- 🐛 **Issues**: [GitHub Issues](https://github.com/kankan223/clean-grid/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/kankan223/clean-grid/discussions)

---

**Built with ❤️ for cleaner cities and smarter waste management**

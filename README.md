# eidosSec - AI-Powered Security Scanner

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)

> **Comprehensive security scanner with 50+ tools, AI-powered explanations, and automated fix suggestions**

🚀 **Status:** Month 1 Development - Infrastructure Setup Complete

---

## 🎯 Features

### FREE Tier
- ✅ **15 Essential Security Tools** - SAST, SCA, Secrets detection
- ✅ **Quick Scan Mode** - Complete scan in ~10 minutes
- ✅ **3 Projects** - Scan up to 3 codebases
- ✅ **10 Scan History** - Keep last 10 scan results
- ✅ **JSON Export** - Export findings programmatically

### PRO Tier ($39/month)
- 🔥 **50+ Premium Tools** - DAST, Container, IaC, API security
- 🔥 **Deep Scan Mode** - Comprehensive analysis with all tools
- 🔥 **AI Explanations** - Plain language vulnerability descriptions
- 🔥 **Auto-Fix Suggestions** - AI-generated code patches
- 🔥 **Unlimited Projects & Scans** - No limits
- 🔥 **PDF/HTML/SARIF Export** - Professional reports
- 🔥 **GitHub/GitLab PR Creation** - Automated fix PRs
- 🔥 **Team Collaboration** - Multi-user, roles, comments

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│              Docker Compose Stack                │
│                                                  │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐        │
│  │Frontend │  │ Backend │  │ Scanner  │        │
│  │(React)  │  │(FastAPI)│  │(50 tools)│        │
│  │  :3000  │  │  :8000  │  │          │        │
│  └────┬────┘  └────┬────┘  └─────┬────┘        │
│       │            │              │             │
│  ┌────┴────────────┴──────────────┴────┐       │
│  │         PostgreSQL + Redis           │       │
│  │           :5432      :6379           │       │
│  └──────────────────────────────────────┘       │
└──────────────────────────────────────────────────┘
```

**Components:**
- **Frontend:** React 18 + TypeScript + TailwindCSS + shadcn/ui
- **Backend:** FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2
- **Scanner:** Python worker with 50+ security tools
- **Queue:** Celery + Redis for async task processing
- **Database:** PostgreSQL 15 with JSONB for flexible schemas
- **WebSocket:** Real-time scan progress updates

---

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git 2.30+
- 8GB RAM minimum (16GB recommended)

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/eidossec/eidossec.git
   cd eidossec
   ```

2. **Set up environment**
   ```bash
   cp .env.template .env
   # Edit .env and set secure passwords
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Open browser**
   ```
   http://localhost:3000
   ```

### First Scan

1. Click **"New Project"**
2. Enter project name and path (e.g., `/path/to/your/code`)
3. Click **"Quick Scan"**
4. Wait 5-10 minutes for results
5. Review findings with severity, file, and line numbers

---

## 🛠️ Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Run tests:**
```bash
pytest tests/ -v
ruff check .
mypy app/
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:3000
```

**Run tests:**
```bash
npm test
npm run lint
npm run type-check
```

### Scanner Development

```bash
cd scanner
pip install -r requirements.txt
# Scanner runs as Celery worker via docker-compose
```

---

## 📚 Documentation

- **[Implementation Spec](./Implementarion-spec.md)** - Technical architecture and API specs
- **[Milestone Development](./milestone_development.md)** - 12-month roadmap with progress tracking
- **[Master Plan](./MasterPlan.md)** - Business strategy and market analysis
- **[Business Model](./Business_model.md)** - Pricing and revenue model

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-02-02T00:00:00Z"
}
```

### Database Status

```bash
docker-compose exec postgres psql -U eidossec -d eidossec -c "\dt"
```

Expected tables: `projects`, `scans`, `findings`, `alembic_version`

---

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PASSWORD` | PostgreSQL password | `eidossec_password_change_in_production` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | Required |
| `OPENAI_API_KEY` | OpenAI for AI features (optional) | - |
| `GITHUB_TOKEN` | GitHub for auto-PR (optional) | - |
| `ENABLE_AI_FEATURES` | Enable/disable AI features | `false` |

### Resource Limits

Defined in `docker-compose.yml`:

- **Scanner:** 4 CPU, 8GB RAM max (adjustable)
- **Celery:** 2 concurrent workers (adjustable)
- **PostgreSQL:** Unlimited (uses named volume)
- **Redis:** Unlimited (uses AOF persistence)

---

## 📦 Project Structure

```
eidosSec/
├── backend/              # FastAPI application
│   ├── alembic/          # Database migrations
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Security, config
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── main.py       # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React application
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # API client, utils
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── scanner/              # Security tools worker
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml    # Production config
├── docker-compose.dev.yml # Development overrides
└── .env.template         # Environment template
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

**Development standards:**
- Backend: Follow PEP 8, use type hints, write tests
- Frontend: ESLint + Prettier, TypeScript strict mode
- Commits: Conventional commits (`feat:`, `fix:`, `docs:`)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with amazing open-source tools:
- [Semgrep](https://semgrep.dev/) - SAST engine
- [Trivy](https://trivy.dev/) - Container & dependency scanner
- [TruffleHog](https://trufflesecurity.com/) - Secrets detection
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library

---

## 📧 Support

- **Documentation:** [docs.eidossec.com](https://docs.eidossec.com) *(coming soon)*
- **Discord:** [discord.gg/eidossec](https://discord.gg/eidossec) *(coming soon)*
- **Email:** support@eidossec.com

---

**Made with ❤️ by the eidosSec team**

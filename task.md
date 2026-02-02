# Month 4 Implementation Task - Stabilize + PRO Prep

**Phase:** Month 4 (Stability & PRO Infrastructure)
**Duration:** 67 hours remaining (~17 hours/week)
**Goal:** Stable FREE tier + infrastructure ready for 60+ tools
**Status:** NO PUBLIC LAUNCH - Internal development only

---

## Reference Documents

- `milestone_development.md` - Month 4 breakdown
- `docs/PRO_TOOLS_MATRIX.md` - Full 63 tools list
- `docs/PRO_LICENSE_SPEC.md` - License system design
- `docs/ONBOARDING_OPTIMIZATION.md` - UX improvements

---

## Week 2: Onboarding Optimization (20 hours)

### 2.1 Platform-Aware Path Input (2h)
**File:** `frontend/src/pages/NewProject.tsx`

| Task | Hours | Status |
|------|-------|--------|
| Detect OS via `navigator.platform` | 0.5h | ⏸️ |
| Update placeholder based on OS | 0.5h | ⏸️ |
| Add path format hint text | 0.5h | ⏸️ |
| Test on Windows + Linux | 0.5h | ⏸️ |

### 2.2 Auto-Scan Checkbox (3h)
**Files:** `frontend/src/pages/NewProject.tsx`, `backend/app/routers/projects.py`

| Task | Hours | Status |
|------|-------|--------|
| Add checkbox UI in Step 3 | 1h | ⏸️ |
| Pass `auto_scan` flag to create endpoint | 0.5h | ⏸️ |
| Backend: trigger scan after project creation | 1h | ⏸️ |
| Redirect to scan page if auto_scan=true | 0.5h | ⏸️ |

### 2.3 Zero Findings Celebration (2h)
**File:** `frontend/src/pages/ScanDetails.tsx`

| Task | Hours | Status |
|------|-------|--------|
| Add success state UI component | 1h | ⏸️ |
| Show when findings.length === 0 && status === 'completed' | 0.5h | ⏸️ |
| Add "Run Deep Scan" CTA (for future PRO) | 0.5h | ⏸️ |

### 2.4 Real Language Detection Endpoint (6h)
**Files:** `backend/app/routers/projects.py`, `backend/app/services/detector.py`

| Task | Hours | Status |
|------|-------|--------|
| Create `POST /api/v1/projects/detect` endpoint | 1h | ⏸️ |
| Implement language detection (file extensions) | 2h | ⏸️ |
| Implement framework detection (config files) | 2h | ⏸️ |
| Update frontend to call detect endpoint | 1h | ⏸️ |

### 2.5 Tool Progress Visibility (5h)
**Files:** `frontend/src/pages/ScanDetails.tsx`, WebSocket messages

| Task | Hours | Status |
|------|-------|--------|
| Update WebSocket message format to include tool list | 1h | ⏸️ |
| Create ToolProgressList component | 2h | ⏸️ |
| Show tool status (pending/running/completed/failed) | 1.5h | ⏸️ |
| Style with icons and animations | 0.5h | ⏸️ |

### 2.6 Error Handling Improvements (2h)
**Files:** Multiple frontend components

| Task | Hours | Status |
|------|-------|--------|
| Standardize error toast component | 1h | ⏸️ |
| Add user-friendly error messages | 0.5h | ⏸️ |
| Add retry buttons where appropriate | 0.5h | ⏸️ |

---

## Week 3: Documentation & Content (22 hours)

### 3.1 Installation Guide Polish (4h)
**File:** `docs/installation.md`

| Task | Hours | Status |
|------|-------|--------|
| Windows installation steps | 1h | ⏸️ |
| Linux (Ubuntu/Debian) steps | 1h | ⏸️ |
| macOS steps | 1h | ⏸️ |
| Troubleshooting section | 1h | ⏸️ |

### 3.2 API Documentation (6h)
**File:** `backend/app/main.py`, OpenAPI config

| Task | Hours | Status |
|------|-------|--------|
| Add OpenAPI descriptions to all endpoints | 2h | ⏸️ |
| Add request/response examples | 2h | ⏸️ |
| Generate and review Swagger UI | 1h | ⏸️ |
| Export OpenAPI JSON for docs site | 1h | ⏸️ |

### 3.3 Tool Documentation (6h)
**File:** `docs/tools.md` (new)

| Task | Hours | Status |
|------|-------|--------|
| Document all 15 FREE tools | 3h | ⏸️ |
| What each tool detects | 1h | ⏸️ |
| Sample findings for each | 1h | ⏸️ |
| Links to official docs | 1h | ⏸️ |

### 3.4 Blog Post Polish (4h)
**File:** `docs/blog/why-startups-need-security-scanner.md`

| Task | Hours | Status |
|------|-------|--------|
| Review and polish existing draft | 2h | ✅ Created |
| Add screenshots | 1h | ⏸️ |
| SEO optimization (meta, keywords) | 1h | ⏸️ |

### 3.5 README Polish (2h)
**File:** `README.md`

| Task | Hours | Status |
|------|-------|--------|
| Update feature list | 0.5h | ⏸️ |
| Add GIF demo | 1h | ⏸️ |
| Add badges (build, license, etc.) | 0.5h | ⏸️ |

---

## Week 4: PRO Infrastructure Prep (25 hours)

### 4.1 Tool Wrapper Base Class (6h)
**File:** `scanner/tools/base.py`

| Task | Hours | Status |
|------|-------|--------|
| Create abstract `BaseTool` class | 2h | ⏸️ |
| Define standard interface: `run()`, `parse()`, `normalize()` | 2h | ⏸️ |
| Add tier checking: `is_pro_tool` property | 1h | ⏸️ |
| Migrate existing tools to new base class | 1h | ⏸️ |

### 4.2 Output Normalizer (6h)
**File:** `scanner/normalizer.py`

| Task | Hours | Status |
|------|-------|--------|
| Define internal Finding schema | 1h | ⏸️ |
| Create SARIF parser | 2h | ⏸️ |
| Create JSON parser (generic) | 1h | ⏸️ |
| Map CWE/OWASP categories | 2h | ⏸️ |

### 4.3 License Check Scaffolding (4h)
**File:** `backend/app/services/license_service.py`

| Task | Hours | Status |
|------|-------|--------|
| Create LicenseService skeleton | 1h | ⏸️ |
| Implement `get_current_tier()` (returns "free" for now) | 1h | ⏸️ |
| Implement `is_tool_allowed(tool_name)` | 1h | ⏸️ |
| Add `@require_pro` decorator for future use | 1h | ⏸️ |

### 4.4 Docker Multi-Stage Prep (5h)
**File:** `scanner/Dockerfile`

| Task | Hours | Status |
|------|-------|--------|
| Design multi-stage build structure | 1h | ⏸️ |
| Stage 1: Python tools | 1h | ⏸️ |
| Stage 2: Go tools | 1h | ⏸️ |
| Stage 3: Ruby/Node tools | 1h | ⏸️ |
| Test build and measure size | 1h | ⏸️ |

### 4.5 CI/CD for Scanner Image (4h)
**File:** `.github/workflows/scanner.yml`

| Task | Hours | Status |
|------|-------|--------|
| Update workflow for multi-stage build | 1h | ⏸️ |
| Add caching for faster builds | 1h | ⏸️ |
| Push to GitHub Container Registry | 1h | ⏸️ |
| Add image size check (fail if > 8GB) | 1h | ⏸️ |

---

## Success Criteria

- ✅ All 15 FREE tools working reliably (no crashes)
- ✅ Time to first scan < 5 minutes
- ✅ Onboarding improvements deployed
- ✅ Documentation complete and accurate
- ✅ Tool wrapper architecture ready for Month 5 expansion
- ✅ License service skeleton in place
- ✅ Docker multi-stage build working

---

## Implementation Order (Start Here)

### Priority 1: Quick Wins (Today)
1. ⏸️ Platform-aware path input (2h)
2. ⏸️ Auto-scan checkbox (3h)
3. ⏸️ Zero findings celebration (2h)

### Priority 2: Backend Improvements
4. ⏸️ Real language detection endpoint (6h)
5. ⏸️ Tool progress visibility (5h)
6. ⏸️ Error handling improvements (2h)

### Priority 3: Documentation
7. ⏸️ Installation guide (4h)
8. ⏸️ API documentation (6h)
9. ⏸️ Tool documentation (6h)
10. ⏸️ README polish (2h)

### Priority 4: PRO Infrastructure
11. ⏸️ Tool wrapper base class (6h)
12. ⏸️ Output normalizer (6h)
13. ⏸️ License check scaffolding (4h)
14. ⏸️ Docker multi-stage prep (5h)
15. ⏸️ CI/CD updates (4h)

---

## Tech Stack Reference

**Frontend:**
- React 18 + TypeScript
- TailwindCSS + shadcn/ui
- TanStack Query (React Query)
- React Router DOM

**Backend:**
- FastAPI + Python 3.11
- SQLAlchemy + Alembic
- Celery + Redis
- WebSocket (fastapi-websocket)

**Scanner:**
- Docker container
- 15 security tools (see PRO_TOOLS_MATRIX.md)

---

**Created:** 2026-02-03
**Last Updated:** 2026-02-03

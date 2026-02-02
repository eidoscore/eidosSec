# Month 3 Implementation Task - eidosSec UI + Launch

**Phase:** Month 3 (UI + Launch)  
**Duration:** 84 hours (~21 hours/week)  
**Goal:** FREE tier ready for public launch  

---

## Reference Documents

Before starting, review these documents:
- ✅ `milestone_development.md` - Month 3 Week 1-4 breakdown (lines 285-332)
- ✅ `Implementarion-spec.md` - Section 4 (Backend API), Section 5 (Frontend)
- ✅ `MasterPlan.md` - FREE tier features, user personas
- ✅ `Business_model.md` - FREE tier value proposition

---

## Week 1-2: Core UI Components (57 hours)

### Backend APIs Required

| API Endpoint | Method | Description | Hours | Status |
|-------------|--------|-------------|-------|--------|
| `/api/v1/projects` | POST | Create project | 3h | ⏸️ |
| `/api/v1/projects` | GET | List projects | 2h | ⏸️ |
| `/api/v1/projects/{id}` | GET | Get project details | 2h | ⏸️ |
| `/api/v1/projects/{id}` | DELETE | Delete project | 2h | ⏸️ |
| `/api/v1/scans` | POST | Start scan (enqueue Celery) | 4h | ⏸️ |
| `/api/v1/scans/{id}` | GET | Get scan status | 2h | ⏸️ |
| `/api/v1/scans/{id}/findings` | GET | List findings (paginated) | 4h | ⏸️ |
| `/api/v1/findings/{id}` | GET | Finding detail | 2h | ⏸️ |
| `/api/v1/findings/{id}` | PATCH | Update finding status | 2h | ⏸️ |
| `/ws/scan-progress` | WS | WebSocket for real-time updates | 4h | ⏸️ |

**Total Backend:** 27 hours

### Frontend Components Required

| Component | Description | Hours | Status |
|-----------|-------------|-------|--------|
| **Dashboard Page** | Project list, stats, "New Project" button | 6h | ⏸️ |
| **Add Project Wizard** | 3-step: path → detect language → confirm | 8h | ⏸️ |
| **Scan Progress Page** | Progress bar, tool status, polling/WebSocket | 8h | ⏸️ |
| **Results Page** | Findings list, severity badges, filters | 10h | ⏸️ |
| **Finding Detail Modal** | Code snippet, CWE info, remediation | 8h | ⏸️ |

**Total Frontend:** 40 hours

---

## Week 3-4: Polish + Launch Prep (27 hours)

| Task | Description | Hours | Status |
|------|-------------|-------|--------|
| **Export JSON** | Export findings to JSON | 4h | ⏸️ |
| **Documentation Site** | Docusaurus setup | 8h | ⏸️ |
| **README Polish** | GIFs, screenshots, badges | 4h | ⏸️ |
| **Landing Page** | Hero, features, CTA | 6h | ⏸️ |
| **Launch Video** | Loom 3-min demo | 5h | ⏸️ |

---

## Implementation Order (Priority)

### Phase 1: Backend Foundation (Days 1-3)
1. Create project service + router
2. Create scan service + router  
3. Create findings service + router
4. WebSocket endpoint for progress

### Phase 2: Frontend Core (Days 4-8)
1. Dashboard page with project list
2. Add Project wizard
3. Scan progress with polling
4. Results page with finding list
5. Finding detail modal

### Phase 3: Integration (Days 9-10)
1. Connect frontend to backend APIs
2. Test end-to-end scan flow
3. Fix bugs

### Phase 4: Polish (Days 11-14)
1. Export functionality
2. Documentation
3. README + Landing page
4. Launch video

---

## Success Criteria

- ✅ User can create project via UI
- ✅ User can start Quick Scan, see real-time progress
- ✅ Results display after scan completes (5-10 min)
- ✅ All 73 unit tests still passing
- ✅ CI/CD build successful
- ✅ Documentation complete (README, installation guide)

---

## Notes for AI Agent

**When implementing:**
1. Start with backend APIs first (they're needed by frontend)
2. Use existing schemas from `scanner/app/schemas.py` as reference
3. Frontend uses: React 18 + TypeScript + TailwindCSS + shadcn/ui
4. Backend uses: FastAPI + SQLAlchemy + Celery + Redis
5. WebSocket for real-time scan progress updates
6. All API responses follow Pydantic schemas in Implementarion-spec.md Section 4.5

**Testing:**
- Backend: `pytest backend/tests/`
- Frontend: `npm test` (if tests exist)
- Integration: Manual test via UI

**Commit message format:**
```
feat: Add [feature name]

- [Brief description]
- [Another point]
```

---

**Created:** 2026-02-02  
**Next Review:** After Week 2 completion

# eidosSec - Development Milestone & Roadmap

**Complete 12-Month Development Plan**  
**Model:** 2-Tier (FREE + PRO at $39/month)  
**Strategy:** Build FREE first, validate, then add PRO features

---

## 📊 PROGRESS TRACKING

**Last Updated:** 2026-02-04T00:30:00+07:00  
**Current Status:** Month 1-5 Testing Complete & All Critical Issues Fixed ✅  
**Current Phase:** Month 4 (Completed) ✅ | Month 5 (Testing Completed) ✅

### Legend
- ⏸️ Not Started
- 🔄 In Progress
- ✅ Completed
- ⚠️ Blocked
- 🔀 Revised (scope changed)

### Overall Progress

| Month | Focus | Status | Hours Complete | Total Hours | % Complete |
|-------|-------|--------|----------------|-------------|------------|
| **Month 1** | Foundation | ✅ Completed | 114 | 114 | 100% |
| Month 2 | FREE Tier Tools | ✅ Completed | 65 | 65 | 100% |
| **Month 3** | UI + Launch | ✅ Completed | 84 | 84 | 100% |
| Month 4 | Stabilize + PRO Prep | ✅ Completed | 92 | 92 | 100% |
| Month 5 | PRO Tools (45 new) | ✅ Completed | 80 | 80 | 100% |
| Month 6 | PRO Tools + Payment | ⏸️ Not Started | 0 | 140 | 0% |
| Month 7 | 🚀 PUBLIC LAUNCH + Auto-Fix | ⏸️ Not Started | 0 | 94 | 0% |
| Month 8 | Enterprise | ⏸️ Not Started | 0 | 106 | 0% |
| Month 9 | Optimization | ⏸️ Not Started | 0 | 88 | 0% |
| Month 10 | Polish | ⏸️ Not Started | 0 | 84 | 0% |
| Month 11 | Marketing | ⏸️ Not Started | 0 | 62 | 0% |
| Month 12 | Scale | ⏸️ Not Started | 0 | 66 | 0% |
| **TOTAL** | **Year 1** | **🔄** | **288** | **1,075** | **26.8%** |

> **Revision Note (2026-02-03):**
> - Month 4 revised: NO public launch, focus on stability + PRO infrastructure prep
> - Month 5-6 EXPANDED to include 60+ tools total (was 23)
> - Month 7: PUBLIC LAUNCH moved here (product complete with 63 tools)
> - All tools 100% FREE & open-source, no API keys required
> - PRO tier: SAST (18), DAST (10), Secrets (6), SCA (10), Container (7), IaC (8), API (3), Mobile (1)

### Detailed Task Status - Month 1

#### Week 1-2: Infrastructure Setup (38/38 hours) ✅

| Task | Status | Hours | Notes |
|------|--------|-------|-------|
| Docker Compose setup | ✅ | 8/8 | 5 services configured with health checks |
| PostgreSQL schema v1 | ✅ | 6/6 | Projects, scans, findings tables |
| Redis setup | ✅ | 2/2 | Pub/sub and cache configured |
| FastAPI skeleton | ✅ | 8/8 | Health endpoint, models, schemas, migrations |
| React + Vite setup | ✅ | 6/6 | TypeScript, TailwindCSS, API client, Dashboard |
| Alembic migrations | ✅ | 4/4 | Initial schema migration ready |
| GitHub repo + CI/CD | ✅ | 4/4 | 3 workflows (backend, frontend, scanner) |

#### Week 3-4: Scanner Core + First 5 Tools (76/76 hours) ✅

| Task | Status | Hours | Notes |
|------|--------|-------|-------|
| Scanner Docker image | ✅ | 12/12 | Ubuntu + Python 3.11 + all tool binaries |
| Base tool wrapper class | ✅ | 8/8 | Abstract class with execute() + parse_output() |
| Tool orchestrator | ✅ | 12/12 | Sequential execution, progress tracking to Redis |
| Celery task queue | ✅ | 8/8 | Async scan execution via Redis broker |
| Language detector | ✅ | 6/6 | Detect PHP, Python, JS, Go from file extensions |
| Framework detector | ✅ | 6/6 | Laravel, Django, Express, Rails from config files |
| Semgrep integration | ✅ | 6/6 | SAST multi-language |
| Bandit integration | ✅ | 4/4 | Python SAST |
| TruffleHog integration | ✅ | 4/4 | Secrets detector |
| Gitleaks integration | ✅ | 4/4 | Secrets in git history |
| Trivy integration | ✅ | 6/6 | SCA dependency scanner |

### Development Notes & Blockers

**Current Blockers:** None

**Recent Completions:**
- ✅ Month 1: Infrastructure complete (114 hours)
- ✅ Month 2: 15 Security Tools implemented (65 hours)
  - SAST: Semgrep, Bandit, ESLint, PHPStan, Brakeman (5 tools)
  - SCA: Safety, npm audit, Composer audit, Trivy (4 tools)
  - Secrets: TruffleHog, Gitleaks (2 tools)
  - DAST: OWASP ZAP, Nuclei (2 tools)
  - IaC: cfn-nag, Checkov (2 tools)
  - All 73 unit tests passing
  - CI/CD build successful (image 2.99GB)
- ✅ Month 3: UI + Launch phase completed (84 hours)
- ✅ Month 4: Stabilization & PRO Prep completed (92 hours)
  - End-to-end testing on production server (43.245.249.18)
  - All SAST wrappers fixed (6 tools: Staticcheck, SpotBugs, PMD, ShellCheck, RetireJS, KICS)
  - Celery worker configuration fixed
  - Health check endpoints fixed
  - Pydantic v2 deprecation warnings resolved
  - Integration tests: 4/4 passing with 0 warnings
- ✅ Month 5: PRO Tools testing completed (80 hours)
  - Comprehensive test suite executed
  - Performance: 6ms avg latency (target: <50ms)
  - Stress test: 500 concurrent requests handled
  - Memory leak testing: Stable
  - Security self-scan: Clean

**Next Steps (Month 6 - PRO Features + Payment):**
1. Deep Scan mode implementation
2. License key system (JWT-based)
3. Stripe payment integration
4. AI explanations and auto-fix features

---

## 📋 FOR AI AGENTS: HOW TO USE THIS DOCUMENT

> **If you are an AI agent helping with eidosSec development, read this section first!**

### Required Reading Before Starting ANY Development Task:

1. **THIS FILE (`milestone_development.md`)** - Your primary guide
   - Part 1 (below): Week-by-week roadmap with detailed hours and tasks
   - Part 2 (end of file): Milestones, deliverables, and acceptance criteria

2. **`Implementarion-spec.md`** - Technical reference
   - Read relevant sections for architecture, database schema, API specs
   - Example: Building FastAPI backend? → Read Section 2 (Backend Architecture)
   - Example: Building frontend? → Read Section 5 (Frontend Implementation)

3. **`MasterPlan.md`** - Business context (optional but helpful)
   - Understand WHY we're building features
   - User personas, market analysis, competitive advantage

### How to Start a Development Session:

**Example: Starting Month 1, Week 1-2**

```
1. Read milestone_development.md → Find "MONTH 1: Week 1-2"
2. See tasks: Docker Compose (8h), PostgreSQL schema (6h), FastAPI (8h), etc.
3. Read Implementarion-spec.md → Section 1-3 for technical specs
4. Start coding!
```

**Example: Starting Month 5 (AI Features)**

```
1. Read milestone_development.md → Find "MONTH 5: Week 1-4"
2. See tasks: LLM integration, Stripe payment, license system
3. Read Implementarion-spec.md → Section 4.8 (AI), Section 9.4 (Payment)
4. Read MasterPlan.md → Pricing strategy, why $39/month
5. Start coding!
```

### When Switching Platforms (Antigravity → Windsurf → Cursor):

**No special handoff needed!** Just:
1. Check `git log` to see what previous agent completed
2. Read milestone_development.md to find next tasks
3. Continue where they left off

### Success Criteria = Definition of Done

Each section has **Success Criteria** or **Acceptance Criteria**. Your work is done when:
- ✅ All criteria met
- ✅ Code tested locally
- ✅ Git commit with clear message

---

## 📋 PART 1: DEVELOPMENT ROADMAP (Month-by-Month)

**Philosophy:** Progressive Enhancement

```
Month 1-3: FREE Tier (MVP)
    ↓
Month 4-6: Validate & Polish FREE
    ↓
Month 7-9: Build PRO Features
    ↓
Month 10-12: Scale & Optimize
```

---

## 🗓️ MONTH 1-3: FREE TIER MVP

### **MONTH 1: Foundation**
**Goal:** Infrastructure + Core Scanner Engine

#### Week 1-2: Infrastructure Setup

| Task | Owner | Hours | Deliverable |
|------|-------|-------|-------------|
| **Docker Compose setup** | You | 8 | 5 containers running (frontend, backend, postgres, redis, scanner) |
| **PostgreSQL schema v1** | You + AI | 6 | Tables: users, projects, scans, findings, tools |
| **Redis setup** | You | 2 | Pub/sub for scan progress updates |
| **FastAPI skeleton** | You + AI | 8 | Basic routes, DB connection, health endpoint |
| **React + Vite setup** | You + AI | 6 | Routing, basic layout, Tailwind CSS |
| **Alembic migrations** | You + AI | 4 | Database version control |
| **GitHub repo + CI/CD** | You | 4 | GitHub Actions for lint, test, build |

**Total Week 1-2:** 38 hours  
**Reference:** `Implementarion-spec.md` Section 1-3 (Tech Stack, Architecture, Database)

**Success Criteria:**
- ✅ `docker-compose up` starts all 5 services without errors
- ✅ Backend responds at `http://localhost:8000/health`
- ✅ Frontend loads at `http://localhost:3000`
- ✅ Database migrations run: `alembic upgrade head`
- ✅ CI pipeline runs on every git push

---

#### Week 3-4: Scanner Core + First 5 Tools

| Task | Owner | Hours | Deliverable |
|------|-------|-------|-------------|
| **Scanner Docker image** | You | 12 | Ubuntu + Python 3.11, all tool binaries installed |
| **Base tool wrapper class** | You + AI | 8 | Abstract class with `execute()` + `parse_output()` |
| **Tool orchestrator** | You + AI | 12 | Sequential execution, progress tracking to Redis |
| **Celery task queue** | You | 8 | Async scan execution via Redis broker |
| **Language detector** | You + AI | 6 | Detect PHP, Python, JS, Go from file extensions |
| **Framework detector** | You + AI | 6 | Laravel, Django, Express, Rails from config files |

**Tool Integrations (5 tools):**
1. **Semgrep** (SAST - multi-language) - 6h
2. **Bandit** (Python SAST) - 4h
3. **TruffleHog** (Secrets detector) - 4h
4. **Gitleaks** (Secrets in git history) - 4h
5. **Trivy** (SCA - dependency scanner) - 6h

**Total Week 3-4:** 76 hours  
**Reference:** `Implementarion-spec.md` Section 6 (Scanner Worker), Section 7 (Tool Integration)

**Success Criteria:**
- ✅ Scanner Docker image builds successfully (<3GB)
- ✅ Each tool runs independently and returns JSON
- ✅ Orchestrator executes all 5 tools sequentially
- ✅ Scan results stored in PostgreSQL `findings` table
- ✅ Celery worker picks up scan tasks from Redis queue
- ✅ Scan a test project (DVWA), finds 10+ issues

**Month 1 Total:** 114 hours (~29 hours/week)  
**Deliverable:** Infrastructure ready, scanner can execute 5 tools

---

### **MONTH 2: FREE Tier Tools (15 Essential)**
**Goal:** Integrate 15 tools that FREE tier gets

#### FREE Tier Tool Selection:

| Category | Tools (15 total) | Why These? |
|----------|------------------|------------|
| **SAST (8)** | Semgrep, Bandit, ESLint, PHPStan, Pylint, Brakeman, Flawfinder, NodeJSScan | Cover main languages (Python, JS, PHP, Ruby, C/C++) |
| **SCA (4)** | Trivy, npm audit, pip-audit, composer audit | Dependency scanning for all package managers |
| **Secrets (3)** | TruffleHog, Gitleaks, detect-secrets | Critical for all users |

#### Week 1-2: SAST Tools (21/21 hours) ✅

**New tools implemented (6):**
- ✅ ESLint (JavaScript) - 4h
- ✅ PHPStan (PHP) - 4h
- ✅ Pylint (Python) - 3h
- ✅ Brakeman (Ruby/Rails) - 4h
- ✅ Flawfinder (C/C++) - 3h
- ✅ NodeJSScan (JavaScript/Node.js) - 3h

**Total:** 21 hours ✅

---

#### Week 3-4: SCA + Secrets + Deduplication (44/44 hours) ✅

**New SCA tools (3):**
- ✅ npm audit (Node.js SCA) - 3h
- ✅ pip-audit (Python SCA) - 3h
- ✅ composer audit (PHP SCA) - 3h

**New Secrets tool (1):**
- ✅ detect-secrets - 3h

**DAST Tools (2):**
- ✅ OWASP ZAP - 8h
- ✅ Nuclei - 8h

**IaC Tools (2):**
- ✅ cfn-nag (CloudFormation) - 6h
- ✅ Checkov (Multi-IaC) - 10h

**Deduplication Engine:**
- ✅ AST-based similarity matching - 12h
- ✅ Hash-based exact matching - 6h
- ✅ Confidence scoring - 6h
- ✅ Merge logic - 8h

**Total:** 44 hours ✅  
**Reference:** `Implementarion-spec.md` Section 7.6 (Deduplication)

**Success Criteria:**
- ✅ 15 tools total integrated and working
- ✅ Deduplication reduces raw findings by 60%+ (100 raw → 40 unique)
- ✅ Confidence score increases with multiple tool confirmations
- ✅ Security score formula: `10.0 - (severity weights)`

**Month 2 Total:** 65 hours (~16 hours/week)  
**Deliverable:** 15 tools working, basic deduplication

---

### **MONTH 3: FREE Tier UI + Launch**
**Goal:** Functional UI, public launch

#### Week 1-2: Core UI

| Component | Hours | AI Assist | Notes |
|-----------|-------|-----------|-------|
| **Dashboard page** | 6 | ✅ | Project list, stats, "New Project" button |
| **Add Project wizard** | 8 | ✅ | 3-step: path → detect language → confirm |
| **Scan progress page** | 8 | ✅ | Progress bar, tool status, polling (5s intervals) |
| **Results page** | 10 | ✅ | Findings list, severity badges, client-side filters |
| **Finding detail page** | 8 | ✅ | Code snippet (syntax highlighted), CWE, remediation |

**Backend APIs:**
- `POST /api/v1/projects` - Create project (3h)
- `GET /api/v1/projects` - List projects (2h)
- `POST /api/v1/scans` - Start scan (enqueue Celery task) (4h)
- `GET /api/v1/scans/{id}` - Get scan status (2h)
- `GET /api/v1/scans/{id}/findings` - List findings (paginated) (4h)
- `GET /api/v1/findings/{id}` - Finding detail (2h)

**Total:** 57 hours  
**Reference:** `Implementarion-spec.md` Section 4 (Backend API), Section 5 (Frontend)

---

#### Week 3-4: Polish + Launch Prep

| Task | Hours | Notes |
|------|-------|-------|
| **Documentation site** | 8 | Docusaurus: installation, first scan, troubleshooting |
| **README.md (polished)** | 4 | GIFs, screenshots, features list, badges |
| **Landing page** | 6 | Hero, features, CTA ("Get Started Free") |
| **Discord server setup** | 2 | Channels: #general, #support, #feature-requests |
| **Product Hunt listing** | 3 | Title, description, screenshots, tagline |
| **Launch video** | 4 | Loom, 3 min: install → scan → results |

**Total:** 27 hours

**Success Criteria:**
- ✅ User can create project via UI
- ✅ User can start Quick Scan, see real-time progress
- ✅ Results display after scan completes (5-10 min)
- ✅ All documentation complete (README, installation guide, FAQ)
- ✅ Demo video recorded and published

**Month 3 Total:** 84 hours (~21 hours/week)  
**Deliverable:** FREE tier ready to launch publicly

---

### **Month 1-3 Summary:**

| Month | Focus | Hours | Cumulative |
|-------|-------|-------|------------|
| 1 | Infrastructure + Scanner Core | 114 | 114 |
| 2 | 15 Tools + Deduplication | 65 | 179 |
| 3 | UI + Launch Prep | 84 | 263 |

**Total:** 263 hours (~22 hours/week average)

**Deliverable: FREE Tier Launched ✅**

- ✅ 15 essential tools
- ✅ Quick Scan mode (10 min)
- ✅ Basic UI (dashboard, results)
- ✅ Docker Compose deployment
- ✅ Documentation
- ✅ Public launch (Product Hunt, Hacker News)

---

## 🗓️ MONTH 4-6: STABILIZE + BUILD PRO ARSENAL

### **MONTH 4: Internal Testing & PRO Preparation**
**Goal:** Stabilize FREE tier, prepare infrastructure for 60+ tools, NO public launch yet

> [!NOTE]
> Public launch delayed to Month 7 after PRO tier is ready.
> Month 4-6 focus: Build complete product (FREE + PRO) before going public.

#### Week 1: Bug Fixes & Stability (25h) ✅

| Task | Status | Hours | Notes |
|------|--------|-------|-------|
| **End-to-end testing** | ✅ | 8 | Deployment verified on target server |
| **Fix scanner bugs** | ✅ | 10 | Implemented diagnostic agent & error recovery |
| **Fix UI bugs** | ✅ | 4 | Dashboard and results page stabilized |
| **Performance profiling** | ✅ | 3 | Sequential build optimization (RAM) |

**Total:** 25 hours

---

#### Week 2: Onboarding Optimization (20h) ✅

| Task | Status | Hours | Notes |
|------|--------|-------|-------|
| **Platform-aware path input** | ✅ | 2 | Windows vs Linux path placeholders |
| **Auto-scan checkbox** | ✅ | 3 | Start scan immediately after project creation |
| **Zero findings celebration** | ✅ | 2 | Success message when no vulns found |
| **Real language detection** | ✅ | 6 | Backend `/projects/detect` endpoint linked |
| **Tool progress visibility** | ✅ | 5 | ScanDetails shows active tools grid |
| **Error handling improvements** | ✅ | 2 | Better feedback on detection/scan failures |

**Total:** 20 hours

---

#### Week 3: Documentation & Content (22h) ✅

| Task | Status | Hours | Notes |
|------|--------|-------|-------|
| **Installation guide polish** | ✅ | 4 | Windows (WSL2), Linux, macOS instructions |
| **API documentation** | ✅ | 6 | `/docs/api.md` created + Swagger pointer |
| **Tool documentation** | ✅ | 6 | `/docs/tools.md` detailing 15 scan engines |
| **Blog post draft** | ✅ | 4 | "Why every startup needs a security scanner" |
| **README.md polish** | ✅ | 2 | Badges, new links, quick start updated |

**Total:** 22 hours

---

#### Week 4: PRO Infrastructure Prep (25h) 🔄

| Task | Status | Hours | Notes |
|------|--------|-------|-------|
| **Tool wrapper base class** | ✅ | 6 | Standardized diagnostic & shell interface |
| **Output normalizer** | ✅ | 2 | `SarifParser` implemented for unified output |
| **License check scaffolding** | ✅ | 2 | Scaffolding in Monitoring Agent implemented |
| **Docker multi-stage prep** | ✅ | 4 | Scanner Dockerfile refactored to 2 stages |
| **CI/CD for scanner image** | ✅ | 4 | GitHub workflow hardened (timeouts/logs) |

**Total:** 25 hours

---

**Month 4 Success Criteria:**
- ✅ All 15 FREE tools working reliably (no crashes)
- ✅ Time to first scan < 5 minutes
- ✅ Documentation complete and accurate
- ✅ Tool wrapper architecture ready for Month 5 expansion
- ✅ No public launch yet - internal testing only

**Month 4 Total:** 92 hours (~23 hours/week)

---

## 🗓️ MONTH 5-6: PRO Tools Integration (60+ Tools)

**Goal:** Build the most comprehensive FREE & open-source security scanner
**Total New Tools:** 45+ tools (FREE 15 → PRO 60+)
**Estimated Hours:** 160 hours (split across Month 5-6)

> [!NOTE]
> All tools are 100% FREE & open-source (MIT, Apache, GPL licensed).
> No API keys, no usage limits, fully self-hosted.

---

### **MONTH 5: Core PRO Tools (Week 1-4)**

**Focus:** SAST expansion + DAST + Secrets
**Hours:** 80 hours (~20 hours/week)

#### Week 1: SAST - Multi-Language Expansion (20h)

| Tool | Category | Hours | License | Install |
|------|----------|-------|---------|---------|
| **CodeQL** | SAST Multi | 8 | MIT | `gh codeql` |
| **Gosec** | SAST Go | 3 | Apache-2.0 | `go install securego/gosec` |
| **Staticcheck** | SAST Go | 2 | MIT | `go install staticcheck` |
| **SpotBugs** | SAST Java | 4 | LGPL-2.1 | JAR download |
| **PMD** | SAST Java | 3 | BSD-4 | Binary |

#### Week 2: SAST - Language Specific (20h)

| Tool | Category | Hours | License | Install |
|------|----------|-------|---------|---------|
| **Find Security Bugs** | SAST Java | 3 | LGPL-3.0 | SpotBugs plugin |
| **Psalm** | SAST PHP | 3 | MIT | `composer require psalm` |
| **Progpilot** | SAST PHP | 2 | MIT | `composer require progpilot` |
| **Cppcheck** | SAST C/C++ | 3 | GPL-3.0 | `apt install cppcheck` |
| **Infer** | SAST C/Java | 4 | MIT | Binary / Docker |
| **Security Code Scan** | SAST .NET | 3 | LGPL-3.0 | NuGet |
| **cargo-audit** | SAST Rust | 2 | Apache/MIT | `cargo install` |

#### Week 3: DAST - Dynamic Testing (20h)

| Tool | Category | Hours | License | Install |
|------|----------|-------|---------|---------|
| **OWASP ZAP (enhanced)** | DAST | 6 | Apache-2.0 | Docker |
| **Nuclei** | DAST | 4 | MIT | `go install nuclei` |
| **Nikto** | DAST | 3 | GPL-1.0 | `apt install nikto` |
| **SQLMap** | DAST | 4 | GPL-2.0 | `pip install sqlmap` |
| **XSStrike** | DAST | 3 | GPL-3.0 | `pip install xsstrike` |

#### Week 4: Secrets + SCA Expansion (20h)

| Tool | Category | Hours | License | Install |
|------|----------|-------|---------|---------|
| **whispers** | Secrets | 2 | Apache-2.0 | `pip install whispers` |
| **git-secrets** | Secrets | 2 | Apache-2.0 | `brew/apt install` |
| **Talisman** | Secrets | 2 | MIT | Binary |
| **Grype** | SCA | 3 | Apache-2.0 | Binary |
| **OSV-Scanner** | SCA | 2 | Apache-2.0 | `go install osv-scanner` |
| **OWASP Dep-Check** | SCA | 4 | Apache-2.0 | JAR |
| **bundler-audit** | SCA Ruby | 2 | GPL-3.0 | `gem install` |
| **Retire.js** | SCA JS | 2 | Apache-2.0 | `npm install -g retire` |
| **Syft** | SBOM | 1 | Apache-2.0 | Binary |

**Month 5 Total:** 80 hours

---

### **MONTH 6: Advanced Tools + PRO Features (Week 1-4)**

**Focus:** Container, IaC, API, Mobile + Payment/License system
**Hours:** 140 hours (~35 hours/week)

#### Week 1: Container Security (18h)

| Tool | Category | Hours | License | Install |
|------|----------|-------|---------|---------|
| **Grype (images)** | Container | 2 | Apache-2.0 | Same binary |
| **Clair** | Container | 4 | Apache-2.0 | Docker |
| **Dockle** | Container | 2 | Apache-2.0 | Binary |
| **Hadolint** | Container | 2 | GPL-3.0 | Docker |
| **Docker Bench** | Container | 3 | Apache-2.0 | Shell script |
| **kube-bench** | Container | 3 | Apache-2.0 | Binary |
| **Trivy (expand modes)** | Container | 2 | Apache-2.0 | Already have |

#### Week 2: IaC + Cloud Security (20h)

| Tool | Category | Hours | License | Install |
|------|----------|-------|---------|---------|
| **tfsec** | IaC Terraform | 3 | MIT | `go install tfsec` |
| **Terrascan** | IaC Multi | 4 | Apache-2.0 | `go install terrascan` |
| **KICS** | IaC Multi | 4 | Apache-2.0 | Docker / binary |
| **Polaris** | IaC K8s | 3 | Apache-2.0 | Binary |
| **kube-linter** | IaC K8s | 2 | Apache-2.0 | Binary |
| **Prowler** | Cloud AWS | 4 | Apache-2.0 | `pip install prowler` |

#### Week 3: API + Mobile + DAST Advanced (22h)

| Tool | Category | Hours | License | Install |
|------|----------|-------|---------|---------|
| **Arjun** | API | 2 | GPL-3.0 | `pip install arjun` |
| **Kiterunner** | API | 3 | MIT | Binary |
| **Schemathesis** | API | 3 | MIT | `pip install schemathesis` |
| **ffuf** | DAST | 2 | MIT | `go install ffuf` |
| **Wapiti** | DAST | 3 | GPL-2.0 | `pip install wapiti3` |
| **Commix** | DAST | 2 | GPL-3.0 | `pip install commix` |
| **Dalfox** | DAST XSS | 2 | MIT | `go install dalfox` |
| **MobSF** | Mobile | 5 | GPL-3.0 | Docker |

#### Week 4: PRO Features + Payment (80h)

| Feature | Hours | Notes |
|---------|-------|-------|
| **Deep Scan mode** | 12 | Run all 60+ tools, parallel execution, 60 min max |
| **License key system (backend)** | 16 | JWT-based, offline verification |
| **License key enforcement (frontend)** | 12 | Feature gating UI components |
| **Stripe integration** | 16 | Checkout, webhooks, subscription management |
| **Pricing page** | 8 | FREE vs PRO comparison, testimonials |
| **AI explanations** | 8 | Claude API integration |
| **AI fix suggestions** | 8 | Auto-patch generation |

**Month 6 Total:** 140 hours

---

### **Tool Integration Architecture**

```
scanner/
├── tools/
│   ├── sast/
│   │   ├── semgrep.py      ✅ FREE
│   │   ├── bandit.py       ✅ FREE
│   │   ├── eslint.py       ✅ FREE
│   │   ├── phpstan.py      ✅ FREE
│   │   ├── brakeman.py     ✅ FREE
│   │   ├── flawfinder.py   ✅ FREE
│   │   ├── codeql.py       🔒 PRO
│   │   ├── gosec.py        🔒 PRO
│   │   ├── staticcheck.py  🔒 PRO
│   │   ├── spotbugs.py     🔒 PRO
│   │   ├── pmd.py          🔒 PRO
│   │   ├── psalm.py        🔒 PRO
│   │   ├── cppcheck.py     🔒 PRO
│   │   ├── infer.py        🔒 PRO
│   │   └── ...
│   ├── dast/
│   │   ├── zap.py          🔒 PRO
│   │   ├── nuclei.py       🔒 PRO
│   │   ├── nikto.py        🔒 PRO
│   │   ├── sqlmap.py       🔒 PRO
│   │   ├── xsstrike.py     🔒 PRO
│   │   └── ...
│   ├── secrets/
│   │   ├── trufflehog.py   ✅ FREE
│   │   ├── gitleaks.py     ✅ FREE
│   │   ├── detect_secrets.py ✅ FREE
│   │   ├── whispers.py     🔒 PRO
│   │   ├── git_secrets.py  🔒 PRO
│   │   └── talisman.py     🔒 PRO
│   ├── sca/
│   │   ├── trivy.py        ✅ FREE
│   │   ├── npm_audit.py    ✅ FREE
│   │   ├── pip_audit.py    ✅ FREE
│   │   ├── composer_audit.py ✅ FREE
│   │   ├── grype.py        🔒 PRO
│   │   ├── osv_scanner.py  🔒 PRO
│   │   ├── dep_check.py    🔒 PRO
│   │   └── ...
│   ├── container/
│   │   ├── trivy_image.py  🔒 PRO
│   │   ├── grype_image.py  🔒 PRO
│   │   ├── clair.py        🔒 PRO
│   │   ├── dockle.py       🔒 PRO
│   │   ├── hadolint.py     🔒 PRO
│   │   └── ...
│   ├── iac/
│   │   ├── checkov.py      ✅ FREE
│   │   ├── cfn_nag.py      ✅ FREE
│   │   ├── tfsec.py        🔒 PRO
│   │   ├── terrascan.py    🔒 PRO
│   │   ├── kics.py         🔒 PRO
│   │   └── ...
│   ├── api/
│   │   ├── arjun.py        🔒 PRO
│   │   ├── kiterunner.py   🔒 PRO
│   │   └── schemathesis.py 🔒 PRO
│   └── mobile/
│       └── mobsf.py        🔒 PRO
├── orchestrator.py         # Tool selection based on license
├── deduplication.py        # AST-based finding merge
└── confidence.py           # Multi-tool verification scoring
```

---

### **Final Tool Count**

| Tier | Tools | Categories |
|------|-------|------------|
| **FREE** | 15 tools | SAST (6), Secrets (3), SCA (4), IaC (2) |
| **PRO** | 60+ tools | All FREE + SAST (12), DAST (10), Secrets (3), SCA (5), Container (7), IaC (6), API (3), Mobile (1) |

### **PRO Tier Complete Tool List (45 additional)**

**SAST (12 new):**
CodeQL, Gosec, Staticcheck, SpotBugs, PMD, Find Security Bugs, Psalm, Progpilot, Cppcheck, Infer, Security Code Scan, cargo-audit

**DAST (10 new):**
OWASP ZAP, Nuclei, Nikto, SQLMap, XSStrike, Commix, Dalfox, ffuf, Wapiti, Gobuster

**Secrets (3 new):**
whispers, git-secrets, Talisman

**SCA (5 new):**
Grype, OSV-Scanner, OWASP Dependency-Check, bundler-audit, Retire.js, Syft

**Container (7 new):**
Grype (images), Clair, Dockle, Hadolint, Docker Bench, kube-bench, Trivy (expanded)

**IaC (6 new):**
tfsec, Terrascan, KICS, Polaris, kube-linter, Prowler

**API (3 new):**
Arjun, Kiterunner, Schemathesis

**Mobile (1 new):**
MobSF

---

### Success Criteria Month 5-6

- ✅ All 60+ tools integrated and producing SARIF/JSON output
- ✅ Deduplication engine handles cross-tool correlation
- ✅ Docker multi-stage build keeps image < 8GB
- ✅ Quick Scan (FREE): 15 tools, < 10 min
- ✅ Deep Scan (PRO): 60+ tools, < 60 min
- ✅ License system validates tool access
- ✅ Stripe payment flow working
- ✅ AI features functional (explain + fix suggestions)

---

### **Month 4-6 Summary:**

| Month | Focus | Hours | Cumulative |
|-------|-------|-------|------------|
| 4 | Stabilize FREE + PRO Prep (NO LAUNCH) | 92 | 355 |
| 5 | PRO Tools (SAST, DAST, Secrets, SCA) | 80 | 435 |
| 6 | PRO Tools (Container, IaC, API) + Payment | 140 | 575 |

**Total Month 4-6:** 312 hours (~26 hours/week average)

> **Strategy Change:** Public launch moved to Month 7.
> Month 4-6 builds complete product (FREE 15 + PRO 48 = 63 tools) before any marketing.

**Deliverable: PRO Tier Launched with 60+ Tools ✅**

- ✅ **60+ tools** total (FREE 15 + PRO 45)
- ✅ Deep Scan mode runs all tools in parallel
- ✅ AI features (explain, auto-fix)
- ✅ Payment integration (Stripe)
- ✅ License key system (JWT, offline-capable)
- ✅ Pricing page live

**Tool Categories:**
| Category | FREE | PRO | Total |
|----------|------|-----|-------|
| SAST | 6 | +12 | 18 |
| DAST | 0 | +10 | 10 |
| Secrets | 3 | +3 | 6 |
| SCA | 4 | +6 | 10 |
| Container | 0 | +7 | 7 |
| IaC | 2 | +6 | 8 |
| API | 0 | +3 | 3 |
| Mobile | 0 | +1 | 1 |
| **TOTAL** | **15** | **+48** | **63** |

---

## 🗓️ MONTH 7-9: PUBLIC LAUNCH + SCALE

### **MONTH 7: PUBLIC LAUNCH + Auto-Fix**
**Goal:** Launch publicly with complete product (FREE + PRO), add auto-fix features

> 🚀 **PUBLIC LAUNCH WEEK** - Product is now complete with 63 tools!

#### Week 1: PUBLIC LAUNCH (30h)

| Activity | Hours | Notes |
|----------|-------|-------|
| **Product Hunt launch** | 10 | Submit Monday 12:01 AM PST, engage all day |
| **Hacker News "Show HN"** | 4 | Post Tuesday 10 AM EST |
| **Reddit posts** | 4 | r/netsec, r/programming, r/cybersecurity, r/selfhosted |
| **Twitter/X thread** | 2 | 10-tweet demo thread with screenshots |
| **Launch video** | 4 | Loom 3-min: install → scan → results |
| **Monitor & respond** | 6 | Discord, GitHub issues, comments |

**Total:** 30 hours

**Launch Targets:**
- Product Hunt: Top 10
- GitHub Stars: 500+
- FREE signups: 200+
- Discord members: 100+

---

#### Week 2-3: Auto-Fix + PR Creation (42h)

| Feature | Hours | Notes |
|---------|-------|-------|
| **Apply auto-fix locally** | 8 | Write patch to file |
| **Git integration** | 12 | GitPython: create branch, commit |
| **GitHub PR creation** | 10 | GitHub REST API v3 |
| **GitLab MR creation** | 6 | GitLab API |
| **PR template** | 2 | Professional security fix description |
| **Fix verification** | 4 | Re-scan after fix applied |

**Total:** 42 hours
**Reference:** `Implementarion-spec.md` Section 8 (Git Integration)

---

#### Week 4: Community & Iteration (22h)

| Task | Hours | Notes |
|------|-------|-------|
| **Fix critical bugs from feedback** | 10 | Top issues from launch users |
| **Community engagement** | 6 | Discord support, GitHub issues |
| **Blog post** | 4 | "Week 1 Launch Retrospective" |
| **Conversion optimization** | 2 | Analyze FREE → PRO funnel |

**Total:** 22 hours

**Month 7 Success Criteria:**
- ✅ 200+ FREE users acquired
- ✅ First 5-10 PRO conversions
- ✅ Auto-fix working for top 5 vulnerability types
- ✅ < 24h response time on support

**Month 7 Total:** 94 hours (~24 hours/week)

---

### **MONTH 8: Enterprise Features**
**Goal:** SSO, RBAC, Compliance

#### Week 1-2: Authentication

| Feature | Hours | Notes |
|---------|-------|-------|
| **SSO/SAML integration** | 20 | Okta, Azure AD (python-saml) |
| **Google OAuth** | 8 | OAuth 2.0 flow |
| **Multi-user management** | 12 | Invite users, manage roles |
| **RBAC** | 16 | Roles: Admin, Security Lead, Developer, Viewer |

**Total:** 56 hours

---

#### Week 3-4: Compliance + Audit

| Feature | Hours | Notes |
|---------|-------|-------|
| **Compliance reports** | 20 | PCI-DSS, HIPAA, SOC2, ISO27001 mapping |
| **Audit logs** | 12 | Immutable, tamper-proof logs |
| **SIEM integration** | 8 | Export to Splunk, Datadog |
| **Air-gapped deployment docs** | 6 | No internet required |
| **Custom SLA config** | 4 | 99.5% uptime guarantee |

**Total:** 50 hours  
**Reference:** `Implementarion-spec.md` Section 10 (Enterprise)

**Month 8 Total:** 106 hours (~27 hours/week)

---

### **MONTH 9: Optimization + Scale**
**Goal:** Performance, reliability, monitoring

#### Week 1-2: Performance

| Task | Hours | Notes |
|------|-------|-------|
| **Database query optimization** | 12 | Add indexes, fix N+1 queries |
| **Parallel tool execution** | 16 | Run 10 tools simultaneously (Deep Scan) |
| **Caching (Redis)** | 12 | Cache scan results, tool outputs |
| **Docker image optimization** | 8 | Multi-stage builds, reduce to <2.5GB |

**Total:** 48 hours

---

#### Week 3-4: Reliability + Monitoring

| Task | Hours | Notes |
|------|-------|-------|
| **Health check endpoints** | 4 | `/health` for all services |
| **Error tracking (Sentry)** | 6 | Catch exceptions, alert |
| **Uptime monitoring** | 2 | UptimeRobot for 99.5% SLA |
| **Logging infrastructure** | 8 | Structured logs, retention |
| **Backup/restore** | 8 | PostgreSQL backups, restore scripts |
| **Load testing** | 12 | Simulate 100 concurrent scans (Locust) |

**Total:** 40 hours

**Month 9 Total:** 88 hours (~22 hours/week)

---

### **Month 7-9 Summary:**

| Month | Focus | Hours | Cumulative |
|-------|-------|-------|------------|
| 7 | Auto-Fix + CI/CD | 94 | 685 |
| 8 | Enterprise (SSO, RBAC, Compliance) | 106 | 791 |
| 9 | Performance + Reliability | 88 | 879 |

**Total:** 288 hours (~24 hours/week average)

**Deliverable: Enterprise-Ready Product ✅**

- ✅ Auto-fix + PR creation
- ✅ CI/CD integration (GitHub, GitLab, Jenkins)
- ✅ SSO/SAML (Okta, Azure AD)
- ✅ RBAC (custom roles)
- ✅ Compliance reports (all frameworks)
- ✅ Optimized performance (<15 min Deep Scan)

---

## 🗓️ MONTH 10-12: POLISH + GROWTH

### **MONTH 10: Polish + UX**
**Goal:** Professional UI, better onboarding

#### Week 1-2: UI/UX Improvements

| Task | Hours | Notes |
|------|-------|-------|
| **Hire contract designer** | 0 | $2,000 budget (Figma designs) |
| **Implement new design system** | 20 | shadcn/ui components |
| **Dashboard redesign** | 12 | Charts, metrics, security score trend |
| **Onboarding flow** | 10 | Tooltips, walkthrough for first-time users |
| **Mobile responsive** | 8 | Tablet + mobile layouts |

**Total:** 50 hours

---

#### Week 3-4: Developer Experience

| Task | Hours | Notes |
|------|-------|-------|
| **API documentation** | 8 | Auto-generated from OpenAPI (Swagger UI) |
| **Code examples** | 6 | Python, JavaScript, cURL samples |
| **Postman collection** | 4 | Pre-built requests |
| **Webhooks documentation** | 4 | Event payloads, retry logic |
| **SDK (Python client)** | 12 | `pip install eidossec` |

**Total:** 34 hours

**Month 10 Total:** 84 hours (~21 hours/week)

---

### **MONTH 11: Marketing + Content**
**Goal:** SEO, content marketing, community

#### Week 1-2: Content Creation

| Task | Hours | Notes |
|------|-------|-------|
| **Blog post 1** | 6 | "How to Find SQL Injection in Laravel" |
| **Blog post 2** | 6 | "Security Scanning for Startups" |
| **Video tutorial 1** | 4 | Installation (10 min, YouTube) |
| **Video tutorial 2** | 6 | First Scan (15 min, end-to-end demo) |
| **Video tutorial 3** | 8 | Advanced Features (20 min: AI, auto-fix, CI/CD) |

**Total:** 30 hours

---

#### Week 3-4: SEO + Community

| Task | Hours | Notes |
|------|-------|-------|
| **SEO optimization** | 8 | Keywords, meta tags ("free security scanner", "SAST tool") |
| **Backlink outreach** | 6 | Guest posts, mentions on security blogs |
| **Discord community growth** | 8 | Weekly office hours, AMAs |
| **GitHub Discussions setup** | 2 | Feature requests, Q&A |
| **Case study** | 8 | "How Company X found 50 bugs" |

**Total:** 32 hours

**Month 11 Total:** 62 hours (~16 hours/week)

---

### **MONTH 12: Scale + Iteration**
**Goal:** Handle growth, prepare Year 2

#### Week 1-2: Feature Requests (Top 3)

| Feature | Hours | Notes |
|---------|-------|-------|
| **Historical trend analysis** | 12 | Security score over time, charts |
| **Custom rules** | 16 | YAML-based rule engine for company policies |
| **Slack integration** | 8 | Webhook to Slack for notifications |

**Total:** 36 hours

---

#### Week 3-4: Year 2 Planning

| Task | Hours | Notes |
|------|-------|-------|
| **User feedback analysis** | 8 | What to build next? |
| **Roadmap for Year 2** | 6 | Prioritize features |
| **Financial review** | 4 | ARR, costs, profit - are we on track? |
| **Hiring plan** | 4 | Do we need help? |
| **Infrastructure scaling prep** | 8 | Can we handle 10x users? |

**Total:** 30 hours

**Month 12 Total:** 66 hours (~17 hours/week)

---

### **Month 10-12 Summary:**

| Month | Focus | Hours | Cumulative |
|-------|-------|-------|------------|
| 10 | Polish + UX | 84 | 963 |
| 11 | Marketing + Content | 62 | 1,025 |
| 12 | Scale + Iteration | 66 | 1,091 |

**Total:** 212 hours (~18 hours/week average)

**Deliverable: Year 1 Complete ✅**

- ✅ Professional UI/UX
- ✅ API documentation + SDK
- ✅ SEO-optimized content
- ✅ Active community (Discord, GitHub)
- ✅ Case studies + testimonials
- ✅ Ready to scale (Year 2)

---

## 📊 YEAR 1 DEVELOPMENT SUMMARY

| Phase | Months | Focus | Hours | Hours/Week |
|-------|--------|-------|-------|------------|
| **Phase 1** | 1-3 | FREE Tier (MVP) | 263 | 22 |
| **Phase 2** | 4-6 | PRO Tier + Monetization | 328 | 27 |
| **Phase 3** | 7-9 | Enterprise Features | 288 | 24 |
| **Phase 4** | 10-12 | Polish + Growth | 212 | 18 |
| **TOTAL** | 1-12 | Full Product | **1,091** | **22 avg** |

**Year 1 = 1,091 hours (~22 hours/week average)**

**Breakdown:**
- Solo coding: ~60% (655 hours)
- AI-assisted coding: ~30% (327 hours)
- Planning/design: ~10% (109 hours)

---

## 🎯 FEATURE GATING MATRIX (FREE vs PRO)

**Complete Feature List:**

| Feature | FREE | PRO | Implementation |
|---------|------|-----|----------------|
| **CORE SCANNING** ||||
| Projects | 3 max | Unlimited | License check in POST /projects |
| Users | 1 | Unlimited | License tier in DB |
| Tools | 15 essential | 50+ tools | Tool selection based on license |
| Scan Mode | Quick only | Quick + Deep + Custom | Mode check in orchestrator |
| Concurrent Scans | 1 sequential | 10 parallel | Queue priority based on license |
| Scan History | 10 scans | Unlimited | DB query limit by license |
| Data Retention | 30 days | Unlimited | Auto-delete old scans for FREE |
| **FINDINGS** ||||
| View Findings | ✅ | ✅ | Always allowed |
| Update Status | View only | ✅ Can edit | Permission check |
| Assign to User | ❌ | ✅ | PRO feature |
| Add Comments | ❌ | ✅ | PRO feature |
| Bulk Actions | ❌ | ✅ | PRO feature |
| **AI FEATURES** ||||
| AI Explanations | ❌ | ✅ | Check license before LLM call |
| AI Fix Suggestions | ❌ | ✅ | Check license before LLM call |
| Attack Scenarios | ❌ | ✅ | PRO feature |
| Business Impact | ❌ | ✅ | PRO feature |
| **AUTO-FIX** ||||
| Generate Patches | ❌ | ✅ | PRO feature |
| Apply Locally | ❌ | ✅ | PRO feature |
| Create GitHub PR | ❌ | ✅ | PRO feature |
| Create GitLab MR | ❌ | ✅ | PRO feature |
| **REPORTING** ||||
| Export JSON | ✅ | ✅ | Always allowed |
| Export PDF | ❌ | ✅ | PRO feature |
| Export HTML | ❌ | ✅ | PRO feature |
| Export SARIF | ❌ | ✅ | PRO feature |
| Compliance Reports | ❌ | ✅ | PRO feature |
| Scheduled Reports | ❌ | ✅ | PRO feature |
| **CI/CD** ||||
| Manual Setup Docs | ✅ | ✅ | Public docs |
| Pre-built Templates | ❌ | ✅ | PRO feature |
| Quality Gates | ❌ | ✅ | PRO feature |
| PR Comments | ❌ | ✅ | PRO feature |
| **INTEGRATIONS** ||||
| Slack | ❌ | ✅ | PRO feature |
| JIRA | ❌ | ✅ | PRO feature |
| Webhooks | ❌ | ✅ | PRO feature |
| API Access | ❌ | ✅ | PRO feature (rate limited) |
| **COLLABORATION** ||||
| Multi-User | ❌ 1 user | ✅ Unlimited | License-based |
| Roles & Permissions | ❌ | ✅ | PRO feature |
| Activity Logs | ❌ | ✅ | PRO feature |
| @mentions | ❌ | ✅ | PRO feature |
| **AUTHENTICATION** ||||
| Email/Password | ✅ | ✅ | Always allowed |
| SSO (OAuth) | ❌ | ✅ | PRO feature |
| SAML/LDAP | ❌ | ✅ | PRO feature |
| MFA/2FA | ❌ | ✅ | PRO feature |
| **ENTERPRISE** ||||
| Compliance (All) | ❌ | ✅ | PRO feature |
| Audit Logs | ❌ | ✅ | PRO feature |
| Air-Gapped Deploy | ❌ | ✅ | PRO feature |
| Custom SLA | ❌ | ✅ | PRO feature |
| Priority Support | ❌ | ✅ Email 24h | PRO feature |

---

**END OF PART 1: ROADMAP**

*(Part 2 with detailed milestones, deliverables, and acceptance criteria follows in sections below...)*

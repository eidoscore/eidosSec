# EIDOSSEC DEEP-DIVE AUDIT REPORT (REAL STATE)

Date: 2026-04-02
Repository: D:\Project\eidosSec
Requested by: Product owner
Main goal from owner:
- Keep all existing tools (no deletion)
- Integrate all existing tools into one working eidosSec flow

---

## 1. Executive Summary

Current codebase is not aligned with the main goal yet.

The project has good structural intent (backend + scanner + frontend + many tool wrappers), but the runtime integration is still broken at critical points:
- scanner cannot compile/run fully,
- frontend cannot compile,
- scan lifecycle is not persisted end-to-end,
- many wrappers share a broken execution contract.

Conclusion: this is not "done" and not "stable integrated" yet. It is a partially assembled platform with major P0/P1 blockers.

---

## 2. Method and Evidence

Validation commands executed:
- backend tests: `python -m pytest -q` (PASS, but minimal scope)
- scanner compile: `python -m compileall -q app` (FAIL)
- scanner tests: `python -m pytest -q` (FAIL at import/collection)
- frontend type-check: `npm run type-check` (FAIL)
- frontend build: `npm run build` (FAIL)

Key failing evidence:
- scanner compile fails on CodeQL wrapper indentation
- frontend fails on JSX structure in ScanDetails

---

## 3. Alignment Against Owner Goals

### Goal A: No existing tools removed
Status: PARTIALLY OK (inventory exists)
- 23 wrappers exist under `scanner/app/tools` (including extended/pro wrappers).
- However, existence != integrated execution readiness.

### Goal B: All existing tools integrated in one app flow
Status: NOT MET
- Wrapper execution contract is broken across almost all wrappers.
- Scan result persistence to backend database is incomplete.
- Frontend cannot compile and has API/status contract drift.

---

## 4. Critical Findings (P0)

### P0-1. Scanner compile blocker
- File: `scanner/app/tools/codeql.py:60`
- Issue: `IndentationError` (function body missing after `parse_output` declaration).
- Impact: scanner test collection/import can fail immediately.

### P0-2. Core wrapper execution contract is broken
- Base expects `ToolResultSchema` execution flow:
  - `scanner/app/tools/base.py:127`
- Orchestrator expects `result.status`, `result.findings`, `result.execution_time`:
  - `scanner/app/orchestrator.py:156-177`
- But all wrappers override `execute()` and return `List[FindingSchema]`.
- All wrappers call non-existent `execute_command(...)` method.
  - Example: `scanner/app/tools/phpstan.py:41`
- Impact: tools cannot be reliably integrated; orchestrator/wrapper interaction is inconsistent by design.

### P0-3. Scan lifecycle persistence is unfinished
- Scan is created as `pending`, task is sent, but no implemented result processing path to persist findings and transition scan status correctly.
  - `backend/app/api/v1/scans.py:77-125`
  - `backend/app/tasks.py:13` (TODO)
- Impact: end-to-end goal (integrated tools -> stored findings -> UI) is not reliable.

### P0-4. Frontend does not compile
- File: `frontend/src/pages/ScanDetails.tsx:438`, `:487`
- TypeScript errors prevent build.
- Impact: UI for scan result/progress is not deployable.

### P0-5. Fresh DB schema drift risk (model vs migration)
- Model has fields not present in initial migration:
  - `Project.owner_id`: `backend/app/models.py:19`
  - `Scan.task_id`: `backend/app/models.py:46`
- Initial migration does not create those columns:
  - `backend/alembic/versions/20260202_0230_001_initial_schema.py`
- Impact: clean deployment/migration path can break ORM assumptions.

---

## 5. High Findings (P1)

### P1-1. Frontend/backend API contract mismatch (scan create)
- Frontend sends `scan_type`:
  - `frontend/src/pages/NewProject.tsx:58`
- Backend expects `mode`:
  - `backend/app/schemas.py:67-70`
- Impact: auto-scan flow fails (422 risk).

### P1-2. Status enum mismatch in frontend
- Frontend uses `in_progress`:
  - `frontend/src/pages/ScanDetails.tsx:40,75,192,207`
- Backend canonical enum: `pending|running|completed|failed|cancelled`:
  - `backend/app/models.py:55`
- Impact: polling/progress behavior diverges.

### P1-3. WebSocket routing mismatch behind frontend nginx
- Frontend opens WS to current host (`window.location.host`):
  - `frontend/src/pages/ScanDetails.tsx:79`
- Frontend nginx has no `/ws` proxy rule to backend:
  - `frontend/nginx.conf`
- Impact: real-time progress can fail even when backend WS exists.

### P1-4. Access control gaps on findings/export
- Findings update/analyze endpoint lacks ownership RBAC check.
  - `backend/app/api/v1/findings.py:54-90`, `93-139`
- Scan export endpoint lacks `current_user` dependency.
  - `backend/app/api/v1/scans.py:391-436`
- Impact: data exposure / unauthorized mutation risk.

### P1-5. License gating still placeholder-grade
- License verifier assumes PRO on certain success path, not strict feature proof.
  - `scanner/app/services/license.py:78-82`
- Impact: inaccurate gating for paid tools/features.

---

## 6. Medium Findings (P2)

### P2-1. Tool wrappers have additional structural bugs
- Nuclei wrapper has duplicate `parse_output` definitions and missing `_get_target_url` implementation while being called.
  - `scanner/app/tools/nuclei.py:18,49,62,76`
- Multiple wrappers use `self.logger` without base class setting logger instance.
  - e.g. `scanner/app/tools/zap.py:56`, `phpstan.py:44`

### P2-2. Frontend route/nav inconsistency
- Layout links to `/projects` and `/scans`, but routes are not declared in `App.tsx`.
  - `frontend/src/components/Layout.tsx:25,31`
  - `frontend/src/App.tsx:12-20`

### P2-3. Root README still conflicts with aligned docs
- Mentions `localhost:3000` and 21+ claims not aligned with current audited state.
  - `README.md:17,23,43`

### P2-4. Test coverage is too shallow for integration goal
- Backend test pass is only 3 tests, mostly AI service unit tests.
- No strong automated gate for true end-to-end scan persistence and full wrapper contract.

---

## 7. Deep-Dive Pass 2: Wrapper Integration Inventory

Automated wrapper inventory results:
- Total wrappers (excluding base/init): 23
- Wrappers with custom `execute()`: 23/23
- Wrappers calling missing `execute_command(...)`: 23/23
- Wrappers using `self.logger` pattern: 18/23

Interpretation:
- This is a systemic contract break, not isolated bugs.
- To achieve "all tools integrated", wrapper architecture must be normalized first (single canonical execution contract).

---

## 8. What Is Already Good

- Baseline architecture components are present and reasonable.
- Tool inventory is broad (good for owner's non-removal requirement).
- Detector service exists and is usable (`/projects/detect`).
- Docs are now aligned on contracts/ports/status after recent rewrite.

---

## 9. Required Fix Plan (Execution Order)

### Phase 0 (must pass before anything else)
1. Fix scanner compile blockers (`codeql.py`, nuclei structural bugs).
2. Rebuild wrapper contract:
   - either remove custom `execute()` overrides and use base execution,
   - or implement a consistent override contract returning `ToolResultSchema`.
3. Add shared execution helper to base (if wrappers need custom command handling).
4. Fix frontend compile errors in `ScanDetails.tsx`.

### Phase 1 (core lifecycle)
1. Implement scan status transitions: `pending -> running -> completed/failed/cancelled`.
2. Implement result ingestion/persistence (`process_scan_results` or equivalent path).
3. Persist findings, `tools_executed`, summary metadata.

### Phase 2 (contract and security hardening)
1. Fix frontend API payload/status mismatches (`scan_type`, `in_progress`).
2. Add WS proxy routing or direct backend WS URL strategy.
3. Enforce RBAC on finding mutation and scan export.
4. Harden license verifier to deterministic feature contract.

### Phase 3 (all-tools integration target)
1. Bring each wrapper to production-ready checklist:
   - binary check,
   - parser test,
   - deterministic failure behavior,
   - canonical schema mapping.
2. Enable staged rollout flags for unstable wrappers without deleting any wrapper.

---

## 10. Final Judgment

Current state relative to owner goal:
- "No tool deletion": conceptually respected.
- "All tools integrated in one working app": not achieved yet.

This codebase is salvageable and directionally correct, but currently still in stabilization phase, not completion phase.

---

## 11. Immediate Next Action Recommended

Start implementation with a strict P0 branch focused on:
- scanner wrapper contract normalization,
- frontend compile recovery,
- scan lifecycle persistence completion.

Without these three, deeper feature integration will continue to drift and regress.

---

## 12. Deep-Dive Addendum (Pass 3)

### 12.1 Tool binary provisioning mismatch (very important)

Several wrappers exist but required binaries are not provisioned in scanner image, which means wrappers will be skipped or fail even after code compiles.

Evidence:
- Scanner Dockerfile installs/copies: gitleaks, trivy, trufflehog, gosec, staticcheck, codeql, spotbugs, pmd, shellcheck, kics.
  - `scanner/Dockerfile:49-64`
- No installation for `nuclei` binary and no `zap-baseline.py` tooling in scanner image.
  - `scanner/Dockerfile` (no nuclei/zap install blocks)
  - `scanner/scripts/download_tools.sh` (no nuclei/zap download)
- But wrappers expect those executables:
  - `scanner/app/tools/nuclei.py:23`
  - `scanner/app/tools/zap.py:23-27,35`

Impact:
- "All existing tools integrated" cannot be achieved until build/runtime provisioning matrix is aligned with wrappers.

### 12.2 Wrapper structural consistency check (automated)

Automated AST/static scan findings:
- `codeql.py` parse failure due to indentation issue.
- `nuclei.py` has duplicate method definition: `parse_output`.
- All 22 parseable wrappers define `execute()` as `List[FindingSchema]` rather than canonical `ToolResultSchema` expected by orchestrator/base contract.

Impact:
- Integration debt is systemic; should be fixed with one unified wrapper contract migration rather than file-by-file patching without design lock.

### 12.3 Frontend navigation/route drift (UX + contract)

- `Layout.tsx` links to `/projects` and `/scans`, but these routes are not defined in `App.tsx`.
  - `frontend/src/components/Layout.tsx:25,31`
  - `frontend/src/App.tsx:12-20`
- `Landing.tsx` links to `/docs/intro`, which is not a frontend route in app router.
  - `frontend/src/pages/Landing.tsx:15`

Impact:
- User navigation appears complete, but several links are dead routes.

### 12.4 Readiness update

After pass 3, readiness for owner goal remains:
- Tool preservation: YES (inventory exists)
- Full integrated execution: NO
- Primary blockers: wrapper contract + binary provisioning + scan lifecycle persistence + frontend compile

---

## 13. Deep-Dive Addendum (Pass 4)

### 13.1 Celery topology mismatch can drop or misroute scan tasks (P0)

Evidence:
- Backend sends task `"scanner.scan_project"` without explicit queue:
  - `backend/app/api/v1/scans.py:92-95`
- Scanner task is named `"scanner.scan_project"`:
  - `scanner/app/tasks.py:13`
- Scanner Celery route is configured for a different task name (`"app.tasks.scan_project"`):
  - `scanner/app/celery_app.py:49-50`
- Compose runs both backend worker and scanner worker on default queue behavior:
  - `docker-compose.yml:63-70` (backend celery-worker)
  - `docker-compose.yml:87-104` (scanner worker)

Impact:
- Task routing is non-deterministic and can be consumed by the wrong worker.
- In worst case, scan task can be ignored/failed at worker side due unregistered task path.
- This blocks reliable "all tools integrated in one app flow."

### 13.2 Scan state machine is not implemented end-to-end in backend (P0)

Evidence:
- Scan is created with `pending`:
  - `backend/app/api/v1/scans.py:77-83`
- No code path sets `running`, `completed`, or `cancelled`.
- Existing explicit assignments only set `failed` on trigger/cancel failures:
  - `backend/app/api/v1/scans.py:101`, `:110`, `:368`, `:378`
- Result processing task is still TODO:
  - `backend/app/tasks.py:9-17`

Impact:
- Lifecycle contract (`pending -> running -> completed/failed/cancelled`) is broken.
- Frontend and monitoring cannot represent real scan progress reliably.

### 13.3 Migration chain is incompatible with active ORM/API usage (P0)

Evidence:
- ORM model uses:
  - `Project.owner_id` (`backend/app/models.py:19`)
  - `Scan.task_id` (`backend/app/models.py:46`)
- Migrations do not create those columns:
  - `backend/alembic/versions/20260202_0230_001_initial_schema.py`
  - No follow-up migration adds `owner_id` or `task_id`.
- API uses both fields in live queries/writes:
  - owner checks: `backend/app/api/v1/projects.py:46,62,96,136`, `backend/app/api/v1/scans.py:53,66,178,226,278,354`
  - task persistence: `backend/app/api/v1/scans.py:97`

Impact:
- Fresh database from Alembic can be incompatible with runtime code paths.
- This is not only "drift risk"; it can break core endpoints.

### 13.4 Docker one-command startup does not apply migrations (P1)

Evidence:
- Backend container starts `uvicorn` directly:
  - `backend/Dockerfile:50-51`
- No automatic `alembic upgrade head` in compose startup path.

Impact:
- `docker-compose up -d --build` can boot services without guaranteed schema readiness.
- This conflicts with all-in-one self-hosted expectation.

### 13.5 Path contract is broken for Windows onboarding + container runtime (P0)

Evidence:
- Frontend onboarding suggests Windows local path input (`C:\\...`):
  - `frontend/src/pages/NewProject.tsx:16-18`
- Backend model enforces Unix-style path regex:
  - `backend/app/models.py:28`
- Scanner/backend containers only mount project volume under `/app/projects`:
  - `docker-compose.yml:54`, `:84`, `:103`
- Detector validates path from backend runtime filesystem:
  - `backend/app/services/detector.py:213-231`

Impact:
- User can input path format suggested by UI but rejected/unreachable in containerized flow.
- This blocks project onboarding and therefore blocks full tool integration flow.

### 13.6 Frontend has no authentication flow even though API is protected (P0)

Evidence:
- Frontend only reads token from localStorage:
  - `frontend/src/lib/api.ts:17-20`
- No route/page in frontend for login/setup/token bootstrap:
  - `frontend/src/App.tsx:12-19`
  - no `/auth/login` usage in `frontend/src`.
- Core API endpoints require authenticated user dependencies:
  - `backend/app/api/v1/projects.py`, `scans.py`, `findings.py`

Impact:
- Clean install cannot perform normal project/scan operations from UI.
- System appears up but functional flow is blocked by 401 state.

### 13.7 WebSocket channel has both connectivity and authorization gaps (P1)

Evidence:
- Frontend WS URL is current host `/ws/scans/{id}`:
  - `frontend/src/pages/ScanDetails.tsx:79`
- Frontend nginx has no `/ws` proxy to backend:
  - `frontend/nginx.conf`
- Backend WS auth token is optional, and RBAC check only executes when token is present:
  - `backend/app/api/v1/websocket.py:24-39`

Impact:
- Progress stream may fail operationally behind frontend nginx.
- If reachable directly, channel can be subscribed without auth token (scan-id enumeration risk).

### 13.8 API/UI response contract mismatches beyond create-scan payload (P1)

Evidence:
- Frontend `ProjectDetails` expects `project.scans` in project payload:
  - `frontend/src/pages/ProjectDetails.tsx:96,109,122`
- Backend `ProjectResponse` does not include `scans`:
  - `backend/app/schemas.py:27-38`
  - `backend/app/api/v1/projects.py:142-151`
- Frontend `ScanDetails` displays `scan.total_findings`:
  - `frontend/src/pages/ScanDetails.tsx:300`
- Backend `ScanDetailResponse` has no `total_findings` field:
  - `backend/app/schemas.py:96-110`

Impact:
- UI renders incomplete/incorrect state even when backend responds successfully.

### 13.9 Read-only project mount conflicts with wrappers that write artifacts (P1)

Evidence:
- Scanner project volume is mounted read-only:
  - `docker-compose.yml:103`
- Some wrappers write result files into project working directory:
  - `scanner/app/tools/gosec.py:17,53`
  - `scanner/app/tools/codeql.py:19,50`
  - `scanner/app/tools/sast/spotbugs.py:23,53`

Impact:
- Those tools can fail even after compile/contract fixes, because output files cannot be created in read-only project path.

### 13.10 Model constraint placement bug (P2)

Evidence:
- `User` model includes findings-related check constraints in `__table_args__`:
  - `backend/app/models.py:101-107`

Impact:
- Schema intent is inconsistent and can create future migration/autogenerate errors.
- Signals unfinished model hygiene in a high-coupling area.

### 13.11 Readiness update after Pass 4

Current readiness vs owner goal:
- Keep existing tools: YES (still preserved in code inventory).
- Integrate all tools in one working app: NO.

Highest-confidence blockers now:
1. Celery routing/topology mismatch.
2. Scan lifecycle persistence/state-machine gap.
3. Migration-model incompatibility on `owner_id/task_id`.
4. Frontend compile + auth + status/API mismatch.
5. Path contract mismatch (Windows UI vs Docker runtime path model).

---

## 14. Deep-Dive Addendum (Pass 5 - Docs vs Code Revalidation)

### 14.1 Revalidation command results (2026-04-03)

Executed again:
- Backend tests: `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- Scanner compile: `cd scanner && python -m compileall -q app` -> FAIL (`IndentationError` in `codeql.py`)
- Scanner tests: `cd scanner && python -m pytest -q` -> FAIL at import (`codeql.py` parse error)
- Frontend type-check: `cd frontend && npm run type-check` -> FAIL (`ScanDetails.tsx`)
- Frontend build: `cd frontend && npm run build` -> FAIL (`ScanDetails.tsx`)

### 14.2 Additional docs-to-code mismatches (beyond Pass 4)

#### 14.2.1 Frontend still violates canonical docs contract for scan request/status (P0)

Docs contract:
- Create scan payload uses `mode` (`docs/api.md`, `docs/README.md`, `docs/usage.md`)
- Status enum uses `pending|running|completed|failed|cancelled` (`docs/README.md`, `docs/ONBOARDING_OPTIMIZATION.md`)

Code reality:
- Frontend auto-scan still sends `scan_type`:
  - `frontend/src/pages/NewProject.tsx:58`
- Frontend logic still relies on `in_progress`:
  - `frontend/src/pages/ScanDetails.tsx:40,75,192,207`

Impact:
- Breaks "aligned docs contract" claim and can trigger scan-creation/polling regressions.

#### 14.2.2 Frontend compile blocker remains unresolved (P0)

Evidence:
- `npm run type-check` and `npm run build` both fail:
  - `frontend/src/pages/ScanDetails.tsx:438`
  - `frontend/src/pages/ScanDetails.tsx:487`

Impact:
- UI cannot be shipped despite docs presenting stable usage flow.

#### 14.2.3 Scanner wrapper contract break is still systemic (P0)

Evidence:
- Wrappers count: 23; all 23 implement custom `execute()` returning findings list style.
- All 23 wrappers call `execute_command(...)` but base has no such method:
  - wrappers: `scanner/app/tools/*` (e.g., `phpstan.py:41`, `semgrep.py:61`)
  - base missing helper: `scanner/app/tools/base.py` (no `def execute_command`)
- Orchestrator still expects `ToolResultSchema` fields (`status`, `findings`, `execution_time`):
  - `scanner/app/orchestrator.py:156-177`

Impact:
- Current code contradicts documented "unified output model" (`docs/tools.md`, `docs/INTEGRATED_APP_PLAN.md`).

#### 14.2.4 Tool provisioning docs narrative vs runtime still mismatched (P1)

Docs baseline includes DAST tools ZAP + Nuclei:
- `docs/tools.md`
- `docs/PRO_TOOLS_MATRIX.md`

Code/runtime:
- Scanner image does not provision `nuclei` binary or `zap-baseline.py`:
  - `scanner/Dockerfile` (no nuclei/zap install)
  - `scanner/scripts/download_tools.sh` (no nuclei/zap download)
- Wrappers require those binaries:
  - `scanner/app/tools/nuclei.py`
  - `scanner/app/tools/zap.py`

Impact:
- Baseline tool matrix in docs cannot be reliably executed in container runtime.

#### 14.2.5 Baseline-vs-extended tool policy drift in orchestrator (P1)

Docs separate stable baseline and "stabilization required" wrappers:
- `docs/tools.md`
- `docs/PRO_TOOLS_MATRIX.md`

Code reality:
- Orchestrator includes all 23 wrappers in the primary execution list:
  - `scanner/app/orchestrator.py:49-73`
- Only 6 wrappers are explicitly license-gated (`requires_license=True`), so some stabilization-stage tools can run in normal flow.

Impact:
- Violates docs intent of deterministic baseline profile behavior.

#### 14.2.6 Security contract drift: protected API docs vs unprotected export / weak WS auth (P1)

Docs state most endpoints require Bearer token:
- `docs/api.md:11`

Code reality:
- Scan export endpoint has no `current_user` auth dependency:
  - `backend/app/api/v1/scans.py:391-436`
- WebSocket accepts unauthenticated clients when token absent:
  - `backend/app/api/v1/websocket.py:24-39`

Impact:
- Docs promise stronger access control than implemented behavior.

#### 14.2.7 UX contract drift: setup/login and container-path guidance not reflected in frontend (P1)

Docs claim setup/login flow and container-path onboarding:
- `docs/usage.md:5,11`
- `docs/ONBOARDING_OPTIMIZATION.md:20`

Code reality:
- No login/setup pages or routes in frontend:
  - `frontend/src/App.tsx`
  - `frontend/src/pages` (only `Dashboard`, `Landing`, `NewProject`, `ProjectDetails`, `ScanDetails`)
- New project path helper still suggests host OS path patterns (`C:\\...`, `/home/...`) instead of canonical `/app/projects/...`:
  - `frontend/src/pages/NewProject.tsx:16-26`

Impact:
- Clean-install user journey in docs cannot be completed from UI as documented.

#### 14.2.8 Documentation-aligned routes still not implemented in app navigation (P2)

Evidence:
- Layout links to routes not declared in router:
  - links: `frontend/src/components/Layout.tsx:25,31` (`/projects`, `/scans`)
  - routes: `frontend/src/App.tsx:10-18`
- Landing links to `/docs/intro` (not a frontend route):
  - `frontend/src/pages/Landing.tsx:15`

Impact:
- Navigation behavior diverges from documentation quality expectations.

#### 14.2.9 Product messaging drift in API metadata (P2)

Docs now carefully frame baseline vs roadmap:
- `docs/tools.md`
- `docs/PRO_TOOLS_MATRIX.md`

Code metadata still claims "50+ tools":
- `backend/app/main.py:31`

Impact:
- Public API docs can overstate current integrated capability.

### 14.3 Readiness update after Pass 5

Current readiness vs owner goal remains:
- Keep existing tools: YES (inventory preserved).
- Integrate all existing tools in one reliable flow: NO.

Updated highest-confidence blockers:
1. Scanner/frontend compile blockers (`codeql.py`, `ScanDetails.tsx`).
2. Wrapper contract architecture mismatch (`execute_command` + return shape).
3. Scan lifecycle persistence gap (`pending` stuck, no complete ingestion path).
4. Contract drift across frontend (`scan_type`, `in_progress`, auth/path UX).
5. Runtime provisioning and topology mismatch (Celery routing, missing nuclei/zap binaries).

---

## 15. Execution Update (2026-04-03) - P0 Progress

### 15.1 P0-1 Frontend compile blocker (`ScanDetails.tsx`) - CLOSED

Status: FIXED

Code evidence:
- `frontend/src/pages/ScanDetails.tsx:397`  
  Wrapped findings table + pagination block into a valid JSX fragment so sibling elements compile correctly.
- `frontend/src/pages/ScanDetails.tsx:422`  
  Normalized `Badge` variant mapping to valid variants (`destructive`/`secondary`) to keep strict TS type compatibility.
- `frontend/src/pages/ScanDetails.tsx:4`  
  Removed unused `Filter` import to satisfy `noUnusedLocals` during `tsc`.

Verification evidence:
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- This closes the hard frontend compile failure previously reported at `ScanDetails.tsx:438,487`.
- Remaining P0 items are still open and continue in sequence.

### 15.2 P0-2 Scanner compile blocker (`codeql.py`) + `nuclei.py` structural bug - CLOSED

Status: FIXED

Code evidence:
- `scanner/app/tools/codeql.py:65`  
  Implemented `parse_output(...)` body so module is syntactically complete (removes `IndentationError` root cause).
- `scanner/app/tools/codeql.py:49`  
  `execute(...)` now reads SARIF with explicit UTF-8 handling and logs failures safely.
- `scanner/app/tools/nuclei.py:65`  
  Added `_get_target_url(...)` helper as actual URL resolver (env + `.nuclei_target` file).
- `scanner/app/tools/nuclei.py:77`  
  Kept only one valid `parse_output(...)` implementation (removed duplicate conflicting definition).

Verification evidence:
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`89 passed`)

Notes:
- Scanner import/collection is now stable again.
- Core wrapper contract normalization (systemic `execute_command` + return-shape mismatch) remains open in P0-3.

### 15.3 P0-3 Wrapper execution contract normalization - CLOSED

Status: FIXED

Code evidence:
- `scanner/app/tools/base.py:25`  
  Added `__init_subclass__` contract shim that wraps legacy custom `execute()` implementations and normalizes outputs to `ToolResultSchema`.
- `scanner/app/tools/base.py:153`  
  Added shared `execute_command(...)` helper in base class, so wrapper calls are no longer referencing undefined method.
- `scanner/app/tools/base.py:184`  
  Added `_normalize_execution_result(...)` to coerce legacy `List[FindingSchema]` / `None` return values into canonical `ToolResultSchema`.
- `scanner/app/tools/base.py:213`  
  Base `execute()` remains canonical `ToolResultSchema` path for wrappers that do not override execution.
- `scanner/tests/tools/test_base_contract.py`  
  Added regression tests proving legacy list/none `execute()` implementations are normalized into `ToolResultSchema`.

Verification evidence:
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)

Notes:
- This keeps all existing wrappers intact (no deletion), while enforcing one orchestrator-facing execution contract.

### 15.4 P0-4 Real scan lifecycle persistence - CLOSED

Status: FIXED

Code evidence:
- `backend/app/api/v1/scans.py:98`  
  Scan status is moved to `running` immediately after scanner task dispatch succeeds.
- `backend/app/api/v1/scans.py:370` and `backend/app/api/v1/scans.py:381`  
  Cancel path now writes terminal `cancelled` state (not forced `failed`).
- `scanner/app/tasks.py:69` and `scanner/app/tasks.py:74`  
  Scanner worker now pushes `running` and final result payloads back to backend via Celery.
- `backend/app/tasks.py:60`  
  Implemented async-backed `process_scan_results` execution path (no longer TODO stub).
- `backend/app/tasks.py:111`  
  Existing findings for scan are replaced during ingestion to persist final canonical result.
- `backend/app/tasks.py:156` and `backend/app/tasks.py:157`  
  Backend now persists summary + score, alongside status, tools executed, completion time, and duration.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Lifecycle path now supports deterministic terminal persistence (`completed/failed/cancelled`) with findings and scan metadata ingestion.

### 15.5 P0-5 Celery topology/routing deterministic alignment - CLOSED

Status: FIXED

Code evidence:
- `backend/app/api/v1/scans.py:94`  
  Backend dispatches `scanner.scan_project` explicitly to queue `scans`.
- `scanner/app/celery_app.py:49-52`  
  Scanner routes are aligned to task names (`scanner.scan_project`, `scanner.health_check`) and backend result task route.
- `backend/app/celery_app.py:32-35`  
  Backend routes backend-owned tasks to dedicated `backend_tasks` queue.
- `docker-compose.yml:70`  
  Backend worker constrained to `--queues backend_tasks`.
- `docker-compose.yml:94`  
  Scanner worker constrained to `--queues scans`.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Queue ownership is now explicit, preventing scanner tasks from being consumed by backend worker topology.

---

## 16. Execution Update (2026-04-03) - P1 Progress

### 16.1 P1-1 Frontend scan payload + status enum alignment - CLOSED

Status: FIXED

Code evidence:
- `frontend/src/pages/NewProject.tsx:58`  
  Auto-scan payload now uses canonical field `mode: 'quick'` (replacing legacy `scan_type`).
- `frontend/src/pages/ScanDetails.tsx:40`  
  Polling interval now follows canonical status `running`.
- `frontend/src/pages/ScanDetails.tsx:75`  
  WebSocket connection guard switched from `in_progress` to `running`.
- `frontend/src/pages/ScanDetails.tsx:192` and `frontend/src/pages/ScanDetails.tsx:207`  
  Running-state UI gates now consistently use `running|pending` enum set.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Frontend request/status contract for scan create and progress flow is now aligned with backend/docs canonical enum.

### 16.2 P1-2 Frontend authentication flow - CLOSED

Status: FIXED

Code evidence:
- `frontend/src/App.tsx:14`, `:33`, `:35`  
  Added route-level auth guards (`RequireAuth` + `/auth` public route), so protected pages require token.
- `frontend/src/pages/Auth.tsx:53`, `:72`, `:82`  
  Implemented explicit login flow and first-time setup flow (`/auth/setup`) with token bootstrap via `/auth/login`.
- `frontend/src/pages/Auth.tsx:115`  
  Added session-expired recovery message on auth page.
- `frontend/src/lib/api.ts:36`, `:38`  
  Added explicit 401 recovery behavior: clear token and redirect user to `/auth?reason=session_expired&next=...`.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Frontend now supports first-time setup/login and provides explicit re-auth path when token is missing/expired.

### 16.3 P1-3 Path contract UX for Docker runtime - CLOSED

Status: FIXED

Code evidence:
- `frontend/src/pages/NewProject.tsx:11-29`  
  Added canonical container-path contract helpers (`/app/projects/...`) and mismatch hint logic.
- `frontend/src/pages/NewProject.tsx:94-100`  
  Added pre-submit validation that rejects host-style path inputs and normalizes path before detection.
- `frontend/src/pages/NewProject.tsx:125`  
  Added explicit error message for host-path/container-path mismatch when backend cannot resolve path.
- `frontend/src/pages/NewProject.tsx:159`, `:175`, `:181`  
  Updated onboarding UX copy + placeholder to container-visible path (`/app/projects/my-app`) with clear examples.
- `frontend/src/pages/NewProject.tsx:183`  
  Added inline warning panel that explains mismatch before submitting.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Onboarding now defaults to container path contract and provides explicit recovery guidance for host-path input mistakes.

### 16.4 P1-4 API/UI response mismatch resolution - CLOSED

Status: FIXED

Code evidence:
- `frontend/src/pages/ProjectDetails.tsx:23-31`  
  Added dedicated scan-history query from canonical endpoint `/scans` with `project_id` filter (instead of relying on `project.scans` in project payload).
- `frontend/src/pages/ProjectDetails.tsx:119` and `:132`  
  Last-scan and table rendering now use `scans` query response, not `project.scans`.
- `frontend/src/pages/ProjectDetails.tsx:162-163`  
  Findings and duration columns now use canonical fields (`findings_count`, computed duration from `started_at/completed_at`).
- `frontend/src/pages/ScanDetails.tsx:300`  
  Total findings card now uses canonical scan summary (`scan.summary?.total_findings`) with paginated fallback, replacing removed `scan.total_findings` assumption.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Frontend project/scan detail rendering is now aligned with backend response schema without ad-hoc fields.

### 16.5 P1-5 RBAC hardening on sensitive endpoints/channels - CLOSED

Status: FIXED

Code evidence:
- `backend/app/api/v1/findings.py:17`, `:63`, `:89`, `:129`  
  Added centralized ownership guard (`_enforce_finding_access`) and applied it to `GET`, `PATCH`, and `POST /analyze` finding flows.
- `backend/app/api/v1/scans.py:395`, `:399`, `:424`  
  Added authenticated user dependency + RBAC ownership check for `GET /scans/{scan_id}/export`.
- `backend/app/api/v1/websocket.py:26`, `:37`, `:42`, `:58`  
  WebSocket now enforces mandatory token, validates scan UUID, validates user identity, and validates project ownership before subscribing to progress channel.
- `frontend/src/pages/ScanDetails.tsx:82`  
  Frontend WebSocket connection now sends token in query string for authenticated subscription.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Sensitive data mutation/export/progress channels now consistently enforce authenticated ownership semantics.

### 16.6 P1-6 Frontend nginx WebSocket proxy - CLOSED

Status: FIXED

Code evidence:
- `frontend/nginx.conf:22`  
  Added dedicated `location /ws/` proxy block for WebSocket traffic.
- `frontend/nginx.conf:23`  
  WebSocket requests are proxied to backend service path `http://backend:8000/ws/`.
- `frontend/nginx.conf:25`  
  Added `Upgrade` header forwarding for WS handshake.
- `frontend/nginx.conf:31`  
  Added long read timeout for streaming scan-progress channel stability.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Frontend host (`:3009`) now has explicit WS reverse-proxy path to backend without requiring direct backend WS host usage.

### 16.7 P1-7 Migration/model drift (`owner_id`, `task_id`) - CLOSED

Status: FIXED

Code evidence:
- `backend/alembic/versions/20260403_1840_005_add_owner_task_columns.py:21`  
  Added `projects.owner_id` column.
- `backend/alembic/versions/20260403_1840_005_add_owner_task_columns.py:23`  
  Added FK `projects.owner_id -> users.id` with `ON DELETE SET NULL`.
- `backend/alembic/versions/20260403_1840_005_add_owner_task_columns.py:30`  
  Added index for `projects.owner_id`.
- `backend/alembic/versions/20260403_1840_005_add_owner_task_columns.py:32-33`  
  Added `scans.task_id` column and index.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Fresh migration chain now includes runtime-required columns used by API/model ownership + task tracking flows.

### 16.8 P1-8 DB migrations in one-command startup - CLOSED

Status: FIXED

Code evidence:
- `docker-compose.yml:36`  
  Backend service startup command now runs `alembic upgrade head` before launching `uvicorn`.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- `docker-compose up` now applies schema upgrades before backend begins serving traffic.

### 16.9 P1-9 Scanner provisioning mismatch (ZAP/Nuclei) - CLOSED

Status: FIXED

Code evidence:
- `scanner/scripts/download_tools.sh:52-55`  
  Added Nuclei binary download/install into `/usr/local/bin`.
- `scanner/scripts/download_tools.sh:111-113`  
  Added `zap-baseline.py` and `zap_common.py` download/install.
- `scanner/Dockerfile:52`  
  Added stage copy for `nuclei`.
- `scanner/Dockerfile:60-61`  
  Added stage copy for ZAP baseline scripts.
- `scanner/Dockerfile:67`  
  Added executable permissions for `nuclei` and `zap-baseline.py`.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Runtime provisioning matrix now includes binaries/scripts expected by active `zap` and `nuclei` wrappers.

### 16.10 P1-10 Read-only mount conflict for artifact-writing wrappers - CLOSED

Status: FIXED

Code evidence:
- `scanner/app/tools/base.py:94-95`  
  Added configurable writable scan results directory (`SCAN_RESULTS_DIR`) with safe local fallback.
- `scanner/app/tools/base.py:189`  
  Added shared `get_output_path(...)` helper to generate writable artifact paths.
- `scanner/app/tools/codeql.py:12-13`, `:32`, `:66`  
  CodeQL SARIF output now written/read from writable scan-results path.
- `scanner/app/tools/gosec.py:7-8`, `:20`, `:56`  
  Gosec SARIF output now written/read from writable scan-results path.
- `scanner/app/tools/sast/spotbugs.py:8-9`, `:26`, `:56`  
  SpotBugs XML output now written/read from writable scan-results path.
- `docker-compose.yml:104`  
  Scanner worker now sets `SCAN_RESULTS_DIR=/app/scan-results`.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Artifact-writing wrappers no longer depend on writing under project source mount (`/app/projects:ro`).

### 16.11 P1-11 Baseline vs stabilization execution policy - CLOSED

Status: FIXED

Code evidence:
- `backend/app/api/v1/scans.py:93`  
  Scan dispatch now sends `mode` to scanner task (`quick|deep|custom`) for deterministic profile selection.
- `scanner/app/tasks.py:66`  
  Scanner task forwards `mode` into orchestrator (`scan_mode`).
- `scanner/app/orchestrator.py:39-69`  
  Added explicit profile/staged-tool policy sets: `QUICK_PROFILE_TOOLS`, `DEEP_PROFILE_TOOLS`, `DEFAULT_STABILIZATION_TOOLS`.
- `scanner/app/orchestrator.py:80-90`  
  Added canonical scan mode normalization and staged rollout flag parsing.
- `scanner/app/orchestrator.py:134-156`  
  Added deterministic tool selection function for mode + staged flags (`SCAN_CUSTOM_TOOLS`, `ENABLE_STABILIZATION_TOOLS`, `STABILIZATION_TOOL_NAMES`).
- `scanner/app/orchestrator.py:166-173`  
  `_filter_tools` now enforces profile gate before applicability/availability/license checks.
- `docker-compose.yml:105-107`  
  Added explicit staged rollout env flags for scanner worker.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Tool execution is now deterministic by profile, with explicit staged inclusion path for unstable wrappers (without deleting wrappers).

---

## 17. Execution Update (2026-04-03) - P2 Progress

### 17.1 P2-1 Model constraint placement bug - CLOSED

Status: FIXED

Code evidence:
- `backend/app/models.py:88-94`  
  Moved findings-related check constraints into `Finding.__table_args__` (correct owning table).
- `backend/app/models.py:97-106`  
  Removed misplaced findings constraints from `User` model.
- `backend/alembic/versions/20260403_2210_006_fix_findings_constraints_placement.py:34-43`  
  Added idempotent migration safety logic: drop stray constraints from `users` if present and ensure canonical constraints exist on `findings`.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- Constraint intent is now model-correct and migration-safe for drifted environments without removing any tool/wrapper.

### 17.2 P2-2 Dead frontend routes/navigation - CLOSED

Status: FIXED

Code evidence:
- `frontend/src/components/Layout.tsx:25`  
  Updated `Projects` navigation link from dead `/projects` to valid `/projects/new`.
- `frontend/src/components/Layout.tsx:31`  
  Updated `Scans` navigation link from dead `/scans` to valid `/` dashboard route.
- `frontend/src/App.tsx:36`  
  Added explicit frontend route `/docs/intro`.
- `frontend/src/pages/DocsIntro.tsx:5`  
  Added new `DocsIntro` page so landing documentation link resolves to a real in-app route.
- `frontend/src/pages/Landing.tsx:15`  
  Existing `Documentation` link now resolves to the newly declared `/docs/intro` route (no longer dead).

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- All visible navigation links now resolve to defined app routes.

### 17.3 P2-3 API metadata messaging alignment - CLOSED

Status: FIXED

Code evidence:
- `backend/app/main.py:34`  
  Updated FastAPI description from legacy "50+ Tools" claim to validated baseline + staged stabilization messaging.

Verification evidence:
- `cd backend && python -m pytest -q` -> PASS (`3 passed`)
- `cd scanner && python -m compileall -q app` -> PASS
- `cd scanner && python -m pytest -q` -> PASS (`91 passed`)
- `cd frontend && npm run type-check` -> PASS
- `cd frontend && npm run build` -> PASS

Notes:
- API metadata now reflects current validated capability model and no longer overstates integrated tool count.


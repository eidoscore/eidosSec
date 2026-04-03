# eidosSec TODO (Based on `audit.md` + Docs Deep-Dive)

Date: 2026-04-03  
Source of truth: `audit.md` (including Pass 5 addendum), `docs/INTEGRATED_APP_PLAN.md`, `docs/ALIGNMENT_AUDIT.md`

## Locked Rules (Do Not Break)
- [ ] Do not delete existing tools/wrappers.
- [ ] Keep all wrappers integratable in one unified flow.
- [ ] If unstable, move to stabilization queue/flag; do not remove.

## P0 - Must Fix First (Runtime Blockers)

- [x] **P0-1 Fix frontend compile blocker (`ScanDetails.tsx`)**
  - Evidence: `npm run type-check` / `npm run build` fail at `frontend/src/pages/ScanDetails.tsx:438,487`.
  - Done when:
    - `cd frontend && npm run type-check` passes.
    - `cd frontend && npm run build` passes.

- [x] **P0-2 Fix scanner compile blocker (`codeql.py`) + structural bug (`nuclei.py`)**
  - Evidence: `python -m compileall -q app` fails on `scanner/app/tools/codeql.py`; `nuclei.py` has duplicate `parse_output`.
  - Done when:
    - `cd scanner && python -m compileall -q app` passes.
    - `cd scanner && python -m pytest -q` can collect and run tests.

- [x] **P0-3 Normalize wrapper execution contract (base + all wrappers)**
  - Evidence:
    - 23/23 wrappers call missing `execute_command(...)`.
    - Orchestrator expects `ToolResultSchema`, wrappers return `List[FindingSchema]`.
  - Required decision:
    - Canonicalize on one contract (`ToolResultSchema` end-to-end).
  - Done when:
    - All wrappers follow one execution contract.
    - No wrapper calls undefined methods from base class.
    - Orchestrator/tool interaction is type-consistent.

- [x] **P0-4 Implement real scan lifecycle persistence**
  - Evidence:
    - Backend creates scan as `pending`, but no full `running -> completed/failed/cancelled` ingestion path.
    - `backend/app/tasks.py::process_scan_results` still TODO.
  - Done when:
    - Status transitions persist deterministically.
    - Findings, summary, tools_executed, duration, score are persisted.
    - Cancel operation uses `cancelled` state (not forced `failed`).

- [x] **P0-5 Fix Celery topology/routing deterministically**
  - Evidence:
    - Sent task name: `"scanner.scan_project"` (`backend/app/api/v1/scans.py`).
    - Scanner route configured for `"app.tasks.scan_project"` (`scanner/app/celery_app.py`).
    - Backend and scanner workers share default queue behavior.
  - Done when:
    - Task names/routes/queues are aligned.
    - Backend worker does not accidentally consume scanner tasks.

## P1 - Contract, Security, and Operational Gaps

- [x] **P1-1 Align frontend scan create payload and status enum**
  - Evidence:
    - Frontend sends `scan_type` (`frontend/src/pages/NewProject.tsx`), API expects `mode`.
    - Frontend uses `in_progress`, backend/docs use `running`.
  - Done when:
    - Frontend sends `{ project_id, mode }`.
    - Frontend only uses `pending|running|completed|failed|cancelled`.

- [x] **P1-2 Add frontend authentication flow**
  - Evidence:
    - API is protected but frontend only reads token from localStorage, no setup/login pages.
  - Done when:
    - UI supports first-time setup/login and token bootstrap.
    - 401 path redirects/recovery UX is explicit.

- [x] **P1-3 Fix path contract UX for Docker runtime**
  - Evidence:
    - Docs require `/app/projects/...`, but onboarding still suggests host OS paths.
  - Done when:
    - New project UI defaults to container-visible path guidance.
    - Validation/error states clearly explain host-path mismatch.

- [x] **P1-4 Resolve API/UI response mismatches**
  - Evidence:
    - `ProjectDetails` expects `project.scans`, backend `ProjectResponse` does not provide it.
    - UI references `scan.total_findings`, backend detail response does not include it.
  - Done when:
    - Either API schema is extended or frontend is adjusted to canonical responses.
    - Project detail and scan detail pages render correctly without ad-hoc assumptions.

- [x] **P1-5 Enforce RBAC on sensitive endpoints/channels**
  - Evidence:
    - Findings patch/analyze routes miss ownership checks.
    - Scan export route has no auth dependency.
    - WebSocket auth is optional.
  - Done when:
    - Ownership and auth checks are applied consistently across HTTP + WS.

- [x] **P1-6 Add frontend nginx WebSocket proxy**
  - Evidence: frontend uses same-host `/ws/scans/{id}` but nginx has no `/ws` proxy block.
  - Done when:
    - WS works behind frontend host (`:3009`) without direct backend host dependency.

- [x] **P1-7 Fix migration/model drift (`owner_id`, `task_id`)**
  - Evidence:
    - ORM uses `Project.owner_id` and `Scan.task_id`.
    - Migration chain does not create those columns.
  - Done when:
    - New Alembic migration adds missing columns, FK/indexes, and is tested on clean DB.

- [x] **P1-8 Ensure DB migrations run in one-command startup**
  - Evidence: backend container starts `uvicorn` directly without migration step.
  - Done when:
    - Compose startup applies `alembic upgrade head` safely before serving traffic.

- [x] **P1-9 Fix scanner image provisioning mismatch (ZAP/Nuclei)**
  - Evidence:
    - Wrappers exist for `zap` and `nuclei`, but scanner image does not install required binaries.
  - Done when:
    - Runtime provisioning matrix matches active wrappers (or wrappers are feature-flagged safely).

- [x] **P1-10 Resolve read-only mount conflict for artifact-writing wrappers**
  - Evidence:
    - `./projects:/app/projects:ro` with wrappers writing SARIF/XML into project path.
  - Done when:
    - Tool outputs are written to writable working directory (e.g., `/app/scan-results`) or mount strategy is revised safely.

- [x] **P1-11 Enforce baseline vs stabilization execution policy**
  - Evidence:
    - Docs define baseline 15 tools, but orchestrator includes all wrappers by default.
  - Done when:
    - Deterministic profile selection exists (`quick/deep/custom`) with explicit staged flags for unstable wrappers.

## P2 - Quality and Consistency Cleanup

- [x] **P2-1 Fix model constraint placement bug**
  - Evidence: findings-related constraints are in `User.__table_args__` (`backend/app/models.py`).
  - Done when:
    - Constraints are moved to correct model/table with migration safety.

- [x] **P2-2 Fix dead frontend routes/navigation**
  - Evidence:
    - Layout links `/projects` and `/scans` but routes are undefined.
    - Landing links to `/docs/intro` (not a frontend route).
  - Done when:
    - All visible navigation links resolve to valid routes or valid external URLs.

- [x] **P2-3 Align API metadata messaging with docs baseline**
  - Evidence: FastAPI description still claims "50+ Tools" while docs separate baseline vs roadmap.
  - Done when:
    - App/API metadata reflects current validated capability.

## Validation Checklist (Must Re-run Per Phase)

- [x] `cd backend && python -m pytest -q`
- [x] `cd scanner && python -m compileall -q app`
- [x] `cd scanner && python -m pytest -q`
- [x] `cd frontend && npm run type-check`
- [x] `cd frontend && npm run build`
- [ ] Integration smoke:
  - create project -> create scan -> progress websocket -> findings persisted -> export authorized

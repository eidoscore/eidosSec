# SESSION ARTIFACT - eidosSec

Date: 2026-04-03 (Asia/Jakarta)
Repo: D:\Project\eidosSec
Primary source report: `audit.md`

## 1) Locked Product Rules (Must Keep)
- Do not delete existing tools/wrappers.
- All existing tools must be integratable into one eidosSec flow.
- If unstable, tool stays in stabilization queue (not removed).

## 2) Current Reality Snapshot
- Docs alignment was completed and normalized in `/docs`.
- Deep-dive audit already updated through Pass 4 in `audit.md`.
- Current implementation is **not** end-to-end stable yet for unified all-tools flow.

## 3) Highest Priority Blockers (P0)
1. Celery topology/routing mismatch.
- Backend triggers `scanner.scan_project`, but scanner routing config mismatches task name.
- Risk: task misroute / worker mismatch.

2. Scan lifecycle not implemented end-to-end.
- `pending -> running -> completed/cancelled` transitions are incomplete.
- Backend result ingestion (`process_scan_results`) still TODO.

3. Migration vs model/API mismatch.
- `Project.owner_id` and `Scan.task_id` used by code, but not present in migration chain.

4. Frontend cannot build (JSX error in `ScanDetails.tsx`).

5. Path contract mismatch (Windows onboarding vs Docker runtime paths).
- UI suggests `C:\...`, while containerized scanner expects mounted `/app/projects/...` paths.

6. Frontend auth flow missing while APIs are protected.
- UI reads token from localStorage but has no login/setup path in app flow.

## 4) Important P1/P2 Gaps
- WS proxy gap: frontend nginx has no `/ws` proxy to backend.
- WS auth currently optional (authorization gap if token absent).
- UI/API response mismatches (`project.scans`, `scan.total_findings`, etc).
- Read-only project volume conflicts with wrappers writing result artifacts (CodeQL/Gosec/SpotBugs).
- Wrapper contract still inconsistent (`execute_command` usage vs base contract).

## 5) Recommended Execution Order (Next Session)
Phase A (unblock runtime)
1. Fix frontend compile error in `frontend/src/pages/ScanDetails.tsx`.
2. Fix scanner compile blocker (`scanner/app/tools/codeql.py` indentation/structure).
3. Normalize wrapper execution contract (base + all wrappers).

Phase B (make scan lifecycle real)
1. Fix Celery task routing/topology.
2. Implement backend result ingestion persistence.
3. Implement status transitions: pending -> running -> completed/failed/cancelled.

Phase C (make schema and API safe)
1. Add migration(s) for `owner_id`, `task_id` (+ related constraints/indexes).
2. Align UI payload/status contracts (`mode`, status enum, response fields).
3. Add frontend auth entry flow and token bootstrap.

Phase D (operational hardening)
1. Fix WS proxy + enforce WS auth/RBAC.
2. Resolve read-only artifact write strategy for file-output tools.
3. Re-test end-to-end with docker-compose and minimal real scan.

## 6) Minimum Validation Checklist
Backend:
- `python -m pytest -q`

Scanner:
- `python -m compileall -q app`
- `python -m pytest -q`

Frontend:
- `npm run type-check`
- `npm run build`

Integration:
- create project -> create scan -> progress websocket -> findings persisted -> export works.

## 7) Where To Continue Reading First
1. `audit.md` (single source of truth findings)
2. `docs/INTEGRATED_APP_PLAN.md` (execution target)
3. `docs/ALIGNMENT_AUDIT.md` (contract alignment decisions)

## 8) Resume Prompt Template (Copy for New Session)
"Lanjutkan eidosSec dari `D:\\Project\\eidosSec` pakai `audit.md` sebagai source of truth. Fokus P0 dulu: fix compile frontend+scanner, normalisasi wrapper contract, benahi Celery routing, implement result persistence + status lifecycle, lalu align migration `owner_id/task_id`. Ingat: jangan hapus tools existing, semua harus tetap integratable."

## 9) Notes
- Current worktree is dirty with many modified/deleted files.
- Do not run destructive git commands.
- Continue incrementally with verification at each phase.

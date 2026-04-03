# Documentation Alignment Audit

Last updated: 2026-04-02
Scope: `D:\Project\eidosSec\docs`

## Objective
Deep-dive audit to remove inconsistencies across documentation related to:
- API contracts
- Database schema assumptions
- Scan status lifecycle
- Tool inventory and tier claims
- Runtime setup and ports

## Key Inconsistencies Found

1. Frontend port mismatch
- Some docs used `http://localhost:3000`.
- Compose currently publishes frontend at `http://localhost:3009`.

2. Scan request payload mismatch
- Docs used `scan_type` and numeric project id examples.
- Backend expects `project_id` (UUID) and `mode` (`quick|deep|custom`).

3. Scan status mismatch
- Some docs/UI narratives used `in_progress`.
- Backend model constraint uses `pending|running|completed|failed|cancelled`.

4. Tool-count drift
- Docs alternated between 15, 21+, 50+, and 63 as if all were already stable.
- Repo currently has a stable baseline plus additional wrappers not fully stabilized.

5. Path contract ambiguity in Docker mode
- Docs implied direct host path scanning from UI.
- Scanner runs in container context and needs mounted paths.

6. PRO/license contract drift
- Spec documented full JWT-based enforcement in backend.
- Current implementation uses scanner-side verifier with placeholder assumptions.

## Alignment Decisions Applied

1. Canonical runtime and ports
- Frontend: `3009`
- Backend: `8000`
- Monitoring: `9000`

2. Canonical API request/response contracts
- Create scan uses `mode` and UUID `project_id`.
- Status enum standardized to backend model values.
- WebSocket event shape documented according to orchestrator progress payload.

3. Canonical tool reporting
- Distinguish clearly between:
  - Current stable baseline
  - Experimental/partial wrappers
  - Target roadmap counts

4. Canonical path guidance
- Document container-accessible path requirement for scanner workloads.

5. Canonical planning doc
- Added `INTEGRATED_APP_PLAN.md` as single roadmap source for all-in-one integration.
6. Tool preservation policy
- Added explicit "no deletion" rule: all existing wrappers remain mandatory integration targets.

## Residual Code Gaps (documented, not fixed here)
- Scanner wrapper contract mismatch (`execute_command` usage vs base class contract).
- Syntax error in `scanner/app/tools/codeql.py`.
- Frontend compile issue in `frontend/src/pages/ScanDetails.tsx`.
- Backend result processing TODOs in `backend/app/tasks.py`.

## Outcome
All documents in `docs/` were rewritten or adjusted to follow one coherent contract and roadmap, with explicit separation between current implementation and planned expansion.

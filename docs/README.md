# eidosSec Documentation Index

Last updated: 2026-04-02
Status: Aligned

## Source-of-Truth Documents
- `api.md`: API contracts (request/response, enums, websocket payload).
- `installation.md`: runtime setup, ports, and path contract.
- `usage.md`: operator workflow.
- `tools.md`: current baseline tools + expansion readiness notes.
- `INTEGRATED_APP_PLAN.md`: all-in-one implementation roadmap.
- `ALIGNMENT_AUDIT.md`: alignment decisions and deep-dive audit findings.

## Locked Product Rule
- No existing tool/wrapper is removed from scope.
- All existing tools must be integrated in eidosSec (stabilize if needed, do not delete).

## Supporting Documents
- `CICD_SETUP.md`: CI/CD quality gates and deployment checks.
- `ONBOARDING_OPTIMIZATION.md`: UX and contract-focused onboarding improvements.
- `PRO_LICENSE_SPEC.md`: license gating architecture and open work.
- `PRO_TOOLS_MATRIX.md`: baseline vs extended vs roadmap tool matrix.
- `LAUNCH_MATERIALS.md`: externally safe messaging aligned to current docs.
- `blog/`: long-form content aligned with current capability framing.

## Canonical Runtime Values
- Frontend: `http://localhost:3009`
- Backend: `http://localhost:8000`
- Monitoring: `http://localhost:9000`

## Canonical Scan Contract
- Status: `pending|running|completed|failed|cancelled`
- Create payload:
```json
{
  "project_id": "<uuid>",
  "mode": "quick"
}
```

## Closure Checklist
- [x] Port and endpoint references aligned across docs.
- [x] Scan payload and status enum aligned across docs.
- [x] Tool-count claims separated by baseline vs roadmap.
- [x] Non-removal policy documented (all existing tools remain integration targets).
- [x] Docker path contract documented consistently.
- [x] Local markdown links verified (no broken local links).

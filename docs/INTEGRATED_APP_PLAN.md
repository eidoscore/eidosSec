# eidosSec All-in-One Integration Plan

Last updated: 2026-04-02
Owner: eidosSec engineering
Status: Active plan

## 1. Goal
Build a single self-hosted application that unifies:
- Code quality and security static analysis (SAST)
- Dependency and supply-chain checks (SCA)
- Secrets detection
- Dynamic app security testing (DAST)
- API mock and contract testing
- End-to-end feature testing
- Centralized findings, triage, and reporting

## 1.1 Tool Preservation Policy (Locked Requirement)
- No existing tool integration is removed from repository scope.
- Every existing tool/wrapper must be integrated into the unified eidosSec pipeline.
- If a tool is unstable, it is moved to a stabilization queue, not deleted.
- Roadmap execution must converge to "all existing tools integrated" with consistent contracts.

## 2. Current Baseline (from repository state)
- Runtime stack: `frontend` (React), `backend` (FastAPI), `scanner` (Celery worker), `postgres`, `redis`, `monitoring`.
- Default ports: frontend `3009`, backend `8000`, monitoring `9000`.
- Stable integrated scanner set: 15 tools (FREE baseline).
- Additional wrappers exist for PRO/extended tools, but not fully stabilized.

## 3. Mandatory Stabilization Before Expansion (Phase 0)
These are blockers that must be fixed before adding more tools/features:
1. Scanner wrapper contract mismatch
- Current wrappers call `execute_command(...)` but base class does not provide that method.
- Base orchestrator expects `ToolResultSchema`; many wrappers return `List[FindingSchema]`.
2. Syntax blockers in scanner and frontend
- `scanner/app/tools/codeql.py` has an `IndentationError`.
- `frontend/src/pages/ScanDetails.tsx` has JSX structure/type-check errors.
3. Scan lifecycle persistence gap
- Scan tasks are queued, but result processing/persistence in backend is incomplete (`backend/app/tasks.py` TODOs).
4. Status enum mismatch across UI behavior
- Canonical backend status: `pending|running|completed|failed|cancelled`.
- Frontend logic still partially expects `in_progress`.
5. Docker path contract ambiguity
- Scanner can only access mounted paths in container context.
- Documentation and UI examples must avoid host-path ambiguity.

## 4. Target Functional Scope (All-in-One)

### 4.1 Security and Quality
- SAST: Semgrep, Bandit, ESLint security, PHPStan, Brakeman, and extended analyzers.
- SCA: Trivy + ecosystem-native audits + extended scanners.
- Secrets: TruffleHog, Gitleaks, and optional complementary detectors.
- IaC: Checkov, cfn-nag, KICS, and optional Kubernetes-specific tooling.
- DAST: OWASP ZAP + Nuclei baseline.

### 4.2 API Validation and Mock Data
- OpenAPI/GraphQL contract import.
- Mock server support (planned: Prism-compatible workflow).
- Property-based API fuzz testing (planned: Schemathesis-compatible workflow).

### 4.3 Feature Testing
- Playwright-based E2E suites integrated as first-class scan artifacts.
- Findings mapped into same triage surface as security findings.

### 4.4 Unified Data Plane
- One canonical finding schema across all engines.
- Deduplication by path/type/line proximity/tool correlation.
- Unified severity and confidence model.

## 5. Delivery Phases

### Phase 0 - Stabilize Existing Core (required)
- Fix scanner wrapper contract and syntax blockers.
- Fix frontend compile and status mapping.
- Implement backend persistence for scan results and findings.
- Add integration tests for end-to-end scan lifecycle.

### Phase 1 - Contract Hardening
- Lock API contract for scans/findings/progress events.
- Add explicit schema versioning for scanner payloads.
- Add migration-safe DB schema docs and examples.

### Phase 2 - Capability Expansion
- Stabilize all currently present wrappers until each passes integration-readiness criteria.
- Add API mock + contract testing pipeline.
- Add feature E2E test ingestion and reporting.

### Phase 3 - Operationalization
- CI profiles (`quick`, `deep`, `custom`) with deterministic tool sets.
- Better observability: run history, duration, failure reason, retry diagnostics.
- Export pipeline (JSON first, additional formats optional).

### Phase 4 - Commercial/License Controls
- Move from placeholder verification to auditable license service.
- Enforce plan gating in backend and scanner consistently.

## 6. Canonical Contracts (must be preserved)

### 6.1 Scan Status Enum
`pending`, `running`, `completed`, `failed`, `cancelled`

### 6.2 Create Scan Request
```json
{
  "project_id": "<uuid>",
  "mode": "quick"
}
```

### 6.3 WebSocket Progress Event
```json
{
  "scan_id": "<uuid>",
  "progress": 42,
  "message": "Running semgrep...",
  "timestamp": "2026-04-02T10:00:00+00:00",
  "tools_list": ["semgrep", "bandit"],
  "current_tool": "semgrep",
  "tool_status": "running",
  "findings_count": 3
}
```

## 7. Definition of Done for All-in-One v1
- End-to-end scan lifecycle works from UI create-scan to persisted findings without manual intervention.
- API docs, implementation, and database schema are consistent and test-validated.
- Quick profile reproducibly executes baseline tools in CI.
- All existing tools in repository are either:
  - integrated and production-ready, or
  - integrated behind explicit staged rollout flags with active stabilization tests.
- API mock/contract tests and E2E feature tests can run and publish into same findings model.
- Documentation is aligned and versioned with code.

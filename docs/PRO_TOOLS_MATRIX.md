# PRO Tools Matrix

Last updated: 2026-04-02

## Matrix Model
This matrix separates **current baseline**, **repository-present wrappers**, and **target roadmap**.

## Non-Removal Rule
- Existing tools/wrappers are not removed from scope.
- Every existing wrapper must be brought into integrated execution flow.
- Unstable wrappers remain tracked in stabilization stage until passing readiness criteria.

## 1. Current Baseline (intended stable)

### SAST
- Semgrep
- Bandit
- ESLint security
- PHPStan
- Brakeman

### Secrets
- TruffleHog
- Gitleaks

### SCA
- Trivy
- Safety
- npm audit
- Composer audit

### DAST
- OWASP ZAP
- Nuclei

### IaC
- Checkov
- cfn-nag

Total baseline: 15 tools

## 2. Repository-Present Extended Wrappers (stabilization stage)
- CodeQL
- Gosec
- Staticcheck
- SpotBugs
- PMD
- ShellCheck
- Retire.js
- KICS

These are part of near-term expansion but should not be treated as fully production-ready until stabilization tasks in `INTEGRATED_APP_PLAN.md` Phase 0 and Phase 2 are complete.
They remain mandatory integration targets under the non-removal policy.

## 3. Target Expansion Buckets (roadmap)
- Additional SAST analyzers by language.
- Broader DAST and API security tooling.
- Extra SCA and container supply-chain scanners.
- Feature testing ingestion (Playwright) and API contract fuzzing.

## 4. Integration Readiness Criteria Per Tool
A tool is "production-ready" only when all are true:
1. Wrapper returns canonical `ToolResultSchema`.
2. Binary availability is validated in image/runtime.
3. JSON/SARIF parser is covered by tests.
4. Findings map into unified schema without lossy fields.
5. Failure behavior is deterministic and logged.

## 5. Source of Truth
Use this file + `INTEGRATED_APP_PLAN.md` for planning and status communication.

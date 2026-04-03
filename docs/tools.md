# Security Tools and Capability Matrix

## Policy
- Existing tools/wrappers in repository are preserved (no deletion policy).
- Any wrapper not yet stable is queued for integration hardening, not removal.
- Target state is full integration of all existing tool wrappers into one unified pipeline.

## Current Baseline (stable target)
The baseline scanning profile currently targets 15 tools:

### SAST
- Semgrep
- Bandit
- ESLint (security rules)
- PHPStan
- Brakeman

### SCA
- Trivy
- Safety
- npm audit
- Composer audit

### Secrets
- TruffleHog
- Gitleaks

### DAST
- OWASP ZAP
- Nuclei

### IaC
- Checkov
- cfn-nag

## Extended Wrappers Present in Repository (stabilization required)
Additional wrappers exist for:
- CodeQL
- Gosec
- Staticcheck
- SpotBugs
- PMD
- ShellCheck
- Retire.js
- KICS

These are part of expansion roadmap and require contract/runtime hardening before production claims.

## How tool execution is selected
- Language and framework detectors run first.
- Tools are filtered by applicability and availability.
- License gate may exclude paid-tier tools.

## Output normalization model
All findings should map into unified fields:
- `type`
- `severity`
- `confidence`
- `file_path`
- `line_start`, `line_end`
- `message`
- `code_snippet`
- `cwe_id`
- `owasp_category`
- `metadata`

## Deduplication intent
Findings are deduplicated by:
- same file path,
- near line proximity,
- compatible type signatures.

## Roadmap reference
For full all-in-one expansion (API mock, feature testing, broader toolchain), see `INTEGRATED_APP_PLAN.md`.

# PRO License Specification

Last updated: 2026-04-02
Status: Revised to match current code and target roadmap

## 1. Scope
Define license-gated behavior for advanced scan capabilities while keeping free baseline accessible.

## 2. Current Implementation Snapshot
Current repository behavior:
- License verification logic currently lives in scanner (`app/services/license.py`).
- Scanner checks license before running `requires_license` tools.
- If no valid key, plan falls back to free.
- Verification response mapping is still placeholder-level and needs hardening.

## 3. Target Architecture
Move to explicit, auditable licensing contract:
1. Backend becomes source of truth for plan and feature flags.
2. Scanner receives signed feature snapshot per scan request.
3. Frontend consumes same feature snapshot for UI gating.
4. License data persisted with activation and verification metadata.

## 4. Canonical Feature Flags (target)
- `max_projects`
- `max_concurrent_scans`
- `enabled_scan_modes`
- `enabled_tools`
- `ai_analysis`
- `advanced_exports`

## 5. Enforcement Layers

### Backend (required)
- Enforce project and concurrency limits at API boundary.
- Enforce scan mode access (`quick/deep/custom`).
- Emit deterministic error codes for denied features.

### Scanner (required)
- Enforce tool-level license requirements from signed feature payload.
- Log skipped tools with reason (`not_applicable|not_available|license_required`).

### Frontend (required)
- Hide/disable unavailable actions using server-provided feature map.
- Do not rely solely on client-side assumptions.

## 6. Data Contract Example
```json
{
  "plan": "free",
  "features": {
    "max_projects": 3,
    "max_concurrent_scans": 1,
    "enabled_scan_modes": ["quick"],
    "enabled_tools": ["semgrep", "bandit"],
    "ai_analysis": false,
    "advanced_exports": false
  }
}
```

## 7. Open Work
- Replace placeholder plan inference in scanner verifier.
- Add backend license endpoint and persistent storage model.
- Add tests for parity between backend and scanner gating decisions.

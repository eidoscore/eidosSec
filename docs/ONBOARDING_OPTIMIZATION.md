# Onboarding Optimization Plan

Last updated: 2026-04-02

## Objective
Reduce time-to-first-successful-scan while keeping contracts accurate.

## Current UX Baseline
- New project wizard exists.
- Project detection endpoint exists (`POST /api/v1/projects/detect`).
- Auto-scan option exists in onboarding flow.
- Scan details UI includes progress, tool list, findings, and export.

## High-Priority UX + Contract Fixes
1. Align status mapping to backend enums
- Use `pending|running|completed|failed|cancelled` only.
- Remove `in_progress` assumptions in frontend polling and WebSocket conditions.

2. Clarify path entry UX
- Default helper should recommend container path format (`/app/projects/<name>`).
- Explain host-path vs container-path mismatch directly in UI hint text.

3. Surface scan lifecycle reliability
- Show explicit warning if scan record is pending too long without task progress.
- Add "task queued / task started" markers.

4. Improve empty-result messaging
- Distinguish "no findings" vs "scan failed" vs "no findings persisted yet".

## Mid-Priority Improvements
1. Add project path validator endpoint behavior hints in wizard.
2. Add scan profile descriptions (`quick/deep/custom`) in UI.
3. Add direct links to API docs for self-hosted operators.

## Acceptance Criteria
- New user can create project and start quick scan in <3 minutes.
- Status labels are consistent with backend model.
- Path-related failures are understandable from UI without checking logs.

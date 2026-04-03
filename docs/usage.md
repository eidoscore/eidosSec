# Usage Guide

## 1. Initial Setup
1. Open `http://localhost:3009`.
2. Create first admin account through setup/login flow.
3. Confirm backend health at `http://localhost:8000/api/v1/health`.

## 2. Create Project
1. Click **New Project**.
2. Fill project name.
3. Provide scanner-accessible absolute path (recommended: `/app/projects/<project-folder>`).
4. Optional: call project detection to prefill languages/framework.

## 3. Start Scan
1. Trigger scan from project page or onboarding flow.
2. Request payload uses:
```json
{
  "project_id": "<uuid>",
  "mode": "quick"
}
```
3. Track progress in scan details page and WebSocket stream.

## 4. Monitor Progress
- Status lifecycle: `pending` -> `running` -> `completed|failed|cancelled`
- Progress stream path: `ws://localhost:8000/ws/scans/{scan_id}`

## 5. Review Findings
1. Open scan detail page.
2. Filter findings by severity/tool.
3. Open finding details to inspect message, snippet, CWE/OWASP fields.
4. Optional: trigger AI analysis per finding (requires AI feature flags/keys).

## 6. Export
Use scan export endpoint or UI action to download JSON findings.

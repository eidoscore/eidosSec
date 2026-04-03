# API Documentation

Base URL: `http://localhost:8000`
API prefix: `/api/v1`

## Interactive Docs
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication
Most endpoints require Bearer token.
- Login: `POST /api/v1/auth/login`
- Current user: `GET /api/v1/auth/me`

## Core Resources

### Projects
- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}` (admin)
- `POST /api/v1/projects/detect`

Create project example:
```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-app",
    "path": "/app/projects/my-app",
    "languages": ["Python"],
    "framework": "FastAPI",
    "settings": {}
  }'
```

### Scans
- `POST /api/v1/scans`
- `GET /api/v1/scans`
- `GET /api/v1/scans/stats`
- `GET /api/v1/scans/{scan_id}`
- `GET /api/v1/scans/{scan_id}/findings`
- `POST /api/v1/scans/{scan_id}/cancel`
- `GET /api/v1/scans/{scan_id}/export`

Create scan example:
```bash
curl -X POST "http://localhost:8000/api/v1/scans" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "11111111-2222-3333-4444-555555555555",
    "mode": "quick"
  }'
```

### Findings
- `GET /api/v1/findings/{finding_id}`
- `PATCH /api/v1/findings/{finding_id}`
- `POST /api/v1/findings/{finding_id}/analyze`

## Canonical Scan Status Values
`pending`, `running`, `completed`, `failed`, `cancelled`

## WebSocket Progress API
Endpoint:
- `ws://localhost:8000/ws/scans/{scan_id}`

Progress payload fields:
```json
{
  "scan_id": "<uuid>",
  "progress": 50,
  "message": "Running semgrep...",
  "timestamp": "2026-04-02T10:00:00+00:00",
  "tools_list": ["semgrep", "bandit"],
  "current_tool": "semgrep",
  "tool_status": "running",
  "findings_count": 4,
  "error": null
}
```

## Contract Notes
- `project_id` and `scan_id` are UUIDs.
- Scan mode enum: `quick|deep|custom`.
- Use scanner-accessible path conventions in project creation.

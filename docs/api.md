# API Documentation

eidosSec provides a fully documented REST API built with FastAPI. All frontend features are implemented via these public APIs.

## 📚 Interactive Documentation

When running locally, you can access the full interactive documentation (Swagger UI) at:

[**http://localhost:8000/docs**](http://localhost:8000/docs)

Or the ReDoc alternative at:

[**http://localhost:8000/redoc**](http://localhost:8000/redoc)

## Core Resources

### 📁 Projects
Manage the code repositories you want to scan.
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Register a new project path
- `POST /api/v1/projects/detect` - Auto-detect language/framework

### 🔍 Scans
Trigger and monitor security scans.
- `POST /api/v1/scans` - Start a new scan for a project
- `GET /api/v1/scans/{id}` - Get status (progress, current tool)
- `GET /api/v1/scans/{id}/export` - Download findings as JSON

### 🐞 Findings
Access the vulnerabilities discovered.
- `GET /api/v1/scans/{id}/findings` - List findings with pagination
- `GET /api/v1/findings/{id}` - Get full details including code snippet and AI analysis

## Example Usage

**1. Create a Project**

```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
     -H "Content-Type: application/json" \
     -d '{"name": "My App", "path": "/path/to/source"}'
```

**2. Start a Scan**

```bash
curl -X POST "http://localhost:8000/api/v1/scans" \
     -H "Content-Type: application/json" \
     -d '{"project_id": 1, "scan_type": "quick"}'
```

**3. Poll Status**

```bash
curl "http://localhost:8000/api/v1/scans/{scan_id}"
```

## WebSocket API

For real-time updates, connect to:

`ws://localhost:8000/ws/scans/{scan_id}`

**Events:**
- `tool_start`: When a specific tool begins execution
- `tool_complete`: When a tool finishes (includes finding count)
- `progress`: Overall percentage update (0-100)

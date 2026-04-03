# Introduction to eidosSec

eidosSec is a self-hosted security scanning platform designed to run multiple open-source engines in one application stack.

## What eidosSec does today
- Manages projects and scan runs from a web UI.
- Runs orchestrated security tools through a scanner worker.
- Streams scan progress via WebSocket.
- Stores scan and finding data in PostgreSQL.

## Architecture
1. Frontend (`React + Vite`) for project and scan workflows.
2. Backend (`FastAPI`) for auth, project, scan, and findings APIs.
3. Scanner worker (`Celery`) for tool orchestration and result generation.
4. PostgreSQL for persistent data.
5. Redis for queueing and pub/sub progress events.

## Runtime defaults
- Frontend: `http://localhost:3009`
- Backend API: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`
- Monitoring API: `http://localhost:9000`

## Documentation navigation
Use `docs/README.md` as the index and source-of-truth map for all documents.

## Current documentation model
To keep expectations clear, docs separate:
- **Current baseline**: what is available/stable in repository now.
- **Target roadmap**: planned all-in-one expansion (see `INTEGRATED_APP_PLAN.md`).

# Installation Guide

## Requirements
- Docker Engine 20.10+
- Docker Compose v2+
- RAM: 8 GB recommended
- Disk: 10 GB recommended

## Quick Start
```bash
git clone <your-repo-url> eidosSec
cd eidosSec
docker-compose up -d --build
```

## Service Endpoints
- Frontend: `http://localhost:3009`
- Backend API: `http://localhost:8000`
- Backend health: `http://localhost:8000/api/v1/health`
- Monitoring health: `http://localhost:9000/health`

## Verify Containers
```bash
docker-compose ps
```
Expected running services:
- `frontend`
- `backend`
- `celery-worker`
- `scanner`
- `postgres`
- `redis`
- `monitoring`

## Project Path Contract (Important)
Scanner runs inside container context. The scan path must be readable by scanner container.

Recommended workflow:
1. Put source code under repository-mounted `./projects` directory.
2. Use container-visible absolute path such as `/app/projects/<project-folder>` when creating a project.

If you provide a host-only path that is not mounted into scanner container, scan will fail path validation.

## Windows Notes
- WSL2 is strongly recommended.
- Keep repository inside WSL filesystem for better I/O performance.
- Even on Windows host, submit scanner path in container form (for example `/app/projects/my-app`).

## Troubleshooting

### Port already in use
If `8000` or `3009` is occupied, edit `docker-compose.yml` host port mappings and restart.

### Scanner exits / OOM
Increase Docker memory allocation (8 GB recommended for heavier scans).

### API healthy but no findings persisted
Check scanner/backend logs for lifecycle blockers and task processing TODOs.

# CI/CD Setup

Last updated: 2026-04-02

## Goal
Provide repeatable CI/CD for eidosSec services with clear build/deploy health checks.

## Recommended Pipelines

### 1. Validate
Trigger: pull request and push
- Backend: lint + unit tests
- Scanner: lint + unit tests + syntax compile checks
- Frontend: type-check + build
- Contract checks: API schema and status enums

### 2. Build
Trigger: merge to main
- Build images: `frontend`, `backend`, `scanner`, `monitoring`
- Tag images by commit SHA
- Run smoke stack boot in CI

### 3. Deploy
Trigger: manual approval or release tag
- Pull latest images on target host
- Run `docker-compose up -d`
- Run post-deploy health checks

## Health Checks to Gate Deployment
- `GET /api/v1/health` returns healthy dependencies
- Frontend reachable on configured host port (default `3009`)
- Scanner worker connected to Redis and accepting jobs

## Mandatory Quality Gates
1. Scanner compile gate
```bash
cd scanner
python -m compileall -q app
```
2. Frontend compile gate
```bash
cd frontend
npm run type-check
npm run build
```
3. Backend tests
```bash
cd backend
python -m pytest -q
```

## Environment Contract
Use one env source across CI and runtime:
- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- Optional AI keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)

## Deployment Notes
- Scanner needs access to mounted project paths.
- Keep `./projects` mount behavior consistent between environments.
- Expose only required ports externally.

## Monitoring
Use monitoring service (`:9000`) plus container logs for rollout diagnostics:
```bash
docker-compose ps
docker-compose logs --tail=200 backend scanner frontend
```

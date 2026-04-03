# Launch Materials (Revised)

Last updated: 2026-04-02
Status: Draft messaging aligned with current docs

## Positioning Statement
"Self-hosted security scanning platform that orchestrates multiple open-source tools in one workflow."

## Messaging Guardrails
Use only claims that are aligned with current documentation:
- Frontend default port is `3009`.
- Baseline profile: 15 integrated tools.
- Additional tools are roadmap or stabilization-stage unless explicitly validated.
- AI analysis is feature-flag dependent.

## Suggested Launch Copy
### Short
"Run multi-engine security scans locally with one dashboard, one API, and one findings model."

### Medium
"eidosSec combines SAST, SCA, secrets, DAST, and IaC checks into a single self-hosted stack (FastAPI + React + Celery). Start with the baseline profile and expand through all-in-one roadmap integrations."

## Quick Start Snippet
```bash
git clone <repo>
cd eidosSec
docker-compose up -d --build
# Frontend: http://localhost:3009
# API docs: http://localhost:8000/docs
```

## FAQ-safe Answers
### Is this SonarQube replacement?
"It overlaps on static analysis but focuses on broader multi-engine security orchestration in one stack."

### Does code leave my environment?
"By default the stack is self-hosted. You control deployment and data residency."

### What is available today vs roadmap?
"Baseline profile is documented in `docs/tools.md`; roadmap integration is documented in `docs/INTEGRATED_APP_PLAN.md`."

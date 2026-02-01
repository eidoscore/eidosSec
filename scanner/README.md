# Scanner Worker

**Purpose:** Executes security tools and reports results back to the backend.

## Current Status

This is a **skeleton implementation** for Month 1 Week 1-2 infrastructure setup.

Full scanner implementation with 50+ tools will be completed in:
- **Month 1 Week 3-4:** First 5 tools (Semgrep, Bandit, TruffleHog, Gitleaks, Trivy)
- **Month 2:** Additional 10 tools for FREE tier (total 15 tools)
- **Month 5:** 35 more tools for PRO tier (total 50+ tools)

## Architecture

```
Scanner Worker
├── Tool Wrappers (one per security tool)
│   ├── Semgrep
│   ├── Bandit
│   ├── TruffleHog
│   └── ...
├── Orchestrator (sequential/parallel execution)
├── Deduplication Engine
└── Results Publisher (Redis pub/sub)
```

## Future Tool Categories

1. **SAST (15 tools):** Semgrep, CodeQL, Bandit, Brakeman, ESLint, PHPStan...
2. **DAST (7 tools):** OWASP ZAP, Nuclei, Wapiti, Nikto...
3. **SCA (8 tools):** Trivy, Grype, npm audit, pip-audit...
4. **Secrets (5 tools):** TruffleHog, Gitleaks, detect-secrets...
5. **Container (3 tools):** Trivy, Dockle, Hadolint
6. **IaC (4 tools):** Checkov, Terrascan, tfsec, Kics
7. **API Security (3 tools):** Nuclei API, FFUF, Postman Newman

## Current Docker Image

For Week 1-2, the Docker image is a minimal Ubuntu + Python setup.

Full tool installation happens in Week 3-4.

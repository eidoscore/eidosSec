# eidosSec Scanner

AI-powered security scanner with 50+ tools (currently: 5 tools for FREE tier).

## Current Tools (Week 3-4)

1. **Semgrep** - Multi-language SAST
2. **Bandit** - Python security linter  
3. **TruffleHog** - Secrets detection
4. **Gitleaks** - Git secrets scanner
5. **Trivy** - Dependency vulnerability scanner (SCA)

## Architecture

```
Scanner Worker (Celery)
├── Orchestrator - Manages tool execution
├── Tool Wrappers - Execute and parse tool outputs
├── Detectors - Detect languages/frameworks
└── Redis Pub/Sub - Real-time progress updates
```

## Usage

### Via Docker Compose

```bash
# Start scanner worker
docker-compose up -d scanner

# Check worker logs
docker-compose logs -f scanner
```

### Run Tests

```bash
cd scanner
pytest tests/ -v --cov=app
```

### Trigger Scan (from Python)

```python
from app.tasks import scan_project

# Async scan
result = scan_project.delay("/path/to/project", "scan-uuid")

# Get result
findings = result.get(timeout=300)
```

## Adding New Tools (Future)

1. Create wrapper in `app/tools/{tool_name}.py`
2. Inherit from `ToolWrapper`  
3. Implement `name`, `command`, `parse_output()`
4. Add to `ScanOrchestrator.all_tools`
5. Update Dockerfile with tool installation

## Tool Categories

- **SAST** (Static Analysis): Semgrep, Bandit
- **Secrets**: TruffleHog, Gitleaks
- **SCA** (Dependencies): Trivy
- **DAST** (Coming in Month 2+)
- **Container Security** (Coming in Month 5+)
- **IaC Security** (Coming in Month 5+)

## Configuration

Environment variables:
- `REDIS_URL` - Redis connection (default: redis://redis:6379/0)
- `DATABASE_URL` - PostgreSQL connection
- `LOG_LEVEL` - Logging level (default: INFO)

## Development

Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

Run tests:
```bash
pytest tests/ -v
```

Run worker locally:
```bash
celery -A worker worker --loglevel=info
```

## Next Steps (Month 2)

Adding 10 more tools for FREE tier:
- ESLint, PHPStan, Brakeman (SAST)
- Safety, npm audit, Composer audit (SCA)
- OWASP ZAP, Nuclei (DAST)
- cfn-nag, Checkov (IaC)

**Total after Month 2: 15 tools**

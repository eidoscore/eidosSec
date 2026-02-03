# 🛠️ AI Agent Testing Policy: Server-Side Enforcement

**CRITICAL INSTRUCTION**: All functional, integration, and performance testing **MUST** be performed on the remote server, **NOT** in the local environment.

## 🚩 Rationale
- Local Docker environment is unstable/not functional for full stack scans.
- The remote server (43.245.249.18) hosts a dedicated self-hosted GitHub Actions runner.
- Month 5+ tools and AI services are configured and optimized for the server infrastructure.

## 🚀 How to Execute Tests (AI Agent Workflow)

### 1. Code Changes
- Complete your code edits in the local workspace.
- Verify imports locally using `scanner/debug_imports.py` if possible.

### 2. Push to Trigger
- **ALWAYS** commit and push your changes to the `main` or `develop` branch.
- This triggers the `.github/workflows/run-tests.yml` workflow on the remote server.

```bash
git add .
git commit -m "feat: your change - triggering server tests"
git push origin main
```

### 3. Verify on Server
- Check the status of the GitHub Action.
- If you have access to the server via terminal commands, you can also trigger tests directly using the `run-tests.yml` logic (Docker Compose).

### 4. Specialized Tests
For Month 5+ features, ensure you run:
- **Performance**: `backend/tests/performance_load.py`
- **Stress**: `scanner/tests/stress_concurrency.py`
- **Memory**: `scanner/tests/memory_profile.py`

## 📋 Test Category Checklist
When reporting completion, ensure you have verified:
1. **Functional**: All tool wrappers work on the server.
2. **Security**: Self-scan has been executed.
3. **Integration**: Backend can talk to the Scanner on the server network.

---
**Note**: If you encounter local Docker errors, ignore them and proceed to server-side verification.

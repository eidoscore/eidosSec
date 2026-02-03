---
description: how to perform comprehensive testing on the remote server
---
# Server-Side Testing Workflow

This workflow ensures that code changes are verified on the production-grade runner at **43.245.249.18**.

1. **Commit and Push**: Ensure all changes are committed and pushed to the repository.
   ```bash
   git add .
   git commit -m "Your descriptive message"
   git push origin <your-branch>
   ```

2. **Wait for GitHub Action**: The push triggers the `run-tests.yml` workflow.

3. **Check Results**: View the GitHub Actions logs or run the following if the `gh` CLI is available:
   ```bash
   gh run list --workflow run-tests.yml
   ```

4. **Detailed Reports**: If you need to see specialized metrics, check the server logs for:
   - `python backend/tests/performance_load.py`
   - `python scanner/tests/stress_concurrency.py`
   - `python scanner/tests/memory_profile.py`

**IMPORTANT**: Never try to run the full `docker compose` stack locally as it will fail or provide inconsistent results compared to the server environment.

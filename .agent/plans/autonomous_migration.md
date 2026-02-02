# Plan: Autonomous Self-Healing Stack Transformation

## Goal
Transition the infrastructure to a fully autonomous, self-healing system where a "Monitoring Agent" (running in a sidecar container) can monitor, inspect logs, and restart other services (Backend, Scanner, Frontend) without requiring direct SSH access.

## Current State
- **Backend**: Failing due to schema issues (fix pushed, pending deployment).
- **Monitoring**: Simple status API, no control capabilities yet (code updated locally, but CI trigger missing).
- **CI/CD**: `deploy-full-stack` workflow is active but missing the `monitoring/**` path trigger.
- **User Request**: "Stop all existing containers" to ensure a clean slate for the new autonomous system.

## Action Plan

### Phase 1: Enable Monitoring Deployment
The CI/CD pipeline needs to recognize changes to the monitoring service to deploy the new "Autonomous Agent".
1.  **Update `deploy-full-stack.yml`**: Add `monitoring/**` to the trigger paths.
2.  **Ensure Docker Socket Access**: Verify `docker-compose.yml` mounts `/var/run/docker.sock` (Done in previous step).

### Phase 2: The "Clean Slate" Reset
To fulfill the user's request to "turn off all existing containers" remotely:
1.  We will use the next deployment to enforce a recreation of containers.
2.  We will modify the `deploy-full-stack.yml` to explicitly run `docker-compose down` before `up` this one time (or permanently) to ensure no zombie containers remain.

### Phase 3: Autonomous Repair Validation
Once the new stack is deployed:
1.  **Verify Health**: Poll `GET /api/status`.
2.  **Test Logs**: Request `GET /api/logs/backend` to verify we can read logs.
3.  **Test Action**: If the backend is failing (restart loop), use `POST /api/action/restart/backend` to attempt recovery.

## Technical Tasks

1.  [ ] **Update CI/CD**: Modify `.github/workflows/deploy-full-stack.yml` to trigger on `monitoring/**` and perform a clean reset (`docker-compose down`).
2.  [ ] **Push Changes**: Trigger the deployment.
3.  [ ] **Monitor Transition**: Watch the build status via the existing (old) monitoring until the new one takes over.
4.  [ ] **Autonomous Check**: Use the new API endpoints to verify the stack state.

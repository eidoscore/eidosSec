# Month 5 Week 3: Enterprise Features (License Integration)

## Goal
Integrate eidosSec with the EidosStack License Server for centralized license management.

## Integration Plan

### 1. Configuration
- Update `backend/app/config.py`:
    - `LICENSE_SERVER_URL`: Default `http://localhost:3000` (or prod URL).
    - `INSTANCE_ID`: UUID generated on first run and stored.
    - `LICENSE_KEY`: The JWT token provided by the user.

### 2. Scanner `LicenseVerifier` (`scanner/app/services/license.py`)
- **Mode:** Online Verification.
- **Protocol:** POST `/api/v1/license/verify`
- **Payload:**
    ```json
    {
        "token": "...",
        "instance_id": "...",
        "app_version": "..."
    }
    ```
- **Response:**
    - verify validity (`valid: true`).
    - get rolling token (`token: "..."`).
    - extract plan/features from response or decoded token (if we trust the server response more than the token content for features).
    - **Caching:** Cache the result for e.g. 1 hour to reduce network spam.

### 3. Cleanup
- Remove the local RSA key generation scripts (`scripts/generate_keys.py`, `scripts/issue_license.py`) as they belong to the License Server repo, not the Client.

## Verification
- Mock the License Server response in tests.
- Point to a running local instance of `eidosstack-license-server` if possible, or use a mock server.

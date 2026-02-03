# Month 5 Week 3: Backend RBAC Implementation Plan

## Goal
Implement Role-Based Access Control (RBAC) to secure the eidosSec Backend.

## 1. Database Schema
- **New Model:** `User`
    - `id`: UUID (PK)
    - `email`: String (Unique, Index)
    - `hashed_password`: String
    - `role`: String (Enum: `admin`, `user`, `viewer`)
    - `is_active`: Boolean
    - `created_at`: Timestamp
- **Migration:** Alembic migration to create `users` table.

## 2. Authentication Framework
- **Service:** `AuthService` (`backend/app/services/auth.py`)
    - `get_password_hash`, `verify_password` (Passlib)
    - `create_access_token` (JWT)
    - `get_current_user` (FastAPI Dependency)
    - `get_current_active_user`
    - `check_permissions(roles=[...])` (Dependency factory)

## 3. API Endpoints
- **New Router:** `backend/app/api/v1/auth.py`
    - `POST /login`: OAuth2PasswordRequestForm -> JWT
    - `POST /setup`: Create initial admin (only works if no users exist)
    - `GET /me`: Get current user info
- **Router Security:**
    - Apply `Depends(get_current_user)` to sensitive routes in `projects.py`, `scans.py`.

## 4. Default Seed
- On startup, check if users table is empty. If so, log a warning or creating a default `admin@eidos.sec` / `changethis` (optional, maybe better via `/setup` endpoint).

## Verification
- Test creating a user.
- Test login flow.
- Test permission denial.

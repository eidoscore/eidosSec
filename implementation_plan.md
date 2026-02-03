# Implementation Plan - Month 5 Prep: Schema & Tools

## Goal Description
Address immediate technical debt identified in the Month 4 handover to prepare for the "Big Bang" tool integration in Month 5.
1.  **Schema Alignment:** Resolve the divergence between Scanner's `metadata` field and Backend's `finding_metadata` field.
2.  **Tool Binaries:** Create a robust strategy for installing 60+ tool binaries without hitting rate limits or creating a massive Docker build context.

## User Review Required
> [!IMPORTANT]
> **Schema Change**: We will standardize on `metadata` for both Scanner and Backend. This requires a database migration for the Backend to rename `finding_metadata` to `metadata` (or alias it).
> **Docker Strategy**: We will create a `binaries` stage in the Dockerfile that can be cached, or potentially a separate base image if the size becomes too large.

## Proposed Changes

### Backend Service (`app/`)
#### [MODIFY] [models.py](file:///d:/Project/eidosSec/backend/app/models.py)
- Rename `finding_metadata` to `metadata` in `Finding` model.
- Ensure SQLModel/SQLAlchemy handles the column rename.
#### [MODIFY] [schemas.py](file:///d:/Project/eidosSec/backend/app/schemas.py)
- Update Pydantic schemas to use `metadata` field.
#### [NEW] [migration_script.py](file:///d:/Project/eidosSec/backend/alembic/versions/xxxx_rename_metadata.py)
- Alembic migration to rename column `finding_metadata` to `metadata`.

### Scanner Service (`scanner/`)
#### [MODIFY] [orchestrator.py](file:///d:/Project/eidosSec/scanner/app/orchestrator.py)
- Ensure `metadata` is populated correctly (already seems to be).
#### [MODIFY] [Dockerfile](file:///d:/Project/eidosSec/scanner/Dockerfile)
- Implement multi-stage build pattern specifically for tools.
- Create a `downloader` stage that fetches all binaries.
- Copy binaries to the final runtime image.

## Verification Plan

### Automated Tests
- Run backend tests to ensure `metadata` field is correctly stored and retrieved.
- Run `scanner/debug_imports.py` to verify tool binaries are present.
- Build Docker image to verify size and build time.

### Manual Verification
- Trigger a scan with `metadata` populated (e.g., from `SarifParser` results) and verify it appears in the Backend API response.

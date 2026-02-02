# Usage Guide

## Creating a Project

1.  Go to the **Dashboard** at `http://localhost:3000`.
2.  Click **New Project**.
3.  Enter the **Subject** (Absolute path to the source code you want to scan on your local machine).
    *   *Note: In Docker mode, you need to mount the volume or use a relative path mapped in docker-compose.*
4.  The system will detect languages and frameworks (simulated for now).
5.  Confirm to create the project.

## Running a Scan

1.  Navigate to the **Project Details** page.
2.  Click **Start Scan**.
3.  You will be redirected to the **Scan Details** page.
4.  Watch the progress bar and real-time logs as tools are executed.

## Viewing Results

1.  Once the scan completes, findings will appear in the table.
2.  Click on a finding row to view details.
    -   **Severity**: Critical, High, Medium, Low, Info.
    -   **Code Snippet**: See the exact line of code.
    -   **AI Analysis**: Read the explanation and remediation advice.
3.  **Export**: Click "Export JSON" to download the raw data.

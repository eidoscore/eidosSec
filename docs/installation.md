# Installation Guide

## Prerequisites

-   Time travel capability (just kidding, but you need modern tools)
-   **Docker** & **Docker Compose**
-   **Node.js 18+** (for local frontend dev)
-   **Python 3.10+** (for local backend dev)

## Quick Start (Docker)

The easiest way to run eidosSec is using Docker Compose.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/eidosSec.git
    cd eidosSec
    ```

2.  **Start services:**
    ```bash
    docker-compose up -d --build
    ```

3.  **Access the application:**
    -   Frontend: http://localhost:3000
    -   Backend API: http://localhost:8000/docs

## Local Development Setup

### Backend

1.  Navigate to backend: `cd backend`
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run server:
    ```bash
    uvicorn app.main:app --reload
    ```

### Frontend

1.  Navigate to frontend: `cd frontend`
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run dev server:
    ```bash
    npm run dev
    ```

### Scanner Worker

1.  Navigate to scanner: `cd scanner`
2.  Start Celery worker:
    ```bash
    celery -A app.celery_app worker --loglevel=info
    ```

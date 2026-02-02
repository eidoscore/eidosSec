# Introduction to eidosSec

eidosSec is an AI-powered security scanner designed to help developers find and fix vulnerabilities in their codebases. It combines traditional static analysis tools with LLM-based verification to reduce false positives and provide actionable remediation advice.

## Key Features

-   **Multi-Language Support**: Scans Python, JavaScript, Java, Go, and more.
-   **AI Verification**: Uses LLMs to analyze findings and filter out noise.
-   **Real-time Progress**: Watch scans happen live via WebSocket updates.
-   **Detailed Reporting**: Get comprehensive reports with code snippets, CWEs, and fix suggestions.
-   **Self-Hosted**: Run it locally or on your private infrastructure.

## Architecture

eidosSec consists of three main components:

1.  **Frontend**: A React-based web dashboard for managing projects and viewing results.
2.  **Backend**: A FastAPI server that handles data management and API requests.
3.  **Scanner**: A Celery-based worker that orchestrates security tools and performs analysis.

## Getting Started

Check out the [Installation Guide](./installation.md) to get set up.

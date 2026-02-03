# eidosSec 🛡️

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![React](https://img.shields.io/badge/React-18-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)

**Secure your code at the speed of thought.**

eidosSec is an AI-powered security scanner that combines traditional static analysis with Large Language Models to provide accurate, actionable vulnerability findings. It runs 100% locally using Docker—your code never leaves your machine.

![Dashboard Preview](docs/images/dashboard-preview.png)

## 📚 Documentation

-   [**Installation Guide**](./docs/installation.md) - Windows (WSL2), Linux, and macOS setup.
-   [**Supported Tools**](./docs/tools.md) - List of all 15+ integrated security scanners (Semgrep, Bandit, Trivy, etc.).
-   [**API Reference**](./docs/api.md) - REST API documentation and usage examples.
-   [**Project Roadmap**](./milestone_development.md) - Development timeline and future features.

## ✨ Features

-   **Multi-Engine Scanning**: Orchestrates 15+ open-source security tools for comprehensive coverage (SAST, SCA, Secrets, IaC).
-   **Intelligent Deduplication**: Merges duplicate findings from multiple tools to reduce noise.
-   **Real-time Progress**: Watch scans execute live via WebSocket streams.
-   **Private & Secure**: Self-hosted architecture ensures no code exfiltration.
-   **(Coming Soon) AI verification**: Use LLMs to explain and verify complex findings.

## 🚀 Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/eidosSec.git
    cd eidosSec
    ```

2.  **Start with Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```

3.  **Access the Dashboard:**
    Open [**http://localhost:3000**](http://localhost:3000) in your browser.

## 🛠️ Development Structure

eidosSec is a monorepo consisting of:

-   `backend/`: FastAPI application (Python)
-   `frontend/`: React + Vite application (TypeScript/Tailwind)
-   `scanner/`: Celery worker & tool wrappers (Python)

See [Installation Guide](./docs/installation.md#local-development-setup) for local development instructions.

## 🤝 Contributing

Contributions are welcome! Please check the [Project Roadmap](./milestone_development.md) to see what we're working on.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

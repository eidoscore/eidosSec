# eidosSec 🛡️

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![React](https://img.shields.io/badge/React-18-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)

**Secure your code at the speed of thought.**

eidosSec is an AI-powered security scanner that combines traditional static analysis with Large Language Models to provide accurate, actionable vulnerability findings.

![Dashboard Preview](docs/images/dashboard-preview.png)

## ✨ Features

-   **Multi-Engine Scanning**: Orchestrates multiple open-source security tools (Brakeman, Bandit, Gosec, etc.).
-   **AI Verification**: Uses LLMs to analyze findings, reducing false positives and explaining complex issues.
-   **Real-time Progress**: Watch scans execute live via WebSocket streams.
-   **Remediation Advice**: Get code-specific fix suggestions.
-   **Exportable Reports**: Download findings in JSON format.
-   **Self-Hosted**: Full control over your code and data.

## 🚀 Quick Start

The fastest way to get started is using Docker Compose.

```bash
git clone https://github.com/your-org/eidosSec.git
cd eidosSec
docker-compose up -d --build
```

Access the dashboard at **http://localhost:3000**.

## 🛠️ Development

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentation

See the [Documentation](./docs/intro.md) folder for detailed guides.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

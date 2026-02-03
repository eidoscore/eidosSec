# Installation Guide

eidosSec generates a complete, self-hosted security environment using Docker.

## System Requirements

-   **Docker Engine** (20.10+)
-   **Docker Compose** (2.0+)
-   **RAM:** 4GB minimum (8GB recommended for scans)
-   **Disk Space:** ~3GB for Docker images

---

## 🖥️ Windows

We strongly recommend using **WSL 2** (Windows Subsystem for Linux) for the best performance and compatibility.

1.  **Install Docker Desktop**: Download from [docker.com](https://www.docker.com/products/docker-desktop/) and ensure the "Use WSL 2 based engine" option is checked in Settings > General.
2.  **Open your terminal** (PowerShell or WSL terminal).
3.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/eidosSec.git
    cd eidosSec
    ```
    *Tip: Recommend cloning into your WSL filesystem (e.g., `\\wsl$\Ubuntu\home\yourname\`) rather than `/mnt/c/` for IO speed.*

4.  **Start the stack**:
    ```bash
    docker-compose up -d --build
    ```
5.  **Access the Dashboard**: Open your browser to `http://localhost:3000`.

---

## 🐧 Linux (Ubuntu/Debian)

1.  **Install Docker & Compose**:
    ```bash
    # Remove old versions
    sudo apt-get remove docker docker.io containerd runc

    # Install using convenience script (or follow official docs)
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh

    # Add user to docker group (avoid sudo)
    sudo usermod -aG docker $USER
    # Log out and back in for this to take effect!
    ```

2.  **Clone and run**:
    ```bash
    git clone https://github.com/your-org/eidosSec.git
    cd eidosSec
    docker-compose up -d --build
    ```

---

## 🍎 macOS

Works on both Intel and Apple Silicon (M1/M2/M3) chips.

1.  **Install Docker Desktop for Mac**: Download from [docker.com](https://www.docker.com/products/docker-desktop/).
2.  **Clone and run**:
    ```bash
    git clone https://github.com/your-org/eidosSec.git
    cd eidosSec
    docker-compose up -d --build
    ```

---

## 🛠️ Verification

After running `docker-compose up`, verify everything is working:

1.  **Check Containers**:
    ```bash
    docker-compose ps
    ```
    You should see `frontend`, `backend`, `scanner_worker`, `postgres`, and `redis` all in `Up` state.

2.  **Health Check**:
    -   Frontend: [http://localhost:3000](http://localhost:3000)
    -   Backend Health: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## 🐛 Troubleshooting

**"Bind for 0.0.0.0:8000 failed"**
> Port 8000 is likely in use. Edit `.env` or `docker-compose.yml` to change the backend port to something else (e.g., 8001).

**"Scanner exited with code 137"**
> Out of memory. Increase Docker memory limit in Docker Desktop settings to at least 4GB.

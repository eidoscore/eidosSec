# CI/CD Setup - Deploy ke Server

Setup untuk build Docker image di server (bukan lokal) dengan monitoring untuk AI agent.

---

## 🎯 Arsitektur

```
[Developer Push] → [GitHub] → [Self-Hosted Runner di Server]
                                        ↓
                              [Docker Build + Deploy]
                                        ↓
                              [Monitoring API] ← [AI Agent Checks]
```

---

## 📋 Prerequisites

**Di Server Kamu:**
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Docker & Docker Compose installed
- Port 9000 accessible (untuk monitoring API)
- Minimal 4GB RAM (untuk build Docker images)

---

## 🚀 Setup Instructions

### Step 1: Install GitHub Runner

**Di server kamu, jalankan:**

```bash
# Download setup script
curl -o setup-runner.sh https://raw.githubusercontent.com/eidoscore/eidosSec/main/scripts/setup-runner.sh

# Make executable
chmod +x setup-runner.sh

# Run (requires sudo)
sudo ./setup-runner.sh
```

**Kemudian configure runner:**

1. Go to: https://github.com/eidoscore/eidosSec/settings/actions/runners/new
2. Copy registration token
3. Run di server:

```bash
sudo su - runner
cd actions-runner
./config.sh --url https://github.com/eidoscore/eidosSec --token YOUR_TOKEN
```

4. Install as service:

```bash
sudo ./svc.sh install runner
sudo ./svc.sh start
```

---

### Step 2: Setup Monitoring API

**Di server yang sama:**

```bash
# Clone repo (if not already)
git clone https://github.com/eidoscore/eidosSec.git
cd eidosSec

# Run monitoring setup
chmod +x scripts/setup-monitoring.sh
./scripts/setup-monitoring.sh
```

Monitoring API akan jalan di `http://localhost:9000`

---

### Step 3: Test Deployment

**Push code ke GitHub:**

```bash
git add .
git commit -m "test: trigger CI/CD"
git push origin main
```

**Pantau build:**

1. **Via GitHub Actions UI:**
   https://github.com/eidoscore/eidosSec/actions

2. **Via Monitoring API:**
   ```bash
   curl http://YOUR_SERVER:9000/api/status
   ```

3. **Via gh CLI (recommended for AI agents):**
   ```bash
   gh api repos/eidoscore/eidosSec/actions/runs | jq '.workflow_runs[0]'
   ```

---

## 🤖 AI Agent Monitoring

### Polling Build Status

**Via Monitoring API:**
```python
import requests
import time

def check_build_status(server_url):
    while True:
        response = requests.get(f"{server_url}/api/status")
        data = response.json()
        
        build = data.get('current_build')
        if build:
            print(f"Status: {build['status']}")
            print(f"Component: {build['component']}")
            
            if build['status'] != 'building':
                break
        
        time.sleep(30)  # Check every 30 seconds

# Usage
check_build_status("http://YOUR_SERVER:9000")
```

**Via GitHub API:**
```python
import subprocess
import json

def get_latest_run():
    result = subprocess.run(
        ['gh', 'api', 'repos/eidoscore/eidosSec/actions/runs'],
        capture_output=True,
        text=True
    )
    
    data = json.loads(result.stdout)
    latest = data['workflow_runs'][0]
    
    return {
        'status': latest['status'],
        'conclusion': latest['conclusion'],
        'url': latest['html_url']
    }
```

---

## 📊 Monitoring Endpoints

### GET /api/status
Current build dan deployment status

**Response:**
```json
{
  "current_build": {
    "build_id": "abc123",
    "status": "building",
    "component": "scanner",
    "started_at": "2026-02-02T03:45:00Z",
    "branch": "main"
  },
  "current_deployment": null,
  "timestamp": "2026-02-02T03:50:00Z"
}
```

### GET /api/builds
List recent builds

### GET /api/builds/{build_id}
Specific build details

---

## 🔧 Workflows Available

### 1. Deploy Scanner (`deploy-scanner.yml`)
Triggered when:
- Push to `main` with changes in `scanner/`
- Manual workflow dispatch

Actions:
- Build scanner Docker image
- Tag with timestamp
- Report status to monitoring API

### 2. Deploy Full Stack (`deploy-full-stack.yml`)
Triggered when:
- Push to `main` with changes in any service
- Manual workflow dispatch

Actions:
- Build all services (backend, frontend, scanner)
- Run database migrations
- Start services with docker-compose
- Health check all services

---

## 🛠️ Troubleshooting

### Runner not picking up jobs

1. Check runner status:
   ```bash
   sudo ./svc.sh status
   ```

2. Check runner logs:
   ```bash
   sudo journalctl -u actions.runner.eidoscore-eidosSec.*
   ```

3. Restart runner:
   ```bash
   sudo ./svc.sh stop
   sudo ./svc.sh start
   ```

### Monitoring API not responding

1. Check container:
   ```bash
   docker ps | grep cicd-monitor
   ```

2. Check logs:
   ```bash
   docker logs eidossec-cicd-monitor
   ```

3. Restart:
   ```bash
   cd monitoring
   docker-compose -f docker-compose.monitor.yml restart
   ```

### Build failing

1. Check Docker space:
   ```bash
   docker system df
   ```

2. Clean up:
   ```bash
   docker system prune -af --volumes
   ```

---

## 📈 Tips

**Optimize Build Time:**
- Use Docker layer caching
- Pre-pull base images
- Add more RAM to server

**Monitor Resource Usage:**
```bash
# Watch Docker stats
docker stats

# Check disk space
df -h

# Monitor RAM
free -h
```

**AI Agent Best Practices:**
- Poll monitoring API every 30s (not more frequent)
- Cache GitHub token for gh CLI
- Log build results for history

---

## 🎉 Success!

Setelah setup selesai:
- ✅ Push code auto-trigger build di server
- ✅ AI agent bisa pantau via monitoring API
- ✅ Build artifacts tersimpan di server
- ✅ Internet lemot di lokal tidak masalah

**Next:** AI agent lain (Windsurf) juga bisa pantau progress yang sama!

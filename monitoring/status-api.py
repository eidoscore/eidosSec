"""
CI/CD Status Monitoring API
Provides build and deployment status for AI agent monitoring
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import os
import docker
import subprocess

app = FastAPI(title="eidosSec CI/CD Monitor", version="1.0.0")

# CORS for AI agents to access from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple file-based storage (can upgrade to Redis later)
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)

class BuildStatus(BaseModel):
    build_id: str
    status: str  # building, success, failed
    component: str  # scanner, backend, frontend
    started_at: str
    completed_at: Optional[str] = None
    branch: str
    commit_message: Optional[str] = None
    image_size: Optional[str] = None
    error: Optional[str] = None

class DeploymentStatus(BaseModel):
    deployment_id: str
    status: str  # deploying, success, failed
    started_at: str
    completed_at: Optional[str] = None
    branch: str
    services: Optional[List[str]] = None

@app.get("/")
def root():
    return {
        "service": "eidosSec CI/CD Monitor",
        "version": "1.0.0",
        "endpoints": {
            "builds": "/api/builds",
            "deployments": "/api/deployments",
            "status": "/api/status"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/builds")
def create_build(build: BuildStatus):
    """Record new build start"""
    file_path = f"{DATA_DIR}/build_{build.build_id}.json"
    with open(file_path, 'w') as f:
        json.dump(build.dict(), f, indent=2)
    return {"message": "Build recorded", "build_id": build.build_id}

@app.patch("/api/builds/{build_id}")
def update_build(build_id: str, update: dict):
    """Update build status"""
    file_path = f"{DATA_DIR}/build_{build_id}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Build not found")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    data.update(update)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return {"message": "Build updated", "build_id": build_id}

@app.get("/api/builds/{build_id}")
def get_build(build_id: str):
    """Get specific build status"""
    file_path = f"{DATA_DIR}/build_{build_id}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Build not found")
    
    with open(file_path, 'r') as f:
        return json.load(f)

@app.get("/api/builds")
def list_builds(limit: int = 10):
    """List recent builds"""
    builds = []
    for filename in sorted(os.listdir(DATA_DIR), reverse=True):
        if filename.startswith("build_"):
            with open(f"{DATA_DIR}/{filename}", 'r') as f:
                builds.append(json.load(f))
        if len(builds) >= limit:
            break
    return builds

@app.post("/api/deployments")
def create_deployment(deployment: DeploymentStatus):
    """Record new deployment start"""
    file_path = f"{DATA_DIR}/deploy_{deployment.deployment_id}.json"
    with open(file_path, 'w') as f:
        json.dump(deployment.dict(), f, indent=2)
    return {"message": "Deployment recorded", "deployment_id": deployment.deployment_id}

@app.patch("/api/deployments/{deployment_id}")
def update_deployment(deployment_id: str, update: dict):
    """Update deployment status"""
    file_path = f"{DATA_DIR}/deploy_{deployment_id}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    data.update(update)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return {"message": "Deployment updated", "deployment_id": deployment_id}

@app.get("/api/status")
def get_current_status():
    """Get current build/deployment status (latest)"""
    builds = []
    deployments = []
    
    for filename in os.listdir(DATA_DIR):
        filepath = f"{DATA_DIR}/{filename}"
        with open(filepath, 'r') as f:
            data = json.load(f)
            if filename.startswith("build_"):
                builds.append(data)
            elif filename.startswith("deploy_"):
                deployments.append(data)
    
    # Sort by started_at
    builds.sort(key=lambda x: x['started_at'], reverse=True)
    deployments.sort(key=lambda x: x['started_at'], reverse=True)
    
    return {
        "current_build": builds[0] if builds else None,
        "current_deployment": deployments[0] if deployments else None,
        "docker_connected": not isinstance(get_docker_client(), str),
        "timestamp": datetime.utcnow().isoformat()
    }


# -----------------------------------------------------------------------------
# Autonomous Management Endpoints
# -----------------------------------------------------------------------------

def get_docker_client():
    try:
        client = docker.from_env()
        client.ping() # Verify connection
        return client
    except Exception as e:
        print(f"Error connecting to Docker: {e}")
        return str(e) # Return error string instead of None to differentiate

@app.post("/api/action/restart/{service_name}")
def restart_service(service_name: str):
    """Restart a docker container by service name fragment"""
    client = get_docker_client()
    if isinstance(client, str):
        raise HTTPException(status_code=500, detail=f"Docker connection failed: {client}")
    if not client:
        raise HTTPException(status_code=500, detail="Docker unavailable")
    
    try:
        # Find container by name (e.g., 'backend' -> 'eidossec-backend')
        containers = client.containers.list(all=True)
        target = None
        for c in containers:
            if service_name in c.name:
                target = c
                break
        
        if not target:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        target.restart()
        return {"message": f"Service {target.name} restarted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ps")
def get_docker_ps():
    """List containers using shell fallback"""
    try:
        result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout}
        return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/health/docker")
def check_docker_health():
    """Verify Docker socket access"""
    client = get_docker_client()
    if isinstance(client, str):
        # Try subprocess as fallback for health check
        try:
            res = subprocess.run(["docker", "version"], capture_output=True)
            if res.returncode == 0:
                return {"status": "connected_via_shell", "info": "Shell OK, SDK Failed"}
        except:
            pass
        return {"status": "error", "error": client, "path": "/var/run/docker.sock"}
    return {"status": "connected", "containers": len(client.containers.list())}

@app.get("/api/logs/{service_name}")
def get_service_logs(service_name: str, tail: int = 100):
    """Retrieve logs for a service with shell fallback"""
    # 1. Try Shell Fallback First (often more reliable in these environments)
    try:
        # Find container name that matches service_name
        ps_res = subprocess.run(["docker", "ps", "-a", "--filter", f"name={service_name}", "--format", "{{.Names}}"], 
                              capture_output=True, text=True)
        if ps_res.returncode == 0 and ps_res.stdout.strip():
            full_name = ps_res.stdout.strip().split('\n')[0]
            log_res = subprocess.run(["docker", "logs", "--tail", str(tail), full_name], 
                                   capture_output=True, text=True)
            if log_res.returncode == 0:
                return {"service": full_name, "logs": log_res.stdout, "method": "shell"}
    except Exception as e:
        print(f"Shell log fallback failed: {e}")

    # 2. Try SDK (as second option)
    client = get_docker_client()
    if isinstance(client, str):
        raise HTTPException(status_code=500, detail=f"Docker SDK failed and shell fallback failed. SDK Error: {client}")
    
    try:
        containers = client.containers.list(all=True)
        target = None
        for c in containers:
            if service_name in c.name:
                target = c
                break
        
        if not target:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        logs = target.logs(tail=tail).decode('utf-8', errors='ignore')
        return {"service": target.name, "logs": logs, "method": "sdk"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)

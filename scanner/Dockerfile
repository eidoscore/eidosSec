# Scanner Worker - Production Build
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    curl \
    wget \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for python3.11
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# Install Gitleaks (binary)
RUN wget -q https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz && \
    tar -xzf gitleaks_8.18.1_linux_x64.tar.gz && \
    mv gitleaks /usr/local/bin/ && \
    chmod +x /usr/local/bin/gitleaks && \
    rm gitleaks_8.18.1_linux_x64.tar.gz

# Install Trivy (binary)
RUN wget -q https://github.com/aquasecurity/trivy/releases/download/v0.48.3/trivy_0.48.3_Linux-64bit.tar.gz && \
    tar -xzf trivy_0.48.3_Linux-64bit.tar.gz && \
    mv trivy /usr/local/bin/ && \
    chmod +x /usr/local/bin/trivy && \
    rm trivy_0.48.3_Linux-64bit.tar.gz

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir --user -r requirements.txt

# Verify tool installations
RUN semgrep --version && \
    bandit --version && \
    trufflehog --version && \
    gitleaks version && \
    trivy --version

# Copy scanner code
COPY . .

# Create directories
RUN mkdir -p /app/projects /app/scan-results

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import redis; r=redis.from_url('redis://redis:6379/0'); r.ping()" || exit 1

# Run Celery worker
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "--concurrency=2", "--max-tasks-per-child=10"]

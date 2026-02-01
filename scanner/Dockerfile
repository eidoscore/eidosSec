# Scanner skeleton - Week 1-2 infrastructure setup
# Full implementation in Week 3-4

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python and basic tools
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy scanner code (placeholder)
COPY . .

# Create directories
RUN mkdir -p /app/projects /app/scan-results

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python3 -c "import redis; r=redis.from_url('redis://redis:6379/0'); r.ping()" || exit 1

# Entry point (placeholder - will run Celery worker in Week 3-4)
CMD ["echo", "Scanner skeleton ready. Full implementation in Week 3-4."]

# Scanner Worker - Production Build
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Install system dependencies + language runtimes
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    curl \
    wget \
    unzip \
    ca-certificates \
    # Node.js dependencies
    gnupg2 \
    # PHP 8.2
    software-properties-common \
    # Ruby dependencies
    build-essential \
    libssl-dev \
    libreadline-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install PHP 8.2 and Composer
RUN add-apt-repository ppa:ondrej/php -y && \
    apt-get update && \
    apt-get install -y php8.2 php8.2-cli php8.2-mbstring php8.2-xml php8.2-curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Install Ruby 3.2
RUN apt-get update && \
    apt-get install -y ruby3.2 ruby3.2-dev && \
    rm -rf /var/lib/apt/lists/* && \
    gem install bundler

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

# Install TruffleHog (binary)
RUN wget -q https://github.com/trufflesecurity/trufflehog/releases/download/v3.63.2/trufflehog_3.63.2_linux_amd64.tar.gz && \
    tar -xzf trufflehog_3.63.2_linux_amd64.tar.gz && \
    mv trufflehog /usr/local/bin/ && \
    chmod +x /usr/local/bin/trufflehog && \
    rm trufflehog_3.63.2_linux_amd64.tar.gz

# Install ESLint + security plugins (SAST for JS/TS)
RUN npm install -g eslint@8.56.0 \
    @eslint/js@8.56.0 \
    eslint-plugin-security@2.1.0 \
    @typescript-eslint/parser@6.19.0 \
    @typescript-eslint/eslint-plugin@6.19.0

# Install Brakeman (SAST for Ruby/Rails)
RUN gem install brakeman -v 6.1.1

# Install PHPStan (SAST for PHP)
RUN composer global require phpstan/phpstan:^1.10 && \
    ln -s /root/.composer/vendor/bin/phpstan /usr/local/bin/phpstan

# Install cfn-nag (IaC for CloudFormation) - bonus for future
RUN gem install cfn-nag -v 0.8.10

# Set working directory
WORKDIR /app

# Set PATH to include user site-packages
ENV PATH="/root/.local/bin:${PATH}"

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir --user -r requirements.txt

# Verify tool installations will happen at runtime
# RUN semgrep --version && \
#     bandit --version && \
#     trufflehog --version && \
#     gitleaks version && \
#     trivy --version

# Copy scanner code
COPY . .

# Create directories
RUN mkdir -p /app/projects /app/scan-results

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import redis; r=redis.from_url('redis://redis:6379/0'); r.ping()" || exit 1

# Run Celery worker
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "--concurrency=2", "--max-tasks-per-child=10"]

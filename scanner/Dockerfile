# Stage 1: Tool Downloader (Parallelizable)
FROM ubuntu:22.04 as tools

RUN apt-get update && apt-get install -y wget tar unzip

WORKDIR /tmp
COPY scripts/download_tools.sh .
RUN chmod +x download_tools.sh && ./download_tools.sh

# Stage 2: Production Runtime
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Install Runtimes (Python, Node, PHP, Ruby)
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    curl wget ca-certificates gnupg2 \
    software-properties-common \
    ruby-full ruby-dev \
    build-essential libssl-dev libreadline-dev zlib1g-dev \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install PHP 8.2 & Composer
RUN add-apt-repository ppa:ondrej/php -y && \
    apt-get update && \
    apt-get install -y php8.2 php8.2-cli php8.2-mbstring php8.2-xml php8.2-curl && \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && \
    rm -rf /var/lib/apt/lists/*

# Install Ruby Gems
RUN gem install bundler brakeman:6.1.1 cfn-nag:0.8.10

# Symlink Python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# Copy Binaries from Stage 1
# Copy Binaries from Stage 1
COPY --from=tools /usr/local/bin/gitleaks /usr/local/bin/
COPY --from=tools /usr/local/bin/trivy /usr/local/bin/
COPY --from=tools /usr/local/bin/trufflehog /usr/local/bin/
COPY --from=tools /usr/local/bin/nuclei /usr/local/bin/
COPY --from=tools /usr/local/bin/gosec /usr/local/bin/
COPY --from=tools /usr/local/bin/staticcheck /usr/local/bin/
COPY --from=tools /usr/local/bin/codeql-home /usr/local/bin/codeql-home
COPY --from=tools /usr/local/bin/spotbugs-home /usr/local/bin/spotbugs-home
COPY --from=tools /usr/local/bin/pmd-home /usr/local/bin/pmd-home
COPY --from=tools /usr/local/bin/shellcheck /usr/local/bin/
COPY --from=tools /usr/local/bin/kics-home /usr/local/bin/kics-home
COPY --from=tools /usr/local/bin/zap-baseline.py /usr/local/bin/
COPY --from=tools /usr/local/bin/zap_common.py /usr/local/bin/

RUN ln -s /usr/local/bin/codeql-home/codeql /usr/local/bin/codeql && \
    ln -s /usr/local/bin/spotbugs-home/bin/spotbugs /usr/local/bin/spotbugs && \
    ln -s /usr/local/bin/pmd-home/bin/pmd /usr/local/bin/pmd && \
    ln -s /usr/local/bin/kics-home/kics /usr/local/bin/kics && \
    chmod +x /usr/local/bin/gitleaks /usr/local/bin/trivy /usr/local/bin/trufflehog /usr/local/bin/nuclei /usr/local/bin/gosec /usr/local/bin/codeql /usr/local/bin/staticcheck /usr/local/bin/spotbugs /usr/local/bin/pmd /usr/local/bin/shellcheck /usr/local/bin/kics /usr/local/bin/zap-baseline.py

# Install Global NPM Packages (ESLint, Retire.js)
RUN npm install -g eslint@8.56.0 \
    @eslint/js@8.56.0 \
    eslint-plugin-security@2.1.0 \
    @typescript-eslint/parser@6.19.0 \
    @typescript-eslint/eslint-plugin@6.19.0 \
    retire@4.4.2

# Install PHPStan
RUN composer global require phpstan/phpstan:^1.10 && \
    ln -s /root/.composer/vendor/bin/phpstan /usr/local/bin/phpstan

# Python Tools Setup
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir pipx && \
    python3 -m pipx ensurepath && \
    # Install Safety via pipx (saves conflict)
    pipx install safety==3.0.1 && \
    # Install App Deps
    pip3 install --no-cache-dir --user -r requirements.txt

# Copy App Code
COPY . .

# Create Directories
RUN mkdir -p /app/projects /app/scan-results

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import redis; r=redis.from_url('redis://redis:6379/0'); r.ping()" || exit 1

CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "--concurrency=2", "--max-tasks-per-child=10"]

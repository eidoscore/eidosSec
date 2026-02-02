#!/bin/bash
set -e

echo "🚀 eidosSec - Production Server Setup (Autonomous Ready)"
echo "========================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root or with sudo"
    exit 1
fi

# 1. Install Docker & Dependencies using official script (More reliable)
echo "📦 Installing Docker & Dependencies..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Ensure git and other tools are present
apt-get update && apt-get install -y git jq curl

# 2. Create runner user
echo "👤 Creating runner user..."
if ! id "runner" &>/dev/null; then
    useradd -m -s /bin/bash runner
    usermod -aG docker runner
    echo "✅ User 'runner' created and added to 'docker' group"
fi

# 3. Prepare Project Directory
echo "📂 Preparing project directory..."
mkdir -p /opt/eidosSec
chown runner:runner /opt/eidosSec
chmod 775 /opt/eidosSec

# 4. Install GitHub Actions Runner
echo "📥 Setting up GitHub Actions Runner..."
RUNNER_VERSION="2.314.1"
RUNNER_DIR="/home/runner/actions-runner"

# Create directory as runner user
sudo -u runner mkdir -p "$RUNNER_DIR"

if [ ! -f "$RUNNER_DIR/config.sh" ]; then
    cd "$RUNNER_DIR"
    
    echo "   Downloading runner v$RUNNER_VERSION..."
    sudo -u runner curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
        -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
    
    sudo -u runner tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
    rm actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
    echo "✅ Runner binaries installed at $RUNNER_DIR"
else
    echo "✅ Runner already installed at $RUNNER_DIR"
fi

echo ""
echo "🎉 Server is ready! Now register the runner:"
echo "==========================================="
echo "1. Go to: https://github.com/eidoscore/eidosSec/settings/actions/runners/new"
echo "2. Copy the token (e.g., A1B2C3D4...)"
echo "3. Run these commands:"
echo ""
echo "   sudo su - runner"
echo "   cd actions-runner"
echo "   ./config.sh --url https://github.com/eidoscore/eidosSec --token YOUR_TOKEN --name eidos-autonomus-01 --labels self-hosted,linux,x64"
echo "   sudo ./svc.sh install"
echo "   sudo ./svc.sh start"
echo ""
echo "==========================================="

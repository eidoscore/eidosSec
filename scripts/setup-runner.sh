#!/bin/bash
set -e

echo "🚀 eidosSec - GitHub Self-Hosted Runner Setup"
echo "=============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root or with sudo"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "❌ Cannot detect OS"
    exit 1
fi

echo "📋 Detected OS: $OS $VERSION"

# Install dependencies
echo "📦 Installing dependencies..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get update
    apt-get install -y curl git docker.io docker-compose jq
    systemctl enable docker
    systemctl start docker
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum install -y curl git docker docker-compose jq
    systemctl enable docker
    systemctl start docker
else
    echo "❌ Unsupported OS: $OS"
    exit 1
fi

# Create runner user
echo "👤 Creating runner user..."
if ! id "runner" &>/dev/null; then
    useradd -m -s /bin/bash runner
    usermod -aG docker runner
fi

# Download GitHub runner
echo "📥 Downloading GitHub Actions Runner..."
RUNNER_VERSION="2.311.0"
cd /home/runner
sudo -u runner mkdir -p actions-runner && cd actions-runner

sudo -u runner curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

sudo -u runner tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
rm actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

echo ""
echo "✅ Runner binaries installed"
echo ""
echo "📝 Next steps:"
echo "1. Go to: https://github.com/eidoscore/eidosSec/settings/actions/runners/new"
echo "2. Copy the registration token"
echo "3. Run as 'runner' user:"
echo "   sudo su - runner"
echo "   cd actions-runner"
echo "   ./config.sh --url https://github.com/eidoscore/eidosSec --token YOUR_TOKEN"
echo "   ./run.sh"
echo ""
echo "4. Or install as a service:"
echo "   sudo ./svc.sh install runner"
echo "   sudo ./svc.sh start"
echo ""
echo "🎉 Setup complete!"

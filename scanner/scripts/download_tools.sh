#!/bin/bash
set -e

# Function to download and extract
download_tool() {
    local name=$1
    local url=$2
    local type=$3 # tar.gz, zip, binary
    local target_dir="/usr/local/bin"
    
    echo "Downloading $name from $url..."
    
    if [ "$type" == "tar.gz" ]; then
        wget -q -O "$name.tar.gz" "$url"
        tar -xzf "$name.tar.gz"
        rm "$name.tar.gz"
        # Handle specific extraction logic if needed
        if [ "$name" == "gosec" ]; then
            mv gosec "$target_dir/"
        elif [ "$name" == "gitleaks" ]; then
            mv gitleaks "$target_dir/"
        elif [ "$name" == "trivy" ]; then
            mv trivy "$target_dir/"
        elif [ "$name" == "trufflehog" ]; then
            mv trufflehog "$target_dir/"
        fi
        
    elif [ "$type" == "zip" ]; then
        wget -q -O "$name.zip" "$url"
        unzip -q "$name.zip"
        rm "$name.zip"
        if [ "$name" == "codeql" ]; then
            # CodeQL extracts to a 'codeql' directory
            mv codeql "$target_dir/codeql-home"
            ln -s "$target_dir/codeql-home/codeql" "$target_dir/codeql"
        fi
    fi
    
    echo "$name installed successfully."
}

# Gitleaks
download_tool "gitleaks" "https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz" "tar.gz"

# Trivy
download_tool "trivy" "https://github.com/aquasecurity/trivy/releases/download/v0.48.3/trivy_0.48.3_Linux-64bit.tar.gz" "tar.gz"

# TruffleHog
download_tool "trufflehog" "https://github.com/trufflesecurity/trufflehog/releases/download/v3.63.2/trufflehog_3.63.2_linux_amd64.tar.gz" "tar.gz"

# Nuclei
download_tool "nuclei" "https://github.com/projectdiscovery/nuclei/releases/download/v3.2.4/nuclei_3.2.4_linux_amd64.zip" "zip"
mv nuclei /usr/local/bin/
rm -f nuclei-config.yaml
echo "nuclei installed successfully."

# Gosec (PRO)
download_tool "gosec" "https://github.com/securego/gosec/releases/download/v2.19.0/gosec_2.19.0_linux_amd64.tar.gz" "tar.gz"

# CodeQL (PRO) - Large download (~1GB), consider caching
# Using a specific version for stability
download_tool "codeql" "https://github.com/github/codeql-cli-binaries/releases/download/v2.16.0/codeql-linux64.zip" "zip"

# Staticcheck (Go)
# Using 'binary' strategy (tar.gz actually but simpler extraction)
echo "Downloading staticcheck..."
wget -q -O staticcheck.tar.gz https://github.com/dominikh/go-tools/releases/download/2023.1.6/staticcheck_linux_amd64.tar.gz
tar -xzf staticcheck.tar.gz
# Starts with staticcheck/staticcheck
mv staticcheck/staticcheck /usr/local/bin/
rm -rf staticcheck staticcheck.tar.gz
echo "staticcheck installed successfully."

# SpotBugs (Java)
echo "Downloading SpotBugs..."
wget -q -O spotbugs.tgz https://github.com/spotbugs/spotbugs/releases/download/4.8.3/spotbugs-4.8.3.tgz
tar -xzf spotbugs.tgz
mv spotbugs-4.8.3 /usr/local/bin/spotbugs-home
ln -s /usr/local/bin/spotbugs-home/bin/spotbugs /usr/local/bin/spotbugs
rm spotbugs.tgz
echo "SpotBugs installed successfully."

# PMD (Java)
echo "Downloading PMD..."
wget -q -O pmd.zip https://github.com/pmd/pmd/releases/download/pmd_7.0.0-rc4/pmd-dist-7.0.0-rc4-bin.zip
unzip -q pmd.zip
mv pmd-bin-7.0.0-rc4 /usr/local/bin/pmd-home
ln -s /usr/local/bin/pmd-home/bin/pmd /usr/local/bin/pmd
rm pmd.zip
echo "PMD installed successfully."

# ShellCheck
echo "Downloading ShellCheck..."
wget -q -O shellcheck.tar.xz https://github.com/koalaman/shellcheck/releases/download/v0.9.0/shellcheck-v0.9.0.linux.x86_64.tar.xz
tar -xf shellcheck.tar.xz
mv shellcheck-v0.9.0/shellcheck /usr/local/bin/
rm -rf shellcheck-v0.9.0 shellcheck.tar.xz
echo "ShellCheck installed successfully."

# KICS (IaC)
echo "Downloading KICS..."
wget -q -O kics.tar.gz https://github.com/Checkmarx/kics/releases/download/v1.7.13/kics_1.7.13_linux_x64.tar.gz
mkdir -p /usr/local/bin/kics-home
tar -xzf kics.tar.gz -C /usr/local/bin/kics-home
ln -s /usr/local/bin/kics-home/kics /usr/local/bin/kics
rm kics.tar.gz
echo "KICS installed successfully."

# ZAP baseline scripts
echo "Downloading ZAP baseline scripts..."
wget -q -O /usr/local/bin/zap-baseline.py https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap-baseline.py
wget -q -O /usr/local/bin/zap_common.py https://raw.githubusercontent.com/zaproxy/zaproxy/main/docker/zap_common.py
chmod +x /usr/local/bin/zap-baseline.py
echo "ZAP baseline scripts installed successfully."

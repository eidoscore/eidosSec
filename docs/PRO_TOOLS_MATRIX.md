# eidosSec - Complete Tools Matrix

**Total Tools:** 63 (FREE: 15, PRO: +48)
**All tools are 100% FREE & Open Source**

---

## Quick Reference

| Tier | Tools | Scan Time | Use Case |
|------|-------|-----------|----------|
| **FREE** | 15 | 5-10 min | Daily dev, CI/CD, hobby projects |
| **PRO** | 63 | 30-60 min | Pre-release audit, compliance, enterprise |

---

## FREE TIER (15 Tools)

### SAST - Static Analysis (6 tools)

| # | Tool | Languages | License | Install | Output |
|---|------|-----------|---------|---------|--------|
| 1 | **Semgrep** | 30+ langs | LGPL-2.1 | `pip install semgrep` | SARIF/JSON |
| 2 | **Bandit** | Python | Apache-2.0 | `pip install bandit` | JSON |
| 3 | **ESLint Security** | JS/TS | MIT | `npm install eslint eslint-plugin-security` | JSON |
| 4 | **PHPStan** | PHP | MIT | `composer require phpstan/phpstan` | JSON |
| 5 | **Brakeman** | Ruby/Rails | MIT | `gem install brakeman` | JSON |
| 6 | **Flawfinder** | C/C++ | GPL-2.0 | `pip install flawfinder` | JSON |

### Secrets Detection (3 tools)

| # | Tool | Focus | License | Install | Output |
|---|------|-------|---------|---------|--------|
| 7 | **TruffleHog** | Git history, files | AGPL-3.0 | `pip install trufflehog` | JSON |
| 8 | **Gitleaks** | Git repos, files | MIT | `go install gitleaks` | JSON |
| 9 | **detect-secrets** | Pre-commit, files | Apache-2.0 | `pip install detect-secrets` | JSON |

### SCA - Dependency Scanning (4 tools)

| # | Tool | Ecosystems | License | Install | Output |
|---|------|------------|---------|---------|--------|
| 10 | **Trivy** | Multi (npm, pip, etc) | Apache-2.0 | `apt install trivy` | JSON |
| 11 | **npm audit** | Node.js | Built-in | `npm audit --json` | JSON |
| 12 | **pip-audit** | Python | Apache-2.0 | `pip install pip-audit` | JSON |
| 13 | **composer audit** | PHP | Built-in | `composer audit --format=json` | JSON |

### IaC - Infrastructure as Code (2 tools)

| # | Tool | Platforms | License | Install | Output |
|---|------|-----------|---------|---------|--------|
| 14 | **Checkov** | Terraform, K8s, CFN, Docker | Apache-2.0 | `pip install checkov` | JSON/SARIF |
| 15 | **cfn-nag** | CloudFormation | MIT | `gem install cfn-nag` | JSON |

---

## PRO TIER (+48 Tools = 63 Total)

### SAST - Static Analysis (+12 = 18 total)

| # | Tool | Languages | License | Install | Why Include |
|---|------|-----------|---------|---------|-------------|
| 16 | **CodeQL** | Java, JS, Python, C++, Go, Ruby | MIT | `gh codeql` | Semantic analysis, data flow tracking |
| 17 | **Gosec** | Go | Apache-2.0 | `go install github.com/securego/gosec/v2/cmd/gosec@latest` | Go-specific security rules |
| 18 | **Staticcheck** | Go | MIT | `go install honnef.co/go/tools/cmd/staticcheck@latest` | Advanced Go static analysis |
| 19 | **SpotBugs** | Java | LGPL-2.1 | JAR download | FindBugs successor, bytecode analysis |
| 20 | **PMD** | Java, Apex, JS, XML | BSD-4 | Binary download | Copy-paste detection, code quality |
| 21 | **Find Security Bugs** | Java | LGPL-3.0 | SpotBugs plugin | OWASP security patterns |
| 22 | **Psalm** | PHP | MIT | `composer require vimeo/psalm` | Taint analysis, type safety |
| 23 | **Progpilot** | PHP | MIT | `composer require progpilot/progpilot` | PHP taint tracking |
| 24 | **Cppcheck** | C/C++ | GPL-3.0 | `apt install cppcheck` | Memory leaks, buffer overflows |
| 25 | **Infer** | C, C++, Java, ObjC | MIT | Binary / Docker | Facebook's inter-procedural analysis |
| 26 | **Security Code Scan** | C#, .NET | LGPL-3.0 | NuGet package | .NET security vulnerabilities |
| 27 | **cargo-audit** | Rust | Apache/MIT | `cargo install cargo-audit` | Rust crate vulnerabilities |

### DAST - Dynamic Testing (+10 = 10 total)

| # | Tool | Focus | License | Install | Why Include |
|---|------|-------|---------|---------|-------------|
| 28 | **OWASP ZAP** | Full web scanner | Apache-2.0 | Docker `zaproxy/zap-stable` | Industry standard, active scanning |
| 29 | **Nuclei** | Template-based | MIT | `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` | 5000+ community templates |
| 30 | **Nikto** | Web server | GPL-1.0 | `apt install nikto` | 6700+ server checks |
| 31 | **SQLMap** | SQL injection | GPL-2.0 | `pip install sqlmap` | Automated SQLi exploitation |
| 32 | **XSStrike** | XSS | GPL-3.0 | `pip install xsstrike` | Advanced XSS detection |
| 33 | **Commix** | Command injection | GPL-3.0 | `pip install commix` | OS command injection |
| 34 | **Dalfox** | XSS | MIT | `go install github.com/hahwul/dalfox/v2@latest` | Parameter analysis, XSS |
| 35 | **ffuf** | Fuzzing | MIT | `go install github.com/ffuf/ffuf/v2@latest` | Fast web fuzzer |
| 36 | **Wapiti** | Web scanner | GPL-2.0 | `pip install wapiti3` | Black-box web vuln scanner |
| 37 | **Gobuster** | Directory brute | Apache-2.0 | `go install github.com/OJ/gobuster/v3@latest` | Directory/DNS enumeration |

### Secrets Detection (+3 = 6 total)

| # | Tool | Focus | License | Install | Why Include |
|---|------|-------|---------|---------|-------------|
| 38 | **whispers** | Structured data | Apache-2.0 | `pip install whispers` | JSON/YAML/XML secrets |
| 39 | **git-secrets** | AWS focused | Apache-2.0 | `brew install git-secrets` | AWS credential patterns |
| 40 | **Talisman** | Pre-commit | MIT | Binary download | Prevent secret commits |

### SCA - Dependency Scanning (+6 = 10 total)

| # | Tool | Ecosystems | License | Install | Why Include |
|---|------|------------|---------|---------|-------------|
| 41 | **Grype** | Multi | Apache-2.0 | `curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh \| sh` | Anchore's vuln scanner |
| 42 | **OSV-Scanner** | Multi | Apache-2.0 | `go install github.com/google/osv-scanner/cmd/osv-scanner@latest` | Google's OSV database |
| 43 | **OWASP Dependency-Check** | Java, .NET, Node, Python, Ruby | Apache-2.0 | JAR download | NVD-based scanning |
| 44 | **bundler-audit** | Ruby | GPL-3.0 | `gem install bundler-audit` | Ruby gem vulnerabilities |
| 45 | **Retire.js** | JavaScript | Apache-2.0 | `npm install -g retire` | Known vulnerable JS libs |
| 46 | **Syft** | Multi | Apache-2.0 | `curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \| sh` | SBOM generation |

### Container Security (+7 = 7 total)

| # | Tool | Focus | License | Install | Why Include |
|---|------|-------|---------|---------|-------------|
| 47 | **Trivy (image mode)** | Container images | Apache-2.0 | Already have | OS & app vulns in images |
| 48 | **Grype (image mode)** | Container images | Apache-2.0 | Same as #41 | Alternative image scanner |
| 49 | **Clair** | Container images | Apache-2.0 | Docker image | CoreOS/Quay scanner |
| 50 | **Dockle** | Dockerfile | Apache-2.0 | Binary download | CIS Docker benchmark |
| 51 | **Hadolint** | Dockerfile | GPL-3.0 | `docker run hadolint/hadolint` | Dockerfile linter |
| 52 | **Docker Bench** | Docker host | Apache-2.0 | Shell script | CIS Docker host benchmark |
| 53 | **kube-bench** | Kubernetes | Apache-2.0 | Binary download | CIS Kubernetes benchmark |

### IaC Security (+6 = 8 total)

| # | Tool | Platforms | License | Install | Why Include |
|---|------|-----------|---------|---------|-------------|
| 54 | **tfsec** | Terraform | MIT | `go install github.com/aquasecurity/tfsec/cmd/tfsec@latest` | Terraform-specific rules |
| 55 | **Terrascan** | Terraform, K8s, Docker | Apache-2.0 | Binary download | 500+ policies |
| 56 | **KICS** | Multi-IaC | Apache-2.0 | Docker / binary | Terraform, K8s, Docker, Ansible |
| 57 | **Polaris** | Kubernetes | Apache-2.0 | Binary / Helm | K8s best practices |
| 58 | **kube-linter** | Kubernetes | Apache-2.0 | Binary download | K8s YAML linter |
| 59 | **Prowler** | AWS | Apache-2.0 | `pip install prowler` | AWS security audit |

### API Security (+3 = 3 total)

| # | Tool | Focus | License | Install | Why Include |
|---|------|-------|---------|---------|-------------|
| 60 | **Arjun** | Parameter discovery | GPL-3.0 | `pip install arjun` | Hidden parameter finding |
| 61 | **Kiterunner** | API endpoint brute | MIT | Binary download | API route discovery |
| 62 | **Schemathesis** | OpenAPI fuzzing | MIT | `pip install schemathesis` | API spec-based fuzzing |

### Mobile Security (+1 = 1 total)

| # | Tool | Focus | License | Install | Why Include |
|---|------|-------|---------|---------|-------------|
| 63 | **MobSF** | Android/iOS | GPL-3.0 | Docker image | Full mobile app analysis |

---

## Tool Integration Specifications

### Output Format Standardization

All tools output to JSON or SARIF. eidosSec normalizes to internal schema:

```json
{
  "tool": "semgrep",
  "finding_id": "uuid",
  "type": "sql-injection",
  "severity": "high",
  "confidence": 0.85,
  "file_path": "src/api/users.py",
  "line_start": 42,
  "line_end": 45,
  "code_snippet": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
  "message": "Potential SQL injection via string formatting",
  "cwe_id": "CWE-89",
  "owasp_category": "A03:2021-Injection",
  "remediation": "Use parameterized queries instead of string formatting",
  "references": ["https://cwe.mitre.org/data/definitions/89.html"]
}
```

### Docker Image Structure

```dockerfile
# Base image with common dependencies
FROM python:3.11-slim AS base

# Stage 1: Python tools
FROM base AS python-tools
RUN pip install semgrep bandit trufflehog gitleaks detect-secrets \
    pip-audit checkov sqlmap xsstrike commix wapiti3 arjun \
    schemathesis whispers prowler

# Stage 2: Go tools
FROM golang:1.21 AS go-tools
RUN go install github.com/securego/gosec/v2/cmd/gosec@latest && \
    go install honnef.co/go/tools/cmd/staticcheck@latest && \
    go install github.com/gitleaks/gitleaks/v8@latest && \
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install github.com/aquasecurity/tfsec/cmd/tfsec@latest && \
    go install github.com/ffuf/ffuf/v2@latest && \
    go install github.com/OJ/gobuster/v3@latest && \
    go install github.com/hahwul/dalfox/v2@latest && \
    go install github.com/google/osv-scanner/cmd/osv-scanner@latest

# Stage 3: Ruby tools
FROM ruby:3.2 AS ruby-tools
RUN gem install brakeman bundler-audit cfn-nag

# Stage 4: Node tools
FROM node:20 AS node-tools
RUN npm install -g eslint eslint-plugin-security retire

# Stage 5: Binary tools
FROM base AS binary-tools
# Trivy
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
# Grype
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh
# Syft
RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh
# Hadolint
RUN wget -qO /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64

# Final image: Combine all
FROM base AS final
COPY --from=python-tools /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=go-tools /go/bin/* /usr/local/bin/
COPY --from=ruby-tools /usr/local/bundle /usr/local/bundle
COPY --from=node-tools /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=binary-tools /usr/local/bin/* /usr/local/bin/

# Additional tools via apt
RUN apt-get update && apt-get install -y \
    cppcheck nikto openjdk-17-jre \
    && rm -rf /var/lib/apt/lists/*

# SpotBugs, PMD, OWASP Dependency-Check (JARs)
RUN mkdir -p /opt/tools && \
    wget -qO /opt/tools/spotbugs.zip https://github.com/spotbugs/spotbugs/releases/latest/download/spotbugs.zip && \
    wget -qO /opt/tools/pmd.zip https://github.com/pmd/pmd/releases/latest/download/pmd-bin.zip && \
    wget -qO /opt/tools/dependency-check.zip https://github.com/jeremylong/DependencyCheck/releases/latest/download/dependency-check.zip
```

### Estimated Image Size
- Python tools: ~800MB
- Go tools: ~400MB
- Ruby tools: ~200MB
- Node tools: ~150MB
- Binary tools: ~500MB
- Java JARs: ~300MB
- Base + apt: ~400MB
- **Total: ~2.7GB** (within 8GB limit)

---

## Scan Profiles

### Quick Scan (FREE) - 5-10 minutes

```yaml
tools:
  sast:
    - semgrep (patterns only, no interfile)
    - bandit
    - eslint
    - phpstan
    - brakeman
    - flawfinder
  secrets:
    - trufflehog (current commit only)
    - gitleaks (staged files)
    - detect-secrets
  sca:
    - trivy (lockfiles only)
    - npm-audit
    - pip-audit
    - composer-audit
  iac:
    - checkov (terraform only)
    - cfn-nag

settings:
  timeout_per_tool: 60s
  parallel_tools: 8
  skip_tests: true
  skip_vendor: true
```

### Deep Scan (PRO) - 30-60 minutes

```yaml
tools:
  # All FREE tools, plus:
  sast:
    - codeql (full semantic analysis)
    - gosec
    - staticcheck
    - spotbugs
    - pmd
    - find-security-bugs
    - psalm
    - progpilot
    - cppcheck
    - infer
    - security-code-scan
    - cargo-audit
  dast:
    - zap (active scan)
    - nuclei (full template set)
    - nikto
    - sqlmap (forms only)
    - xsstrike
    - commix
    - dalfox
    - ffuf (common wordlist)
    - wapiti
  secrets:
    - whispers
    - git-secrets
    - talisman
    - trufflehog (full history)
    - gitleaks (full repo)
  sca:
    - grype (full image)
    - osv-scanner
    - owasp-dependency-check
    - bundler-audit
    - retire.js
    - syft (SBOM)
  container:
    - trivy (image)
    - grype (image)
    - clair
    - dockle
    - hadolint
    - docker-bench
    - kube-bench
  iac:
    - tfsec
    - terrascan
    - kics
    - polaris
    - kube-linter
    - prowler
  api:
    - arjun
    - kiterunner
    - schemathesis
  mobile:
    - mobsf

settings:
  timeout_per_tool: 300s
  total_timeout: 3600s
  parallel_tools: 4
  skip_tests: false
  skip_vendor: false
  dast_target: auto-detect  # or user-provided URL
```

---

## Deduplication Rules

### Cross-Tool Correlation

```python
DEDUP_RULES = {
    # Same file + same line = exact match
    "exact": {
        "match": ["file_path", "line_start"],
        "action": "merge",
        "boost_confidence": 0.2
    },

    # Same file + within 5 lines + same type = near match
    "near": {
        "match": ["file_path", "type"],
        "line_tolerance": 5,
        "action": "merge",
        "boost_confidence": 0.15
    },

    # Same code pattern (AST hash) = similar match
    "similar": {
        "match": ["ast_hash", "type"],
        "action": "group",
        "boost_confidence": 0.1
    }
}

# Multi-tool verification scoring
CONFIDENCE_BOOST = {
    2: 0.10,  # 2 tools agree: +10%
    3: 0.20,  # 3 tools agree: +20%
    4: 0.30,  # 4+ tools agree: +30%
}
```

### Expected Deduplication Ratio

| Scan Type | Raw Findings | After Dedup | Ratio |
|-----------|--------------|-------------|-------|
| Quick Scan | ~200 | ~50 | 4:1 |
| Deep Scan | ~1500 | ~200 | 7.5:1 |

---

## Implementation Priority

### Month 5 (Week 1-4) - 80 hours

| Week | Focus | Tools | Hours |
|------|-------|-------|-------|
| 1 | SAST Multi-lang | CodeQL, Gosec, Staticcheck, SpotBugs, PMD | 20 |
| 2 | SAST Lang-specific | Find Security Bugs, Psalm, Progpilot, Cppcheck, Infer, Security Code Scan, cargo-audit | 20 |
| 3 | DAST | ZAP, Nuclei, Nikto, SQLMap, XSStrike | 20 |
| 4 | Secrets + SCA | whispers, git-secrets, Talisman, Grype, OSV-Scanner, Dep-Check, bundler-audit, Retire.js, Syft | 20 |

### Month 6 (Week 1-3) - 60 hours tools + 80 hours features

| Week | Focus | Tools | Hours |
|------|-------|-------|-------|
| 1 | Container | Grype, Clair, Dockle, Hadolint, Docker Bench, kube-bench | 18 |
| 2 | IaC + Cloud | tfsec, Terrascan, KICS, Polaris, kube-linter, Prowler | 20 |
| 3 | API + Mobile + DAST | Arjun, Kiterunner, Schemathesis, ffuf, Wapiti, Commix, Dalfox, MobSF | 22 |
| 4 | PRO Features | License, Payment, AI, Export | 80 |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Total tools integrated | 63 |
| Docker image size | < 8GB |
| Quick Scan time | < 10 min |
| Deep Scan time | < 60 min |
| Deduplication ratio | > 5:1 |
| False positive rate | < 15% |
| Coverage (OWASP Top 10) | 100% |

---

*Document Version: 1.0*
*Last Updated: 2026-02-03*

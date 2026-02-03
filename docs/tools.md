# Security Tools & Capabilities

eidosSec integrates **15 industry-leading open-source security tools** in the FREE tier to provide comprehensive coverage across your technology stack. All tools run locally within the Docker container—no code ever leaves your infrastructure.

## 🛡️ Static Application Security Testing (SAST)

These tools analyze your source code for vulnerabilities without executing it.

| Tool | Languages | Description |
|------|-----------|-------------|
| **Semgrep** | Multi-language | A fast, open-source static analysis tool that finds bugs and enforces code standards. Excellent for custom rules. |
| **Bandit** | Python | Designed to find common security issues in Python code, such as hardcoded passwords and SQL injection risks. |
| **ESLint** | JavaScript/TS | Pluggable linting utility for JavaScript and JSX, configured with security plugins to catch XSS and other web vulnerabilities. |
| **PHPStan** | PHP | detailed static analysis for PHP APIs and web applications. |
| **Brakeman** | Ruby on Rails | A static analysis security vulnerability scanner for Ruby on Rails applications. |

## 📦 Software Composition Analysis (SCA)

These tools check your dependencies (npm, pip, composer, etc.) for known vulnerabilities (CVEs).

| Tool | Ecosystem | Description |
|------|-----------|-------------|
| **Trivy** | Containers/FS | A comprehensive security scanner for vulnerabilities in container images, file systems, and git repositories. |
| **Safety** | Python | Checks installed Python dependencies for known security vulnerabilities. |
| **npm-audit** | Node.js | Scans your project for vulnerabilities in `npm` dependencies. |
| **Composer Audit** | PHP | Checks usage of known vulnerable PHP packages in `composer.lock`. |

## 🔑 Secrets Detection

Stops credentials, API keys, and tokens from leaking into production.

| Tool | Scope | Description |
|------|-------|-------------|
| **TruffleHog** | Git History/FS | Scans deep into commit history and branches for high-entropy strings and secrets. |
| **Gitleaks** | Git History | Detects hardcoded secrets like passwords, API keys, and tokens in git repos. |

## 🏗️ Infrastructure as Code (IaC)

Ensures your cloud infrastructure is configured securely.

| Tool | Platforms | Description |
|------|-----------|-------------|
| **Checkov** | Terraform/AWS/K8s | Scans cloud infrastructure configurations to find misconfigurations before they're deployed. |
| **cfn_nag** | CloudFormation | Looks for patterns in CloudFormation templates that may indicate insecure infrastructure. |

## 💥 Dynamic Application Security Testing (DAST)

Tests running applications for vulnerabilities (Note: Requires a running target URL).

| Tool | Type | Description |
|------|------|-------------|
| **OWASP ZAP** | Web App | The world’s most popular free security scanner. Finds OWASP Top 10 issues like SQLi and XSS in running apps. |
| **Nuclei** | Web App | Fast and customizable vulnerability scanner based on simple YAML based templates. |

## 🔄 Deduplication Engine

eidosSec doesn't just list raw output. Our **intelligent deduplication engine**:
1.  **Normalizes** finding formats from all 15 tools.
2.  **Correlates** findings that point to the same file and line number.
3.  **Merges** duplicates to reduce noise.
4.  **Prioritizes** fixes based on multi-tool confirmation confidence scores.

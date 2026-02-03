# Month 5 Week 1: Tool Expansion Plan

## Goal
Integrate 3 new tools to expand coverage across SAST, SCA, and IaC categories, moving towards the 50+ tool target.

## New Tools

### 1. ShellCheck (SAST)
- **Language:** Shell/Bash
- **Type:** Static Analysis
- **Execution:** `shellcheck -f json script.sh`
- **Location:** `scanner/app/tools/sast/shellcheck.py`

### 2. Retire.js (SCA)
- **Language:** JavaScript
- **Type:** Software Composition Analysis (Client-side)
- **Execution:** `retire --outputformat json --outputpath result.json --path .`
- **Location:** `scanner/app/tools/sca/retirejs.py`

### 3. KICS (IaC)
- **Language:** Terraform, Kubernetes, Docker, Ansible, etc.
- **Type:** Infrastructure as Code Security
- **Execution:** `kics scan -p . -o . --output-name kics-results.json`
- **Location:** `scanner/app/tools/iac/kics.py`

## Implementation Steps
1.  **Structure:** Create package `__init__.py` for `sca` and `iac`.
2.  **Wrappers:** Implement the 3 wrapper classes inheriting from `ToolWrapper`.
3.  **Docker:** Update `download_tools.sh` and `Dockerfile` to install these tools.
    - ShellCheck: apt-get or binary
    - Retire.js: npm
    - KICS: binary/tar.gz
4.  **Orchestrator:** Register tools.

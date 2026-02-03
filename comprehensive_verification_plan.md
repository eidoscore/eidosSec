# Comprehensive Verification Plan (Months 1-5)

## Objective
Verify all features and quality metrics of eidosSec from its inception (Month 1) to the completion of Month 5 (PRO Expansion).

## 1. Test Categories & Tools

### Level 1: Core Testing
- **Unit Testing**: Pytest for Backend/Scanner logic.
- **Integration Testing**: Testing interactions between Backend, Scanner, Postgres, and Redis.
- **System Testing**: End-to-end scan flow using Docker Compose.
- **Acceptance (UAT)**: Manual/Automated verification of the primary user journeys (Project Creation -> Scan -> Report).

### Level 2: Quality & Special Tests
- **Functional**: Verification of all 50+ tool integrations and AI Analysis.
- **Performance/Scalability**: [Locust](https://locust.io/) or custom scripts to measure scan throughput and API latency.
- **Stress**: Testing system behavior under high project volume.
- **Security**: Dogfooding eidosSec to scan its own codebase + Dependency check.
- **Memory/Concurrency**: Monitoring scanner process behavior during multiple concurrent deep scans.

## 2. Execution Strategy
1. **Local Preparation**: Create missing test scripts for Performance, Concurrency, and Stress.
2. **Server Execution**: Update `.github/workflows/run-tests.yml` to include all levels and metrics.
3. **Trigger**: Manually trigger the workflow on the remote server (IP: 43.245.249.18).
4. **Report Generation**: Consolidate artifacts into a unified Month 1-5 report.

## 3. Reporting Structure (Month 1-5)
| Month | Focus | Status | Test results |
|-------|-------|--------|--------------|
| M1 | Foundations | [Verified] | Core CRUD, Basic Scan |
| M2 | Aggregation | [Verified] | Deduplication, Multi-tool |
| M3 | DAST/Infrastructure | [Verified] | Network/OWASP ZAP integration |
| M4 | Enterprise Core | [Verified] | Multi-tenancy, reporting |
| M5 | PRO & AI | [RE-VERIFYING] | 50+ Tools, AI Analysis, License |

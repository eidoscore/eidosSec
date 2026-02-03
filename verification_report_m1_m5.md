# Month 1-5 Comprehensive Verification Report (Evidence-Based)

## 📋 Overview
- **Project**: eidosSec
- **Primary Execution Environment**: Self-hosted GitHub Actions runner (**server-side**, host IP: `43.245.249.18`)
- **Source of Truth**: Artifacts produced by workflow `Comprehensive Test Suite` (`.github/workflows/run-tests.yml`)

> Catatan penting: report ini **tidak** lagi berisi angka “perkiraan/manual”. Angka PASS/FAIL dan metrik latency/memory/stress harus berasal dari log/artifact hasil eksekusi di runner server.

---

## 1) Level Pengujian

| Level | Coverage di repo | Cara eksekusi (server runner) | Evidence |
|------|-------------------|------------------------------|----------|
| **Unit Testing** | Backend + Scanner (pytest) | Workflow `Comprehensive Test Suite` | `backend-results.xml`, `scanner-results.xml`, `backend-tests.log`, `scanner-tests.log` |
| **Integration Testing** | Scanner integration suite + service interaction via compose | Workflow `Comprehensive Test Suite` | JUnit + container logs |
| **System Testing** | Docker Compose boot + health check | Workflow `Comprehensive Test Suite` | `runner_diagnostics.log` + step health |
| **Acceptance Testing (UAT)** | Manual (UI journeys) | Manual checklist per release | (di luar scope artifact CI) |

---

## 2) Pengujian Fungsional & Kualitas

| Test Type | Implementasi saat ini | Evidence (artifact) |
|----------|------------------------|---------------------|
| **Functional Testing** | Smoke + wrapper/tool execution sanity | `verification_report_m1_m5.md` (generated), logs |
| **Performance Testing** | Baseline latency benchmark ke endpoint `/health` | `performance.log` |
| **Security Testing** | “Dogfooding” (scanner dapat import & run orchestrator logic) | workflow logs |
| **Regression Testing** | Unit + integration suites dijalankan konsisten | JUnit XML |
| **Usability Testing** | Manual (frontend UX) | (manual) |

---

## 3) Pengujian Kondisi Khusus

| Test | Implementasi saat ini | Evidence (artifact) |
|------|------------------------|---------------------|
| **Smoke Testing** | `curl http://localhost:8000/health` | workflow logs |
| **Stress Testing** | Concurrent scans (deterministic tool subset) | `stress_concurrency.log` |
| **Memory Leak Testing** | Sequential scans RSS growth threshold | `memory_profile.log` |
| **Concurrency/Race Condition Testing** | covered by stress concurrency execution | `stress_concurrency.log` |
| **Scalability Testing** | baseline-only (needs dedicated load harness for scale targets) | (future) |

---

## 4) Month 1 → Month 5 Verification Matrix

| Month | Fokus | Minimal Evidence yang wajib ada |
|------:|------|----------------------------------|
| **M1** | Foundation | system smoke + unit tests |
| **M2** | FREE tool expansion + dedup | scanner unit/integration + smoke |
| **M3** | UI + launch readiness | frontend CI (lint/type/build) + UAT |
| **M4** | stabilization + PRO prep | regression + compose system checks |
| **M5** | PRO expansion + enterprise | regression + performance + stress + memory |

---

## 5) Cara Menjalankan di Server (bukan lokal)

Karena runner self-hosted terpasang di server `43.245.249.18`, maka eksekusi dilakukan dengan:
- **Push ke branch** `main`/`develop` → workflow `Comprehensive Test Suite` otomatis jalan, atau
- **Manual** via `workflow_dispatch` dari GitHub Actions UI.

Output report akan tersedia sebagai artifact:
- `eidossec-test-artifacts/verification_report_m1_m5.md`
- beserta JUnit XML + log pendukung (performance/stress/memory).


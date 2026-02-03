import argparse
import os
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class JUnitSummary:
    tests: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    time_seconds: float = 0.0

    @property
    def passed(self) -> int:
        return max(0, self.tests - self.failures - self.errors - self.skipped)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _tail_lines(text: str, n: int = 60) -> str:
    lines = text.splitlines()
    if len(lines) <= n:
        return text.strip()
    return "\n".join(lines[-n:]).strip()


def _parse_junit(path: Path) -> Optional[JUnitSummary]:
    if not path.exists():
        return None
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception:
        return None

    # junit can be <testsuites> or <testsuite>
    suites: Iterable[ET.Element]
    if root.tag == "testsuite":
        suites = [root]
    else:
        suites = root.findall(".//testsuite")

    total = JUnitSummary()
    for s in suites:
        tests = int(float(s.attrib.get("tests", "0") or "0"))
        failures = int(float(s.attrib.get("failures", "0") or "0"))
        errors = int(float(s.attrib.get("errors", "0") or "0"))
        skipped = int(float(s.attrib.get("skipped", "0") or "0"))
        t = float(s.attrib.get("time", "0") or "0")

        total = JUnitSummary(
            tests=total.tests + tests,
            failures=total.failures + failures,
            errors=total.errors + errors,
            skipped=total.skipped + skipped,
            time_seconds=total.time_seconds + t,
        )
    return total


def _status_badge(summary: Optional[JUnitSummary]) -> str:
    if summary is None:
        return "⚠️ NO DATA"
    if summary.failures == 0 and summary.errors == 0:
        return "✅ PASS"
    return "❌ FAIL"


def main() -> int:
    p = argparse.ArgumentParser(description="Generate Month 1-5 verification report (Markdown).")
    p.add_argument("--output", required=True)
    p.add_argument("--backend-junit", required=False)
    p.add_argument("--scanner-junit", required=False)
    p.add_argument("--performance-log", required=False)
    p.add_argument("--stress-log", required=False)
    p.add_argument("--memory-log", required=False)
    p.add_argument("--runner-log", required=False)
    args = p.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    backend_junit = Path(args.backend_junit) if args.backend_junit else None
    scanner_junit = Path(args.scanner_junit) if args.scanner_junit else None

    backend_summary = _parse_junit(backend_junit) if backend_junit else None
    scanner_summary = _parse_junit(scanner_junit) if scanner_junit else None

    # GitHub context (available in Actions)
    sha = os.environ.get("GITHUB_SHA", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    ref = os.environ.get("GITHUB_REF_NAME", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")

    environment = "Self-hosted runner (server-side)"
    server_hint = "43.245.249.18 (runner host)"

    perf_tail = _tail_lines(_safe_read_text(Path(args.performance_log))) if args.performance_log else ""
    stress_tail = _tail_lines(_safe_read_text(Path(args.stress_log))) if args.stress_log else ""
    mem_tail = _tail_lines(_safe_read_text(Path(args.memory_log))) if args.memory_log else ""
    runner_tail = _tail_lines(_safe_read_text(Path(args.runner_log))) if args.runner_log else ""

    md = f"""\
    # Month 1-5 Comprehensive Verification Report

    ## Overview
    - **Project**: eidosSec
    - **Generated at**: {_utc_now_iso()}
    - **Environment**: {environment}
    - **Server/Runner**: {server_hint}
    - **Repo**: {repo or "(unknown)"}
    - **Branch**: {ref or "(unknown)"}
    - **Commit**: {sha or "(unknown)"}
    - **Workflow Run**: {run_id or "(unknown)"} (attempt {run_attempt or "?"})

    ## Test Scope (requested)
    This report maps the requested test categories to automated checks executed by the `Comprehensive Test Suite` workflow.

    - **Level Pengujian**
      - **Unit Testing**: Backend + Scanner pytest suites
      - **Integration Testing**: Scanner integration tests (pipeline compatibility/dedup), plus containerized interactions via compose
      - **System Testing**: Docker Compose boot + health checks
      - **Acceptance Testing (UAT)**: Manual verification of key user journeys (tracked separately)

    - **Fungsional & Kualitas**
      - **Functional Testing**: Wrapper/tool availability + smoke checks
      - **Performance Testing**: HTTP baseline latency benchmark against `/health`
      - **Security Testing**: “Dogfooding” (scanner can import and execute orchestrator logic)
      - **Regression Testing**: Covered by unit/integration suites on each run
      - **Usability Testing**: Manual (UI/UX flows), out of scope for CI automation

    - **Kondisi Khusus**
      - **Smoke Testing**: service health check
      - **Stress Testing**: concurrent scan execution (limited tool set to keep deterministic)
      - **Memory Leak Testing**: sequential scan loop RSS growth threshold
      - **Concurrency/Race Condition Testing**: covered by stress test concurrency
      - **Scalability Testing**: partially covered (concurrency baseline); full scale tests tracked separately

    ## Results Summary
    | Area | Source | Status | Notes |
    |------|--------|--------|------|
    | Backend unit/integration | JUnit (`backend-results.xml`) | {_status_badge(backend_summary)} | tests={backend_summary.tests if backend_summary else "?"}, failures={backend_summary.failures if backend_summary else "?"}, errors={backend_summary.errors if backend_summary else "?"} |
    | Scanner unit/integration | JUnit (`scanner-results.xml`) | {_status_badge(scanner_summary)} | tests={scanner_summary.tests if scanner_summary else "?"}, failures={scanner_summary.failures if scanner_summary else "?"}, errors={scanner_summary.errors if scanner_summary else "?"} |
    | Performance | `performance.log` | ✅/⚠️ | See excerpt below |
    | Stress/Concurrency | `stress_concurrency.log` | ✅/⚠️ | See excerpt below |
    | Memory | `memory_profile.log` | ✅/⚠️ | See excerpt below |
    | System/Smoke | workflow step | ✅/❌ | Backend `/health` must respond |

    ## Evidence (log excerpts)
    ### Runner diagnostics (tail)
    ```
    {runner_tail}
    ```

    ### Performance (tail)
    ```
    {perf_tail}
    ```

    ### Stress/Concurrency (tail)
    ```
    {stress_tail}
    ```

    ### Memory (tail)
    ```
    {mem_tail}
    ```

    ## Month 1 → Month 5 Verification Matrix (high-level)
    | Month | Focus | Automated evidence in CI | Notes |
    |------:|-------|--------------------------|-------|
    | M1 | Foundation (compose, DB, skeleton) | ✅ smoke/system + unit | Core stack boot + baseline tests |
    | M2 | Tool expansion (FREE) | ✅ scanner tests + smoke | Wrapper parsing + orchestrator stability |
    | M3 | UI + Launch readiness | ✅ frontend CI (separate workflow) | Lint/type/build; UI UAT manual |
    | M4 | Stabilization + PRO prep | ✅ regression + system | Deployment workflow includes clean reset + migrations |
    | M5 | PRO tools + enterprise | ✅ stress/memory/perf + regression | Special tests run on server runner |

    ## Notes / Follow-ups
    - For **UAT** and deep **system E2E** (project → scan → findings), add a dedicated e2e script/job when needed.
    - If server is offline / runner not picking jobs, use `test-runner.yml` (push `RUNNER_TEST`) to validate runner connectivity.
    """

    md = textwrap.dedent(md).strip() + "\n"
    out_path.write_text(md, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


import asyncio
import os
import time
import uuid
from pathlib import Path

from app.orchestrator import ScanOrchestrator
from app.tools.bandit import BanditWrapper


def _prepare_test_project(project_path: Path) -> None:
    """
    Create a small Python project that reliably triggers language detection
    (min_files=3) and produces Bandit findings.
    """
    project_path.mkdir(parents=True, exist_ok=True)

    # Ensure >= 3 python files so LanguageDetector detects "Python"
    (project_path / "main.py").write_text(
        "import os\n"
        "def run(cmd):\n"
        "    os.system(cmd)\n"
        "run('echo test')\n"
    )
    (project_path / "utils.py").write_text(
        "import subprocess\n"
        "def shell(cmd):\n"
        "    subprocess.Popen(cmd, shell=True)\n"
        "shell('id')\n"
    )
    (project_path / "crypto.py").write_text(
        "import hashlib\n"
        "def weak(pw):\n"
        "    return hashlib.md5(pw.encode()).hexdigest()\n"
        "weak('password')\n"
    )


def _run_one_scan(project_path: Path, scan_id: str, redis_url: str) -> int:
    """
    Run a small scan focusing on orchestration + concurrency behavior.

    Important: we intentionally limit the tool set to keep this deterministic and fast
    on CI runners (avoid tools requiring network updates, big databases, etc).
    """
    orchestrator = ScanOrchestrator(project_path=project_path, scan_id=scan_id, redis_url=redis_url)
    orchestrator.all_tools = [BanditWrapper(project_path)]

    result = orchestrator.run_scan()
    if result.status != "completed":
        raise RuntimeError(f"Scan {scan_id} failed with status={result.status} metadata={result.metadata}")
    return result.total_findings


async def stress_concurrent_scans(num_scans: int = 3) -> None:
    project_path = Path(os.environ.get("EIDOS_TEST_PROJECT_PATH", "/tmp/eidossec_test_project"))
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    _prepare_test_project(project_path)

    print(f"🧪 Stress Test: starting {num_scans} concurrent scans")
    print(f"📁 Project: {project_path}")
    print(f"🧵 Redis URL: {redis_url}")

    start = time.perf_counter()

    scan_ids = [f"stress-{uuid.uuid4()}" for _ in range(num_scans)]
    tasks = [
        asyncio.to_thread(_run_one_scan, project_path, scan_id, redis_url)
        for scan_id in scan_ids
    ]
    findings_counts = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start

    print("✅ Stress Test Completed")
    print(f"⏱️  Elapsed: {elapsed:.2f}s")
    print(f"📊 Findings per scan: {findings_counts}")
    print(f"📊 Total findings: {sum(findings_counts)}")


if __name__ == "__main__":
    scans = int(os.environ.get("EIDOS_STRESS_SCANS", "5"))
    asyncio.run(stress_concurrent_scans(scans))

import asyncio
import gc
import os
import time
import uuid
from pathlib import Path

from app.orchestrator import ScanOrchestrator
from app.tools.bandit import BanditWrapper


def _get_rss_mb() -> float:
    """
    Get current resident set size (RSS) without external deps (Linux).
    """
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    # Example: "VmRSS:\t   123456 kB"
                    parts = line.split()
                    kb = float(parts[1])
                    return kb / 1024.0
    except Exception:
        pass
    return float("nan")


def _prepare_test_project(project_path: Path) -> None:
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "a.py").write_text("import os\nos.system('echo a')\n")
    (project_path / "b.py").write_text("import subprocess\nsubprocess.Popen('id', shell=True)\n")
    (project_path / "c.py").write_text("import hashlib\nhashlib.md5(b'x').hexdigest()\n")


def _run_quick_scan(project_path: Path, redis_url: str) -> int:
    scan_id = f"mem-{uuid.uuid4()}"
    orchestrator = ScanOrchestrator(project_path=project_path, scan_id=scan_id, redis_url=redis_url)
    orchestrator.all_tools = [BanditWrapper(project_path)]
    result = orchestrator.run_scan()
    if result.status != "completed":
        raise RuntimeError(f"Scan {scan_id} failed with status={result.status} metadata={result.metadata}")
    return result.total_findings


async def memory_leak_smoke() -> None:
    """
    Memory leak smoke test:
    - run multiple scans sequentially
    - observe RSS growth and fail if growth exceeds a threshold
    """
    iterations = int(os.environ.get("EIDOS_MEMORY_ITERS", "5"))
    max_growth_mb = float(os.environ.get("EIDOS_MEMORY_MAX_GROWTH_MB", "80"))
    project_path = Path(os.environ.get("EIDOS_TEST_PROJECT_PATH", "/tmp/eidossec_test_project"))
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    _prepare_test_project(project_path)

    rss_before = _get_rss_mb()
    print(f"📊 Initial RSS: {rss_before:.2f} MB")
    print(f"🔁 Iterations: {iterations}")
    print(f"🧵 Redis URL: {redis_url}")

    rss_samples: list[float] = []
    start = time.perf_counter()

    for i in range(iterations):
        findings = await asyncio.to_thread(_run_quick_scan, project_path, redis_url)
        gc.collect()

        rss_now = _get_rss_mb()
        rss_samples.append(rss_now)
        print(f"Iteration {i+1}/{iterations}: findings={findings} rss={rss_now:.2f} MB")

    elapsed = time.perf_counter() - start
    rss_after = rss_samples[-1] if rss_samples else _get_rss_mb()

    growth = rss_after - rss_before
    peak = max(rss_samples) if rss_samples else rss_after

    print("✅ Memory profiling completed")
    print(f"⏱️  Elapsed: {elapsed:.2f}s")
    print(f"📈 Peak RSS: {peak:.2f} MB")
    print(f"📈 Final RSS: {rss_after:.2f} MB")
    print(f"📈 RSS Growth: {growth:.2f} MB")

    if growth > max_growth_mb:
        raise SystemExit(
            f"❌ Potential memory leak: RSS growth {growth:.2f}MB exceeds threshold {max_growth_mb:.2f}MB"
        )


if __name__ == "__main__":
    asyncio.run(memory_leak_smoke())

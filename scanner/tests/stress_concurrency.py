import time
import asyncio
from app.orchestrator import ScanOrchestrator
import os

async def test_concurrent_scans(num_scans=3):
    """Stress test by running multiple scans concurrently"""
    project_path = "/tmp/test_project" # Ensure this exists in CI environment
    if not os.path.exists(project_path):
        os.makedirs(project_path, exist_ok=True)
        with open(f"{project_path}/main.py", "w") as f:
            f.write("import os\nos.system('echo test')\n")

    print(f"🧪 Stress Test: Initiating {num_scans} concurrent scans...")
    
    start_time = time.time()
    
    async def run_one_scan(scan_id):
        orchestrator = ScanOrchestrator(project_path)
        # Mocking the actual scan execution for speed in CI, or running real one
        print(f"Scan {scan_id} started...")
        results = await orchestrator.execute_scan(mode="quick")
        print(f"Scan {scan_id} finished with {len(results)} findings.")
        return results

    tasks = [run_one_scan(i) for i in range(num_scans)]
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    print(f"✅ Stress Test Completed in {end_time - start_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_concurrent_scans(5))

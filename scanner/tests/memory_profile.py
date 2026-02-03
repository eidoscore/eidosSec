import sys
import os
import psutil
from app.orchestrator import ScanOrchestrator
import asyncio

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024) # MB

async def profile_memory():
    print(f"📊 Initial Memory: {get_memory_usage():.2f} MB")
    
    project_path = "." # Scan self
    orchestrator = ScanOrchestrator(project_path)
    
    print("🚀 Running deep scan for memory profiling...")
    
    # Track memory during execution
    results = await orchestrator.execute_scan(mode="quick")
    
    print(f"📊 Final Memory: {get_memory_usage():.2f} MB")
    print(f"✅ Profiling complete. Findings: {len(results)}")

if __name__ == "__main__":
    asyncio.run(profile_memory())

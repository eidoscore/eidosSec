import httpx
import asyncio
import time
import statistics

async def benchmark_endpoint(url, num_requests=100, concurrency=10):
    async with httpx.AsyncClient() as client:
        latencies = []
        
        async def make_request():
            start = time.perf_counter()
            try:
                # Testing health endpoint as a baseline
                resp = await client.get(url)
                latencies.append(time.perf_counter() - start)
            except Exception as e:
                print(f"Request failed: {e}")

        # Run in batches for concurrency
        for i in range(0, num_requests, concurrency):
            tasks = [make_request() for _ in range(concurrency)]
            await asyncio.gather(*tasks)

        if latencies:
            print(f"\n--- Performance Report for {url} ---")
            print(f"Total Requests: {len(latencies)}")
            print(f"Average Latency: {statistics.mean(latencies)*1000:.2f}ms")
            print(f"P95 Latency: {statistics.quantiles(latencies, n=20)[18]*1000:.2f}ms")
            print(f"Max Latency: {max(latencies)*1000:.2f}ms")
            return latencies
        return []

if __name__ == "__main__":
    # In CI/Server, we point to localhost:8000
    API_URL = "http://localhost:8000/health"
    print("🚀 Starting Load Test...")
    asyncio.run(benchmark_endpoint(API_URL, 100, 10))

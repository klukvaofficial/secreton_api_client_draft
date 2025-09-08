"""Simple health check for Secreton API endpoints."""

import asyncio
import time
from typing import Dict, List

import httpx

class HealthChecker:
    """Simple health checker for API endpoints."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.endpoints = [
            # Public endpoints (no auth required)
            "/api/auth/login",

            # These might require auth, but we can check if they respond
            "/api/orders/service_types",
            "/api/profile/profile",
            "/api/orders/",
            "/api/orders/view",
            "/api/orders/new",
            "/api/orders/pay",
            "/api/profile/topup",
        ]

    async def check_endpoint(self, endpoint: str, client: httpx.AsyncClient) -> Dict:
        """Check if an endpoint is reachable."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            # Try GET request first
            response = await client.get(url, timeout=10.0)
            elapsed = (time.time() - start_time) * 1000

            return {
                "endpoint": endpoint,
                "status": "reachable",
                "status_code": response.status_code,
                "response_time_ms": round(elapsed, 2),
                "error": None
            }

        except httpx.TimeoutException:
            elapsed = (time.time() - start_time) * 1000
            return {
                "endpoint": endpoint,
                "status": "timeout",
                "status_code": None,
                "response_time_ms": round(elapsed, 2),
                "error": "Request timed out"
            }

        except httpx.ConnectError:
            elapsed = (time.time() - start_time) * 1000
            return {
                "endpoint": endpoint,
                "status": "unreachable",
                "status_code": None,
                "response_time_ms": round(elapsed, 2),
                "error": "Cannot connect to server"
            }

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return {
                "endpoint": endpoint,
                "status": "error",
                "status_code": None,
                "response_time_ms": round(elapsed, 2),
                "error": str(e)
            }

    async def check_all(self) -> List[Dict]:
        """Check all endpoints."""
        print(f"🏥 Health checking API endpoints at {self.base_url}")
        print("-" * 60)

        async with httpx.AsyncClient() as client:
            results = []

            for endpoint in self.endpoints:
                print(f"Checking {endpoint}...", end=" ")
                result = await self.check_endpoint(endpoint, client)
                results.append(result)

                # Print result
                if result["status"] == "reachable":
                    status_code = result["status_code"]
                    response_time = result["response_time_ms"]

                    if status_code in [200, 201]:
                        print(f"✅ {status_code} ({response_time}ms)")
                    elif status_code in [401, 403]:
                        print(f"🔒 {status_code} - Auth required ({response_time}ms)")
                    elif status_code == 422:
                        print(f"📝 {status_code} - Validation error ({response_time}ms)")
                    elif status_code == 404:
                        print(f"❓ {status_code} - Not found ({response_time}ms)")
                    else:
                        print(f"⚠️ {status_code} ({response_time}ms)")

                elif result["status"] == "timeout":
                    print(f"⏱️ TIMEOUT ({result['response_time_ms']}ms)")

                elif result["status"] == "unreachable":
                    print("❌ UNREACHABLE")

                else:
                    print(f"💥 ERROR: {result['error']}")

        return results

    def print_summary(self, results: List[Dict]) -> None:
        """Print health check summary."""
        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 60)

        total = len(results)
        reachable = sum(1 for r in results if r["status"] == "reachable")
        timeouts = sum(1 for r in results if r["status"] == "timeout")
        unreachable = sum(1 for r in results if r["status"] == "unreachable")
        errors = sum(1 for r in results if r["status"] == "error")

        print(f"Total Endpoints: {total}")
        print(f"✅ Reachable: {reachable}")
        print(f"⏱️ Timeouts: {timeouts}")
        print(f"❌ Unreachable: {unreachable}")
        print(f"💥 Errors: {errors}")

        if reachable > 0:
            avg_response_time = sum(r["response_time_ms"] for r in results if r["status"] == "reachable") / reachable
            print(f"📊 Average Response Time: {avg_response_time:.2f}ms")

        # Status code distribution
        status_codes = {}
        for result in results:
            if result["status_code"]:
                code = result["status_code"]
                status_codes[code] = status_codes.get(code, 0) + 1

        if status_codes:
            print("\nStatus Code Distribution:")
            for code, count in sorted(status_codes.items()):
                print(f"  {code}: {count}")

async def main():
    """Run health check."""
    import os

    BASE_URL = os.getenv("SECRETON_API_URL", "https://api.secreton.com")

    checker = HealthChecker(BASE_URL)
    results = await checker.check_all()
    checker.print_summary(results)

if __name__ == "__main__":
    asyncio.run(main())
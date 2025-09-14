"""Simple load test for API endpoints."""

import asyncio
import time
from typing import List, Dict

from secreton_api_client import SecretOnClient


async def load_test_endpoint(
    client: SecretOnClient,
    endpoint_name: str,
    endpoint_func,
    concurrent_requests: int = 10,
    **kwargs,
) -> Dict:
    """Load test a specific endpoint."""
    print(
        f"🔄 Load testing {endpoint_name} with {concurrent_requests} concurrent requests..."
    )

    start_time = time.time()
    errors = []
    successful_requests = 0

    async def single_request():
        nonlocal successful_requests
        try:
            await endpoint_func(**kwargs)
            successful_requests += 1
        except Exception as e:
            errors.append(str(e))

    # Run concurrent requests
    tasks = [single_request() for _ in range(concurrent_requests)]
    await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    total_time = end_time - start_time

    result = {
        "endpoint": endpoint_name,
        "concurrent_requests": concurrent_requests,
        "successful_requests": successful_requests,
        "failed_requests": len(errors),
        "total_time": total_time,
        "requests_per_second": concurrent_requests / total_time,
        "success_rate": (successful_requests / concurrent_requests) * 100,
        "errors": errors[:5],  # Show first 5 errors
    }

    print(
        f"✅ {endpoint_name}: {successful_requests}/{concurrent_requests} successful "
        f"({result['success_rate']:.1f}%) in {total_time:.2f}s "
        f"({result['requests_per_second']:.1f} req/s)"
    )

    return result


async def main():
    """Run load tests."""
    BASE_URL = "http://176.114.89.94:5648/api/"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMGE2Y2E5OWQtMmQ1Yy00YmY5LWJhYzctZTU3NDc5NzIzZTE2IiwiY3JlYXRlZF9hdCI6MTc1NzMwMTI2OX0.cBUPpwfoBa70eRut3lH3WPexYVyJTaHwGFMnRPRFmrA"  # Replace with real token

    if not TOKEN or TOKEN == "your-auth-token":
        print("❌ Please set a valid authentication token")
        return

    async with SecretOnClient(BASE_URL, TOKEN) as client:
        results = []

        # Test 1: Service types (low load)
        result1 = await load_test_endpoint(
            client,
            "Get Service Types",
            client.orders.get_service_types,
            concurrent_requests=5,
            auth=client.get_auth(),
        )
        results.append(result1)

        # Test 2: Profile (medium load)
        result2 = await load_test_endpoint(
            client,
            "Get Profile",
            client.profile.get_profile,
            concurrent_requests=10,
            auth=client.get_auth(),
        )
        results.append(result2)

        # Test 3: List orders (higher load)
        result3 = await load_test_endpoint(
            client,
            "List Orders",
            client.orders.list_orders,
            concurrent_requests=15,
            auth=client.get_auth(),
            page=1,
        )
        results.append(result3)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 LOAD TEST SUMMARY")
        print("=" * 60)

        for result in results:
            print(f"\n{result['endpoint']}:")
            print(f"  Requests: {result['concurrent_requests']}")
            print(f"  Success Rate: {result['success_rate']:.1f}%")
            print(f"  RPS: {result['requests_per_second']:.1f}")
            print(f"  Total Time: {result['total_time']:.2f}s")

            if result["errors"]:
                print(f"  Sample Errors:")
                for error in result["errors"]:
                    print(f"    • {error}")


if __name__ == "__main__":
    asyncio.run(main())

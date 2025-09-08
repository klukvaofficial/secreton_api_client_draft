"""Comprehensive endpoint testing for Secreton API."""

import asyncio
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from secreton_api_client import SecretOnClient
from secreton_api_client.exceptions import (
    APIClientError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)


class EndpointTester:
    """Test all API endpoints systematically."""

    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        self.test_results: List[Dict] = []
        self.test_data = {}  # Store data between tests

    async def run_all_tests(self) -> None:
        """Run all endpoint tests."""
        print("🚀 Starting comprehensive endpoint testing...")
        print(f"📡 API URL: {self.base_url}")
        print("=" * 80)

        async with SecretOnClient(self.base_url, self.token) as client:
            self.client = client

            # Test groups
            await self.test_auth_endpoints()
            await self.test_profile_endpoints()
            await self.test_orders_endpoints()

        # Print summary
        self.print_summary()

    async def test_auth_endpoints(self) -> None:
        """Test authentication endpoints."""
        print("\n🔐 Testing Authentication Endpoints")
        print("-" * 50)

        # Test 1: Login with phone
        await self.test_endpoint(
            "Login with Phone", self.client.auth.login, phone=79123456789
        )

        # Test 2: Login with invalid phone
        await self.test_endpoint(
            "Login with Invalid Phone",
            self.client.auth.login,
            phone=123456789,  # Invalid
            expect_error=True,
        )

        # Test 3: Password login (if we have credentials)
        await self.test_endpoint(
            "Password Login",
            self.client.auth.password_login,
            phone=79123456789,
            password="testpassword123",
            expect_error=True,  # Might fail without real credentials
        )

        # Test 4: Phone confirmation (will fail without real request_id)
        await self.test_endpoint(
            "Phone Confirmation",
            self.client.auth.phone_confirmation,
            request_id=uuid4(),
            code=1234,
            expect_error=True,
        )

        # Test 5: Set password (will fail without real request_id)
        await self.test_endpoint(
            "Set Password",
            self.client.auth.set_password,
            request_id=uuid4(),
            password="newpassword123",
            expect_error=True,
        )

        # Test 6: Send code (will fail without real request_id)
        await self.test_endpoint(
            "Send Code",
            self.client.auth.send_code,
            request_id=uuid4(),
            expect_error=True,
        )

        # Test 7: Logout (needs authentication)
        if self.client.get_auth():
            await self.test_endpoint(
                "Logout", self.client.auth.logout, auth=self.client.get_auth()
            )

    async def test_profile_endpoints(self) -> None:
        """Test profile endpoints."""
        print("\n👤 Testing Profile Endpoints")
        print("-" * 50)

        if not self.client.get_auth():
            print("⚠️ Skipping profile tests - no authentication token")
            return

        # Test 1: Get current user profile
        result = await self.test_endpoint(
            "Get Current Profile",
            self.client.profile.get_profile,
            auth=self.client.get_auth(),
        )

        # Test 2: Get profile with user_id
        await self.test_endpoint(
            "Get Profile by User ID",
            self.client.profile.get_profile,
            auth=self.client.get_auth(),
            user_id=uuid4(),
            expect_error=True,  # Might not exist
        )

        # Test 3: Top up balance
        await self.test_endpoint(
            "Top up Balance",
            self.client.profile.topup_balance,
            amount=100.0,
            auth=self.client.get_auth(),
        )

        # Test 4: Top up with invalid amount
        await self.test_endpoint(
            "Top up Invalid Amount",
            self.client.profile.topup_balance,
            amount=5.0,  # Less than minimum
            auth=self.client.get_auth(),
            expect_error=True,
        )

    async def test_orders_endpoints(self) -> None:
        """Test order endpoints."""
        print("\n📋 Testing Orders Endpoints")
        print("-" * 50)

        if not self.client.get_auth():
            print("⚠️ Skipping orders tests - no authentication token")
            return

        # Test 1: Get service types
        await self.test_endpoint(
            "Get Service Types",
            self.client.orders.get_service_types,
            auth=self.client.get_auth(),
        )

        # Test 2: List orders
        await self.test_endpoint(
            "List Orders",
            self.client.orders.list_orders,
            auth=self.client.get_auth(),
            page=1,
        )

        # Test 3: List orders with filters
        await self.test_endpoint(
            "List Orders with Filters",
            self.client.orders.list_orders,
            auth=self.client.get_auth(),
            service_type="transcription",
            status="completed",
            tags=["test"],
            page=1,
        )

        # Test 4: Create order with file
        test_file = await self.create_test_file()
        try:
            result = await self.test_endpoint(
                "Create Order",
                self.client.orders.create_order,
                order_name="Test Order",  # <-- Изменили name на order_name
                service_type=1,
                file=test_file,
                auth=self.client.get_auth(),
                tags=["test", "automated"],
                comments=["Test order from endpoint testing"],
            )

            # Store order_id for subsequent tests
            if result and hasattr(result, "order_id"):
                self.test_data["order_id"] = result.order_id

        finally:
            # Cleanup test file
            test_file.unlink(missing_ok=True)

        # Test 5: Get order (if we created one)
        if "order_id" in self.test_data:
            await self.test_endpoint(
                "Get Order",
                self.client.orders.get_order,
                order_id=self.test_data["order_id"],
                auth=self.client.get_auth(),
            )

            # Test 6: Pay order
            await self.test_endpoint(
                "Pay Order",
                self.client.orders.pay_order,
                order_id=self.test_data["order_id"],
                auth=self.client.get_auth(),
            )

            # Test 7: Summarize order
            await self.test_endpoint(
                "Summarize Order",
                self.client.orders.summarize_order,
                order_id=self.test_data["order_id"],
                auth=self.client.get_auth(),
            )

        # Test 8: Get non-existent order
        await self.test_endpoint(
            "Get Non-existent Order",
            self.client.orders.get_order,
            order_id=uuid4(),
            auth=self.client.get_auth(),
            expect_error=True,
        )

    async def create_test_file(self) -> Path:
        """Create a temporary test file for upload."""
        test_file = Path(tempfile.mktemp(suffix=".mp3"))
        test_file.write_bytes(b"fake audio content for testing")
        return test_file

    async def test_endpoint(
        self, name: str, func, expect_error: bool = False, **kwargs
    ) -> Optional[any]:
        """Test a single endpoint."""
        result = {
            "name": name,
            "success": False,
            "error": None,
            "response": None,
            "status": "unknown",
        }

        try:
            print(f"🧪 Testing: {name}...", end=" ")
            response = await func(**kwargs)

            if expect_error:
                result["status"] = "unexpected_success"
                result["error"] = "Expected error but got success"
                print("⚠️ UNEXPECTED SUCCESS")
            else:
                result["success"] = True
                result["response"] = response
                result["status"] = "success"
                print("✅ SUCCESS")

                # Print response preview
                if hasattr(response, "__dict__"):
                    print(f"   📄 Response: {type(response).__name__}")
                elif isinstance(response, list):
                    print(f"   📄 Response: List with {len(response)} items")
                elif isinstance(response, dict):
                    print(
                        f"   📄 Response: Dict with keys: {list(response.keys())[:3]}..."
                    )

            self.test_results.append(result)
            return response

        except (ValueError, TypeError) as e:
            if expect_error:
                result["success"] = True
                result["status"] = "expected_error"
                print("✅ EXPECTED ERROR")
            else:
                result["error"] = str(e)
                result["status"] = "validation_error"
                print(f"❌ VALIDATION ERROR: {e}")

        except AuthenticationError as e:
            result["error"] = str(e)
            result["status"] = "auth_error"
            if expect_error:
                result["success"] = True
                print("✅ EXPECTED AUTH ERROR")
            else:
                print(f"🔒 AUTH ERROR: {e.message}")

        except ValidationError as e:
            result["error"] = str(e)
            result["status"] = "api_validation_error"
            if expect_error:
                result["success"] = True
                print("✅ EXPECTED VALIDATION ERROR")
            else:
                print(f"📝 VALIDATION ERROR: {e.message}")

        except NotFoundError as e:
            result["error"] = str(e)
            result["status"] = "not_found"
            if expect_error:
                result["success"] = True
                print("✅ EXPECTED NOT FOUND")
            else:
                print(f"🔍 NOT FOUND: {e.message}")

        except APIClientError as e:
            result["error"] = str(e)
            result["status"] = "api_error"
            if expect_error:
                result["success"] = True
                print("✅ EXPECTED API ERROR")
            else:
                print(f"⚡ API ERROR: {e.message}")

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "unexpected_error"
            print(f"💥 UNEXPECTED ERROR: {e}")

        self.test_results.append(result)
        return None

    def print_summary(self) -> None:
        """Print test results summary."""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests

        print(f"Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests / total_tests * 100):.1f}%")

        # Group by status
        status_counts = {}
        for result in self.test_results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        print("\nStatus Breakdown:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")

        # Show failed tests
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print(f"\n❌ Failed Tests ({len(failed_results)}):")
            for result in failed_results:
                print(f"  • {result['name']}: {result['error']}")

        print("\n" + "=" * 80)


async def main():
    """Main function to run endpoint tests."""
    import os

    # Configuration
    BASE_URL = os.getenv("SECRETON_API_URL", "https://api.secreton.com")
    TOKEN = os.getenv("SECRETON_API_TOKEN")  # Optional

    if not TOKEN:
        print("⚠️ No SECRETON_API_TOKEN found. Some tests will be skipped.")
        print("Set environment variable: export SECRETON_API_TOKEN='your-token'")

    # Run tests
    tester = EndpointTester(BASE_URL, TOKEN)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

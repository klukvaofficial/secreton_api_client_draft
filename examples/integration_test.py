"""Full integration test with real authentication flow."""

import asyncio
import tempfile
from pathlib import Path

from secreton_api_client import SecretOnClient

async def integration_test():
    """Run full integration test with authentication."""
    print("🔧 Starting Integration Test")
    print("=" * 50)

    BASE_URL = "https://api.secreton.com"

    async with SecretOnClient(BASE_URL) as client:

        try:
            # Step 1: Health check
            print("\n1️⃣ Health Check")
            # You could add a simple endpoint check here

            # Step 2: Authentication flow
            print("\n2️⃣ Authentication Flow")
            print("Enter phone number (79XXXXXXXXX): ", end="")
            phone = input()

            if not phone.isdigit() or len(phone) != 11:
                print("❌ Invalid phone number format")
                return

            try:
                # Login
                login_resp = await client.auth.login(phone=int(phone))
                print(f"✅ Login request sent. Request ID: {login_resp.request_id}")

                # Get SMS code
                print("Enter SMS code: ", end="")
                code = input()

                if not code.isdigit():
                    print("❌ Invalid code format")
                    return

                # Confirm phone
                confirm_resp = await client.auth.phone_confirmation(
                    request_id=login_resp.request_id,
                    code=int(code)
                )
                print("✅ Phone confirmed")

                # Set password
                print("Enter new password: ", end="")
                password = input()

                password_resp = await client.auth.set_password(
                    request_id=login_resp.request_id,
                    password=password
                )

                if hasattr(password_resp, 'token') and password_resp.token:
                    client.set_token(password_resp.token)
                    print("✅ Password set and token received")
                else:
                    print("✅ Password set")

            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                # Try password login as fallback
                try:
                    print("\nTrying password login...")
                    password = input("Enter password: ")
                    login_resp = await client.auth.password_login(
                        phone=int(phone),
                        password=password
                    )

                    if hasattr(login_resp, 'token') and login_resp.token:
                        client.set_token(login_resp.token)
                        print("✅ Logged in with password")
                    else:
                        print("❌ No token received from login")
                        return

                except Exception as e2:
                    print(f"❌ Password login also failed: {e2}")
                    return

            # Step 3: Profile operations
            print("\n3️⃣ Profile Operations")
            try:
                profile = await client.profile.get_profile(auth=client.get_auth())
                print(f"✅ Profile loaded: {profile.email if hasattr(profile, 'email') else 'User'}")
                print(f"   Balance: ${profile.balance if hasattr(profile, 'balance') else 0}")
            except Exception as e:
                print(f"❌ Failed to load profile: {e}")

            # Step 4: Orders operations
            print("\n4️⃣ Orders Operations")
            try:
                # Get service types
                service_types = await client.orders.get_service_types(auth=client.get_auth())
                print(f"✅ Service types loaded: {len(service_types)} available")

                # List orders
                orders = await client.orders.list_orders(auth=client.get_auth())
                print(f"✅ Orders loaded: {len(orders)} orders found")

                # Create test order (optional)
                create_order = input("\nCreate test order? (y/n): ").lower() == 'y'
                if create_order:
                    test_file = Path(tempfile.mktemp(suffix=".mp3"))
                    test_file.write_bytes(b"fake audio content for integration test")

                    try:
                        order = await client.orders.create_order(
                            name="Integration Test Order",
                            service_type=1,
                            file=test_file,
                            auth=client.get_auth(),
                            tags=["integration", "test"],
                            comments=["Created during integration testing"]
                        )
                        print(f"✅ Test order created: {order.order_id}")

                        # Get the created order
                        order_details = await client.orders.get_order(
                            order.order_id,
                            auth=client.get_auth()
                        )
                        print(f"✅ Order details retrieved: {order_details.name}")

                    finally:
                        test_file.unlink(missing_ok=True)

            except Exception as e:
                print(f"❌ Orders operations failed: {e}")

            print("\n🎉 Integration test completed!")

        except KeyboardInterrupt:
            print("\n⏹️ Test interrupted by user")
        except Exception as e:
            print(f"\n💥 Integration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(integration_test())
"""Example demonstrating both sync and async client usage."""

import asyncio
from secreton_api_client import SyncSecretOnClient, AsyncSecretOnClient

# Example with synchronous client
def sync_example():
    """Example using synchronous client."""
    print("=== Synchronous Client Example ===")
    
    with SyncSecretOnClient("https://api.secreton.ru") as client:
        # Login
        try:
            login_resp = client.auth.login(phone=79123456789)
            print(f"Login response: {login_resp}")
            
            # Set token after authentication
            client.set_token("your-auth-token")
            
            # Use authenticated services
            if client.get_auth():
                profile = client.profile.get_profile(auth=client.get_auth())
                print(f"Profile: {profile}")
                
                orders = client.orders.list_orders(auth=client.get_auth())
                print(f"Orders: {orders}")
        except Exception as e:
            print(f"Error: {e}")

# Example with asynchronous client
async def async_example():
    """Example using asynchronous client."""
    print("=== Asynchronous Client Example ===")
    
    async with AsyncSecretOnClient("https://api.secreton.ru") as client:
        # Login
        try:
            login_resp = await client.auth.login(phone=79123456789)
            print(f"Login response: {login_resp}")
            
            # Set token after authentication
            client.set_token("your-auth-token")
            
            # Use authenticated services
            if client.get_auth():
                profile = await client.profile.get_profile(auth=client.get_auth())
                print(f"Profile: {profile}")
                
                orders = await client.orders.list_orders(auth=client.get_auth())
                print(f"Orders: {orders}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Run sync example
    sync_example()
    
    # Run async example
    asyncio.run(async_example())

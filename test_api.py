"""
Quick API test script
"""
import httpx
import asyncio
import uuid

async def test_api():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=10.0) as client:
        # Test root endpoint
        print("Testing root endpoint...")
        response = await client.get("/")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        print()

        # Test health endpoint
        print("Testing health endpoint...")
        response = await client.get("/health")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        print()

        # Generate a test device token
        device_token = str(uuid.uuid4())
        headers = {"Authorization": f"Bearer {device_token}"}

        # Test creating a task
        print(f"Testing task creation with device token: {device_token}...")
        task_data = {
            "text": "Test task from API test",
            "position": 0
        }
        response = await client.post("/tasks", json=task_data, headers=headers)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        print()

        # Test listing tasks
        print("Testing task listing...")
        response = await client.get("/tasks", headers=headers)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        print()

if __name__ == "__main__":
    try:
        asyncio.run(test_api())
        print("\n[SUCCESS] All API tests completed!")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

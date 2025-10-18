"""
Quick server startup script to diagnose issues
"""
import sys
import traceback

try:
    print("Attempting to import FastAPI app...")
    from backend.src.main import app
    print("[OK] Import successful")

    print("\nAttempting to start server...")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

except Exception as e:
    print(f"\n[ERROR] Error occurred: {type(e).__name__}")
    print(f"Message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

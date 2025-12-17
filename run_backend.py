import asyncio
import sys
import uvicorn
import os

def main():
    # Force ProactorEventLoopPolicy on Windows BEFORE anything else happens
    if sys.platform == 'win32':
        print("Setting WindowsProactorEventLoopPolicy...")
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    print("Starting Uvicorn Server on port 8081...")
    # Run uvicorn programmatically (reload=False to ensure loop policy is respected in same process)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8081, reload=False)

if __name__ == "__main__":
    main()

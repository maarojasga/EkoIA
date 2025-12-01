import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.append(project_root)

print(f"Project root: {project_root}")

try:
    from app.main import startup_event, DATA_PATH
    print(f"DATA_PATH: {DATA_PATH}")
    print("Imported app.main successfully")
except Exception as e:
    print(f"Error importing app.main: {e}")
    sys.exit(1)

async def main():
    print("Running startup_event...")
    try:
        await startup_event()
        print("startup_event completed successfully")
    except Exception as e:
        print(f"Error in startup_event: {e}")

if __name__ == "__main__":
    asyncio.run(main())

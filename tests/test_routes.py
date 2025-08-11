import asyncio
from datetime import datetime

from src.services.custom.routes import find_all_paths


async def test_find_all_paths():
    print("\n=== Testing find_all_paths ===")
    test_date = datetime(2025, 6, 10).date()
    start_point_id = 6
    end_point_id = 82
    container_ids = [6]

    try:
        result = await find_all_paths(test_date, start_point_id, end_point_id, container_ids)
        routes = list(result) if hasattr(result, '__iter__') else []

        print(f"Found {len(routes)} routes")

        if not routes:
            print("No routes found. Possible issues:")
            print("- Check if database connection is established")
            print("- Verify the query logic in find_all_paths")
            return

        print("\nFirst route details:")
        for key, value in routes[0].items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"Error in find_all_paths: {str(e)}")
        raise


async def main():
    await test_find_all_paths()


if __name__ == "__main__":
    asyncio.run(main())

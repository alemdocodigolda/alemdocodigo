import asyncio
from backend.crawler import crawl_site

async def test():
    print("Testing Playwright Crawler...")
    try:
        results = await crawl_site("https://best-credit.pt/home/", max_pages=1)
        print("Success!")
        print(results)
    except Exception as e:
        print("Caught exception:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

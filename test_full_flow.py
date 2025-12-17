import asyncio
from backend.crawler import crawl_site
from backend.compliance import analyze_compliance

async def test_full():
    url = "https://best-credit.pt/home/"
    print(f"Testing FULL FLOW for {url}...")
    try:
        # 1. Crawl
        pages = await crawl_site(url, max_pages=1)
        print(f"Crawled {len(pages)} pages.")
        
        # 2. Analyze
        print("Analyzing...")
        result = await analyze_compliance(pages)
        print("Analysis Result:")
        print(result['status'])
        print(f"Score: {result['score']}")
        print(f"Issues: {len(result['issues'])}")
        
    except Exception as e:
        print("Caught exception in FULL FLOW:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full())

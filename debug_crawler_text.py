import asyncio
from backend.crawler import crawl_site

async def debug_text():
    url = "https://www.creditoaqui.pt"
    print(f"Debugging crawler for: {url}")
    try:
        results = await crawl_site(url, max_pages=1)
        if not results:
            print("No results returned!")
            return
            
        page_data = results[0]
        text = page_data.get('text', '')
        print(f"Text Length: {len(text)}")
        print("--- Text Snippet (First 500 chars) ---")
        print(text[:500])
        print("--- End Snippet ---")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_text())

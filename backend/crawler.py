from playwright.async_api import async_playwright
import os
import uuid
from typing import Dict, List, Tuple

# Directory to save screenshots
SCREENSHOT_DIR = "frontend/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def crawl_site(start_url: str, max_pages: int = 3) -> List[Dict]:
    """
    Crawls the site using Playwright.
    Returns a list of dicts: {'url': str, 'text': str, 'screenshot': str}
    """
    results = []
    visited_urls = set()
    queue = [start_url]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Browser context with more permissive settings
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ignore_https_errors=True
        )
        
        while queue and len(visited_urls) < max_pages:
            url = queue.pop(0)
            if url in visited_urls:
                continue
            
            visited_urls.add(url)
            print(f"Crawling (Playwright): {url}")
            
            page = await context.new_page()
            try:
                # Increased timeout to 45s and use networkidle to ensure all resources (API, images) are loaded
                await page.goto(url, timeout=45000, wait_until="networkidle")
                
                # Auto-scroll to bottom to trigger lazy loading
                await page.evaluate("""
                    async () => {
                        await new Promise((resolve) => {
                            let totalHeight = 0;
                            const distance = 100;
                            const timer = setInterval(() => {
                                const scrollHeight = document.body.scrollHeight;
                                window.scrollBy(0, distance);
                                totalHeight += distance;

                                if(totalHeight >= scrollHeight){
                                    clearInterval(timer);
                                    resolve();
                                }
                            }, 100);
                        });
                    }
                """)
                
                # Extra safety wait for animations/loading after scroll
                await page.wait_for_timeout(3000)
                
                # --- VISUAL HIGHLIGHT INJECTION ---
                from .rules import FORBIDDEN_TERMS
                terms_to_highlight = list(FORBIDDEN_TERMS.keys())
                
                # Execute JS to find and highlight terms AND regex patterns
                await page.evaluate(f"""
                    (terms) => {{
                        function highlightText(root, term, isRegex=false) {{
                            const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
                            let node;
                            const nodesToHighlight = [];
                            
                            while (node = walker.nextNode()) {{
                                let match = false;
                                if (isRegex) {{
                                    if (term.test(node.nodeValue)) match = true;
                                }} else {{
                                    if (node.nodeValue.toLowerCase().includes(term)) match = true;
                                }}
                                
                                if (match) nodesToHighlight.push(node);
                            }}
                            
                            nodesToHighlight.forEach(node => {{
                                const parent = node.parentNode;
                                if (parent && parent.style) {{
                                   if (isRegex) {{
                                        // Specific style for Rates/Numbers (Blue/Cyan)
                                        parent.style.border = '3px dashed blue';
                                        parent.style.backgroundColor = '#e0f7fa'; 
                                        parent.style.color = 'black'; 
                                   }} else {{
                                        // Danger terms (Red/Yellow)
                                        parent.style.border = '5px solid red';
                                        parent.style.backgroundColor = 'yellow';
                                        parent.style.color = 'black';
                                   }}
                                }}
                            }});
                        }}
                        
                        // Highlight forbidden terms
                        terms.forEach(term => {{
                            highlightText(document.body, term);
                        }});
                        
                        // Highlight Potential Rates (Regex for percentages)
                        // Matches number + space? + %
                        const rateRegex = /\\d+([.,]\\d+)?\\s?%/;
                        highlightText(document.body, rateRegex, true);
                    }}
                """, terms_to_highlight)
                
                # Capture FULL PAGE to ensure we satisfy "screenshot where the problem is"
                # Screenshot is taken AFTER highlighting
                filename = f"{uuid.uuid4()}.png"
                screenshot_path = os.path.join(SCREENSHOT_DIR, filename)
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Get text and HTML content
                text_content = await page.evaluate("document.body.innerText")
                html_content = await page.content() # Capture raw HTML for location tagging
                
                results.append({
                    "url": url,
                    "text": text_content,
                    "html": html_content,
                    "screenshot": f"screenshots/{filename}" # Relative path for frontend
                })
                
                # Find internal links
                links = await page.evaluate("""
                    () => {
                        return Array.from(document.querySelectorAll('a[href]'))
                            .map(a => a.href)
                            .filter(href => href.startsWith(window.location.origin))
                    }
                """)
                
                for link in links:
                    if link not in visited_urls and link not in queue:
                        queue.append(link)
                        
            except Exception as e:
                print(f"Error crawling {url}: {e}")
            finally:
                await page.close()
                
        await browser.close()
        
    return results

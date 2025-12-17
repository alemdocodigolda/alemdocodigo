from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import sys
import asyncio

# CRITICAL: Force ProactorEventLoop on Windows for Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from .crawler import crawl_site
from .compliance import analyze_compliance

app = FastAPI(title="BdP Compliance Checker")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount screenshots directory
os.makedirs("frontend/screenshots", exist_ok=True)
app.mount("/screenshots", StaticFiles(directory="frontend/screenshots"), name="screenshots")

class AnalyzeRequest(BaseModel):
    url: str

class ComplianceIssue(BaseModel):
    rule: str
    description: str
    severity: str
    suggestion: str
    context: Optional[str] = None
    location_guide: Optional[str] = "Não identificada"
    url: str
    screenshot: str

class AnalysisResult(BaseModel):
    score: int
    status: str
    issues: List[ComplianceIssue]
    scanned_pages: int

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_url(request: AnalyzeRequest):
    try:
        print(f"Starting Premium Analysis for {request.url}")
        # Crawl with Playwright (returns list of page objects)
        pages = await crawl_site(request.url, max_pages=3)
        
        # Analyze
        result = await analyze_compliance(pages)
        
        return result
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"Server Error: {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

# Mount Frontend Static Files (Must be last to avoid intercepting API routes)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)

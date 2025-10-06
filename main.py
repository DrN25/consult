"""
PMC to DOI Lookup API
Simple FastAPI service to get DOI from PMC ID
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PMC to DOI API",
    description="Get DOI from PMC ID and metadata from Semantic Scholar",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Semantic Scholar API key from environment variable
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

# Rate limiter: 1 request per second for Semantic Scholar API
last_request_time = None
rate_limit_lock = asyncio.Lock()

async def rate_limit():
    """Ensure we don't exceed 1 request per second to Semantic Scholar"""
    global last_request_time
    async with rate_limit_lock:
        if last_request_time is not None:
            elapsed = datetime.now().timestamp() - last_request_time
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
        last_request_time = datetime.now().timestamp()

# Request/Response models
class PMCRequest(BaseModel):
    pmc_id: str

class DOIResponse(BaseModel):
    pmc_id: str
    doi: Optional[str] = None
    found: bool
    message: str

class MetadataResponse(BaseModel):
    doi: Optional[str] = None
    pmc_id: Optional[str] = None  # Include PMC if converted
    found: bool
    message: str
    data: Optional[Dict[str, Any]] = None

def load_doi_mapping(pmc_id: str) -> Optional[dict]:
    """
    Load DOI data for a given PMC ID from JSON file
    
    Args:
        pmc_id: PMC identifier (with or without 'PMC' prefix)
    
    Returns:
        Dict with PMC and DOI or None if not found
    """
    # Normalize PMC ID to ensure it has PMC prefix
    pmc_upper = pmc_id.upper().strip()
    if not pmc_upper.startswith("PMC"):
        pmc_with_prefix = f"PMC{pmc_upper}"
    else:
        pmc_with_prefix = pmc_upper
    
    # Path to DOI JSON files
    # In Vercel, files are at the same level as main.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "doi", f"{pmc_with_prefix}.json")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[ERROR] Loading DOI for {pmc_with_prefix}: {str(e)}")
        return None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "PMC to DOI Lookup API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /doi/{pmc_id}": "Get DOI by PMC ID (path parameter)",
            "POST /doi": "Get DOI by PMC ID (JSON body)",
            "GET /metadata/{doi_or_pmc}": "Get metadata from Semantic Scholar by DOI or PMC ID (auto-converts PMC to DOI)"
        },
        "example_usage": {
            "GET /doi": "/doi/PMC2910419 or /doi/2910419",
            "POST /doi": "/doi with body: {\"pmc_id\": \"PMC2910419\"}",
            "GET /metadata": "/metadata/10.1016/j.heliyon.2023.e16103 or /metadata/PMC2897429"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pmc-doi-api"}

@app.get("/doi/{pmc_id}")
async def get_doi_by_path(pmc_id: str):
    """
    Get DOI for a PMC ID using path parameter
    
    Example: GET /doi/PMC2910419
    Example: GET /doi/2910419
    """
    # Load DOI data
    doi_data = load_doi_mapping(pmc_id)
    
    if doi_data is None:
        return DOIResponse(
            pmc_id=pmc_id,
            doi=None,
            found=False,
            message=f"PMC {pmc_id} not found in database"
        )
    
    return DOIResponse(
        pmc_id=doi_data.get("PMC", pmc_id),
        doi=doi_data.get("DOI"),
        found=True,
        message="DOI found successfully"
    )

@app.post("/doi")
async def get_doi_by_body(request: PMCRequest):
    """
    Get DOI for a PMC ID using JSON body
    
    Example: POST /doi
    Body: {"pmc_id": "PMC2910419"}
    """
    # Load DOI data
    doi_data = load_doi_mapping(request.pmc_id)
    
    if doi_data is None:
        return DOIResponse(
            pmc_id=request.pmc_id,
            doi=None,
            found=False,
            message=f"PMC {request.pmc_id} not found in database"
        )
    
    return DOIResponse(
        pmc_id=doi_data.get("PMC", request.pmc_id),
        doi=doi_data.get("DOI"),
        found=True,
        message="DOI found successfully"
    )

async def get_semantic_scholar_metadata(doi: str) -> Optional[Dict[str, Any]]:
    """
    Fetch metadata from Semantic Scholar API
    Rate limited to 1 request per second
    
    Args:
        doi: DOI identifier (e.g., "10.1016/j.heliyon.2023.e16103")
    
    Returns:
        Dict with metadata or None if error
    """
    # Apply rate limiting (1 request per second)
    await rate_limit()
    
    # Semantic Scholar API endpoint and fields (as per official example)
    fields = "citationCount,influentialCitationCount,url,openAccessPdf,fieldsOfStudy,journal"
    url = f"https://api.semanticscholar.org/graph/v1/paper/{doi}?fields={fields}"
    
    # Headers with API key
    headers = {}
    if SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = SEMANTIC_SCHOLAR_API_KEY
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            elif response.status_code == 429:
                print(f"[ERROR] Rate limit exceeded for DOI {doi}")
                return None
            else:
                print(f"[ERROR] Semantic Scholar API returned {response.status_code}: {response.text}")
                return None
                
    except Exception as e:
        print(f"[ERROR] Fetching metadata for DOI {doi}: {str(e)}")
        return None

@app.get("/metadata/{doi_or_pmc:path}")
async def get_metadata_by_doi(doi_or_pmc: str):
    """
    Get metadata from Semantic Scholar for a given DOI or PMC ID
    
    If a PMC ID is provided, it will be automatically converted to DOI first.
    
    Examples: 
    - GET /metadata/10.1016/j.heliyon.2023.e16103
    - GET /metadata/PMC2897429
    - GET /metadata/2897429
    """
    doi = doi_or_pmc
    original_input = doi_or_pmc
    pmc_id = None
    
    # Check if input is a PMC ID (contains "PMC" or is just numbers)
    is_pmc = doi_or_pmc.upper().startswith("PMC") or doi_or_pmc.isdigit()
    
    if is_pmc:
        # Convert PMC to DOI first
        doi_data = load_doi_mapping(doi_or_pmc)
        
        if doi_data is None:
            return MetadataResponse(
                doi=None,
                pmc_id=doi_or_pmc,
                found=False,
                message=f"PMC {doi_or_pmc} not found in database. Cannot retrieve metadata.",
                data=None
            )
        
        pmc_id = doi_data.get("PMC", doi_or_pmc)
        doi = doi_data.get("DOI")
        if not doi:
            return MetadataResponse(
                doi=None,
                pmc_id=pmc_id,
                found=False,
                message=f"DOI not available for PMC {doi_or_pmc}",
                data=None
            )
    
    # Fetch metadata from Semantic Scholar
    metadata = await get_semantic_scholar_metadata(doi)
    
    if metadata is None:
        return MetadataResponse(
            doi=doi,
            pmc_id=pmc_id,
            found=False,
            message=f"Metadata not found for DOI: {doi}" + (f" (converted from {original_input})" if is_pmc else ""),
            data=None
        )
    
    return MetadataResponse(
        doi=doi,
        pmc_id=pmc_id,
        found=True,
        message="Metadata retrieved successfully" + (f" (converted from PMC {original_input})" if is_pmc else ""),
        data=metadata
    )

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

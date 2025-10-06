"""
PMC to DOI Lookup API
Simple FastAPI service to get DOI from PMC ID
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from typing import Optional

app = FastAPI(
    title="PMC to DOI API",
    description="Get DOI from PMC ID",
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

# Request/Response models
class PMCRequest(BaseModel):
    pmc_id: str

class DOIResponse(BaseModel):
    pmc_id: str
    doi: Optional[str] = None
    found: bool
    message: str

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
            "POST /doi": "Get DOI by PMC ID (JSON body)"
        },
        "example_usage": {
            "GET": "/doi/PMC2910419 or /doi/2910419",
            "POST": "/doi with body: {\"pmc_id\": \"PMC2910419\"}"
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

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

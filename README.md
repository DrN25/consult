# PMC to DOI Lookup API

Simple FastAPI service to convert PMC IDs to DOI identifiers.

## Features

- ✅ Get DOI from PMC ID
- ✅ Get metadata from Semantic Scholar by DOI
- ✅ Supports both GET and POST methods
- ✅ Rate limiting (1 request/second to Semantic Scholar)
- ✅ CORS enabled
- ✅ Ready for Vercel deployment
- ✅ Health check endpoint

## API Endpoints

### GET /
Get API information and usage examples

### GET /health
Health check endpoint

### GET /doi/{pmc_id}
Get DOI by PMC ID (path parameter)

**Example:**
```bash
curl http://localhost:8001/doi/PMC2910419
curl http://localhost:8001/doi/2910419
```

**Response:**
```json
{
  "pmc_id": "PMC2910419",
  "doi": "10.1152/jn.00378.2010",
  "found": true,
  "message": "DOI found successfully"
}
```

### POST /doi
Get DOI by PMC ID (JSON body)

**Example:**
```bash
curl -X POST http://localhost:8001/doi \
  -H "Content-Type: application/json" \
  -d '{"pmc_id": "PMC2910419"}'
```

**Response:**
```json
{
  "pmc_id": "PMC2910419",
  "doi": "10.1152/jn.00378.2010",
  "found": true,
  "message": "DOI found successfully"
}
```

### GET /metadata/{doi}
Get metadata from Semantic Scholar by DOI

**Example:**
```bash
curl http://localhost:8001/metadata/10.1128/AEM.03065-09
```

**Response:**
```json
{
  "doi": "10.1128/AEM.03065-09",
  "found": true,
  "message": "Metadata retrieved successfully",
  "data": {
    "paperId": "e9e10a725bfe2329313d3254472ce65da5315ceb",
    "url": "https://www.semanticscholar.org/paper/...",
    "citationCount": 13,
    "influentialCitationCount": 0,
    "openAccessPdf": {
      "url": "https://...",
      "status": "GOLD",
      "license": "CCBYNCND"
    },
    "fieldsOfStudy": ["Medicine"],
    "journal": {
      "name": "Heliyon",
      "volume": "9"
    }
  }
}
```

**Note:** Rate limited to 1 request per second to comply with Semantic Scholar API limits.

## Local Development

### Environment Setup

1. **Copy the example environment file:**
```bash
cp .env.example .env
```

2. **Add your Semantic Scholar API key to `.env`:**
```env
SEMANTIC_SCHOLAR_API_KEY=your_api_key_here
```

Get your API key at: https://www.semanticscholar.org/product/api

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the API
```bash
uvicorn main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

### Test the API
```bash
# Test with GET
curl http://localhost:8001/doi/PMC2910419

# Test with POST
curl -X POST http://localhost:8001/doi \
  -H "Content-Type: application/json" \
  -d '{"pmc_id": "PMC2910419"}'

# Test metadata endpoint
curl http://localhost:8001/metadata/10.1128/AEM.03065-09
```

Or use the PowerShell test scripts:
```powershell
# Test production API
.\test_production.ps1

# Test metadata endpoint locally
.\test_metadata.ps1
```

## Deployment to Vercel

### 1. Install Vercel CLI (if not installed)
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Add Environment Variables
In Vercel dashboard or using CLI:
```bash
vercel env add SEMANTIC_SCHOLAR_API_KEY
```

Enter your Semantic Scholar API key when prompted.

### 4. Deploy
```bash
vercel --prod
```

## Project Structure

```
consultor/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel configuration
└── README.md           # This file
```

## Data Structure

Each DOI JSON file follows this structure:

```json
{
  "PMC": "PMC2910419",
  "DOI": "10.1152/jn.00378.2010"
}
```

## Error Handling

If a PMC ID is not found:

```json
{
  "pmc_id": "PMC999999999",
  "doi": null,
  "found": false,
  "message": "PMC PMC999999999 not found in database"
}
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## License

MIT

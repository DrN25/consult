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
Get metadata from Semantic Scholar by DOI or PMC ID

**Auto-converts PMC to DOI:** If you provide a PMC ID (with or without prefix), it will automatically be converted to DOI before fetching metadata.

**Examples:**
```bash
# With DOI
curl http://localhost:8001/metadata/10.1128/AEM.03065-09

# With PMC (auto-converts to DOI)
curl http://localhost:8001/metadata/PMC2897429
curl http://localhost:8001/metadata/2897429
```

**Response (with DOI):**
```json
{
  "doi": "10.1128/AEM.03065-09",
  "pmc_id": null,
  "found": true,
  "message": "Metadata retrieved successfully",
  "data": {
    "paperId": "12cc490c4209a8895ea377e30542112324f4c835",
    "url": "https://www.semanticscholar.org/paper/...",
    "citationCount": 171,
    "influentialCitationCount": 8,
    "openAccessPdf": {
      "url": "https://...",
      "status": "GREEN",
      "license": null
    },
    "fieldsOfStudy": ["Biology", "Medicine"],
    "journal": {
      "name": "Applied and Environmental Microbiology",
      "pages": "4136 - 4142",
      "volume": "76"
    }
  }
}
```

**Response (with PMC auto-conversion):**
```json
{
  "doi": "10.1128/AEM.03065-09",
  "pmc_id": "PMC2897429",
  "found": true,
  "message": "Metadata retrieved successfully (converted from PMC PMC2897429)",
  "data": { ... }
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

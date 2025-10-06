# PMC to DOI Lookup API

Simple FastAPI service to convert PMC IDs to DOI identifiers.

## Features

- ✅ Get DOI from PMC ID
- ✅ Supports both GET and POST methods
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

## Local Development

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

### 3. Deploy
```bash
vercel --prod
```

### 4. Copy DOI data files
Make sure the `data/doi/*.json` files are accessible in your deployment.

You may need to:
- Include them in the repository
- Or adjust the file path in `main.py` to point to your data source

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

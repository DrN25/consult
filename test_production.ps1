# Test script for production API
$BASE_URL = "https://consult-silk.vercel.app"

Write-Host "`n=== Testing Production API ===" -ForegroundColor Cyan

# Test 1: Root endpoint
Write-Host "`n1. Testing root endpoint..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "$BASE_URL/" -Method Get | ConvertTo-Json

# Test 2: Health check
Write-Host "`n2. Testing health check..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get | ConvertTo-Json

# Test 3: GET with PMC prefix
Write-Host "`n3. Testing GET /doi/PMC2910419..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "$BASE_URL/doi/PMC2910419" -Method Get | ConvertTo-Json

# Test 4: GET without PMC prefix
Write-Host "`n4. Testing GET /doi/10020673..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "$BASE_URL/doi/10020673" -Method Get | ConvertTo-Json

# Test 5: POST request
Write-Host "`n5. Testing POST /doi..." -ForegroundColor Yellow
$body = @{
    pmc_id = "PMC10025027"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$BASE_URL/doi" -Method Post -Body $body -ContentType "application/json" | ConvertTo-Json

# Test 6: Non-existent PMC
Write-Host "`n6. Testing non-existent PMC..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "$BASE_URL/doi/PMC9999999" -Method Get | ConvertTo-Json

Write-Host "`n=== Tests Completed ===" -ForegroundColor Green

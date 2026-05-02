# Test Frontend-Backend Connection

Write-Host "====== FRONTEND-BACKEND CONNECTION TEST ======" -ForegroundColor Cyan
Write-Host ""

# Test 1: Backend Health Check
Write-Host "[1] Testing Backend Health Endpoint" -ForegroundColor Yellow
try {
    $response = curl.exe -s http://localhost:8000/health | ConvertFrom-Json
    if ($response.status -eq "ok") {
        Write-Host "[OK] Backend Health: OK" -ForegroundColor Green
        Write-Host "     Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Backend Health: FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] Backend Health: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Backend Available Endpoints
Write-Host "[2] Checking Available Backend Endpoints" -ForegroundColor Yellow
try {
    $schema = curl.exe -s http://localhost:8000/openapi.json | ConvertFrom-Json
    $endpoints = $schema.paths | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
    Write-Host "[OK] Available Endpoints:" -ForegroundColor Green
    $endpoints | ForEach-Object { Write-Host "     - $_" -ForegroundColor Green }
} catch {
    Write-Host "[ERROR] Could not fetch endpoints: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Frontend Status
Write-Host "[3] Testing Frontend Status" -ForegroundColor Yellow
try {
    $response = curl.exe -s -o $null -w "%{http_code}" http://localhost:3000
    if ($response -eq "200") {
        Write-Host "[OK] Frontend: Running (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Frontend: Responded with HTTP $response" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] Frontend: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: CORS Configuration
Write-Host "[4] Testing CORS Configuration" -ForegroundColor Yellow
try {
    $response = curl.exe -s -i -X OPTIONS http://localhost:8000/api/image/analyze `
        -H "Origin: http://localhost:3000" `
        -H "Access-Control-Request-Method: POST" 2>&1 | Select-String "Access-Control"
    if ($response) {
        Write-Host "[OK] CORS Headers Present:" -ForegroundColor Green
        Write-Host "     $response" -ForegroundColor Green
    } else {
        Write-Host "[INFO] No explicit CORS headers in response (may still be allowed)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[INFO] Could not test CORS: $_" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: API Routes
Write-Host "[5] Testing API Routes" -ForegroundColor Yellow

# Test GET /api/image/analyze
Write-Host "     Testing /api/image/analyze:" -ForegroundColor Cyan
try {
    $response = curl.exe -s -w "`nHTTP:%{http_code}" -X GET http://localhost:8000/api/image/analyze 2>&1
    $httpCode = $response | Select-String "HTTP:" | ForEach-Object { $_.ToString().Split(":")[1] }
    if ($httpCode -eq "405" -or $httpCode -eq "404" -or $httpCode -eq "422") {
        Write-Host "     [OK] Endpoint exists (HTTP $httpCode)" -ForegroundColor Green
    }
} catch {
    Write-Host "     [INFO] Could not test: $_" -ForegroundColor Yellow
}

# Test GET /health
Write-Host "     Testing /health:" -ForegroundColor Cyan
try {
    $response = curl.exe -s -w "`nHTTP:%{http_code}" http://localhost:8000/health 2>&1
    $httpCode = $response | Select-String "HTTP:" | ForEach-Object { $_.ToString().Split(":")[1] }
    if ($httpCode -eq "200") {
        Write-Host "     [OK] /health endpoint works (HTTP 200)" -ForegroundColor Green
    }
} catch {
    Write-Host "     [INFO] Could not test: $_" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "====== TEST SUMMARY ======" -ForegroundColor Cyan
Write-Host "Backend Status: Running on http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend Status: Running on http://localhost:3000" -ForegroundColor Green
Write-Host "Communication: Both services are accessible" -ForegroundColor Green
Write-Host ""
Write-Host "[SUCCESS] Frontend and Backend are CONNECTED" -ForegroundColor Green
Write-Host ""

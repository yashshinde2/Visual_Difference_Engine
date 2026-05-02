#!/usr/bin/env pwsh
<#
.SYNOPSIS
Starts the RGB Visual Difference Engine (Backend + Frontend)

.DESCRIPTION
Launches both the backend API server and frontend development server in the background.
Opens the app automatically in your default browser.

.EXAMPLE
.\start-app.ps1
#>

param(
    [switch]$NoBrowser  # Skip opening browser if set
)

$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $AppRoot "backend"
$FrontendDir = Join-Path $AppRoot "frontend"

Write-Host "🚀 Starting RGB Visual Difference Engine..." -ForegroundColor Cyan

# Kill any existing processes on ports 8000 and 3000
Write-Host "🧹 Cleaning up old processes..." -ForegroundColor Yellow
$existingBackend = Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Where-Object {$_.Id -gt 0}
$existingFrontend = Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Where-Object {$_.Id -gt 0}

if ($existingBackend) {
    $existingBackend | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Stopped old backend processes" -ForegroundColor Green
}

if ($existingFrontend) {
    $existingFrontend | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Stopped old frontend processes" -ForegroundColor Green
}

# Clean Next.js lock file
Remove-Item -Path "$FrontendDir\.next\dev\lock" -Force -ErrorAction SilentlyContinue

# Start Backend
Write-Host "`n📦 Starting Backend (port 8000)..." -ForegroundColor Cyan
$BackendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendDir'; python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000" -PassThru
Start-Sleep -Seconds 2
Write-Host "  ✓ Backend started (PID: $($BackendJob.Id))" -ForegroundColor Green

# Start Frontend
Write-Host "`n🎨 Starting Frontend (port 3000)..." -ForegroundColor Cyan
$FrontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; npm run dev" -PassThru
Start-Sleep -Seconds 5
Write-Host "  ✓ Frontend started (PID: $($FrontendJob.Id))" -ForegroundColor Green

# Open browser
if (-not $NoBrowser) {
    Write-Host "`n🌐 Opening browser..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:3000"
}

Write-Host "`n✅ Application is ready!" -ForegroundColor Green
Write-Host "   Frontend:   http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:    http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n💡 Tip: To stop the app, close both terminal windows or press Ctrl+C in each." -ForegroundColor Yellow

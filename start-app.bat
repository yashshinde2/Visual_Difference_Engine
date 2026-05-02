@echo off
REM Start the RGB Visual Difference Engine
REM Double-click to run both backend and frontend servers

echo.
echo Starting RGB Visual Difference Engine...
echo.

REM Get the directory where this batch file is located
pushd "%~dp0"

REM Kill any old processes
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

REM Clean Next.js lock
if exist "frontend\.next\dev\lock" (
    del /F "frontend\.next\dev\lock" >nul 2>&1
)

REM Start backend in a new window
echo Starting Backend (port 8000)...
start "Backend - RGB Visual Difference Engine" cmd /k "cd backend && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak

REM Start frontend in a new window
echo Starting Frontend (port 3000)...
start "Frontend - RGB Visual Difference Engine" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak

REM Open browser
echo Opening http://localhost:3000 in browser...
start http://localhost:3000

echo.
echo ============================================
echo Application is starting!
echo.
echo Frontend:   http://localhost:3000
echo Backend:    http://localhost:8000
echo API Docs:   http://localhost:8000/docs
echo.
echo Keep both command windows open while using the app.
echo ============================================
echo.

popd

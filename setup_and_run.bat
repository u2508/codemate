@echo off
echo 🚀 AI Terminal Setup and Run Script
echo =================================

echo.
echo 📦 Setting up backend...
cd backend
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    
call .venv\Scripts\activate.bat
pip install fastapi uvicorn python-dotenv psutil
echo ✅ Backend setup complete!
) else (
    echo ✅ Backend virtual environment already exists
    call .venv\Scripts\activate.bat
)

echo.
echo 🌐 Setting up frontend...
cd ../frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
) else (
    echo ✅ Frontend dependencies already installed
)

echo.
echo 🎯 Starting servers...
echo.
echo Backend will start on: http://localhost:8000
echo Frontend will start on: http://localhost:3000
echo.
echo Press Ctrl+C to stop both servers
echo.

echo Starting backend server...
start cmd /k "cd backend && .venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo Starting frontend server...
start cmd /k "cd frontend && python -m http.server 3000"

echo.
echo Setup complete! Open http://localhost:3000 in your browser
echo.
pause

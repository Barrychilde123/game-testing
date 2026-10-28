@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=python"
where python >nul 2>&1
if errorlevel 1 set "PYTHON=py"
where %PYTHON% >nul 2>&1
if errorlevel 1 (
  echo Python not found. Please install Python first.
  pause
  exit /b 1
)

echo Starting 2048 game testing server...
echo URL: http://127.0.0.1:8001
echo.

start "Game Testing Server" cmd /k "%PYTHON% -m http.server 8001 --bind 127.0.0.1"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8001"
endlocal

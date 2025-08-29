@echo off
echo Testing StudyMate Backend...
echo.

echo Starting test server...
cd backend
python -m uvicorn test_server:app --host 0.0.0.0 --port 8000

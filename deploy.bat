@echo off
echo ========================================
echo         Deploy to Server
echo ========================================
echo.

git add .
git commit -m "auto deploy"
git push

echo.
echo Connecting to server...
echo.

ssh root@8.138.108.144 "cd /opt/license-service && [ ! -d venv ] && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && pkill -f uvicorn && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > /var/log/license-service.log 2>&1 &"

echo.
echo ========================================
echo         Deploy Complete!
echo ========================================
echo Access: http://8.138.108.144:8001/admin
echo Token: dev-token
echo ========================================
pause

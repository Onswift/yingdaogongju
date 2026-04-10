@echo off
chcp 65001 >nul
echo ========================================
echo         启动授权服务（热重载模式）
echo ========================================
echo.
echo 管理后台：http://localhost:8001/admin
echo API 文档：http://localhost:8001/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

set ADMIN_TOKEN=dev-token
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

pause

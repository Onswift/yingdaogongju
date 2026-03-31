  @echo off
  echo ========================================
  echo         一键部署到服务器
  echo ========================================
  echo.

  git add .
  git commit -m "auto deploy"
  git push

  if errorlevel 1 (
      echo.
      echo [错误] Git 推送失败
      pause
      exit /b 1
  )

  echo.
  echo [成功] 代码已推送
  echo.
  echo [正在部署] 连接服务器...
  echo.

  ssh root@8.138.108.144 "bash /opt/license-service/deploy.sh"

  echo.
  echo ========================================
  echo         部署完成！
  echo ========================================
  pause
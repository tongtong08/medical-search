@echo off
chcp 65001 >nul
echo ========================================
echo   医学知识检索系统 - 本地服务器
echo ========================================
echo.
echo 正在启动本地服务器...
echo.
echo 请在浏览器中访问:
echo   http://localhost:8080/医学知识检索.html
echo.
echo 按 Ctrl+C 可停止服务器
echo ========================================
echo.
start http://localhost:8080/医学知识检索.html
python -m http.server 8080
pause

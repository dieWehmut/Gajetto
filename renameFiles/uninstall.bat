@echo off
chcp 65001 >nul

REM 检查管理员权限,如果没有则自动请求提升
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 正在请求管理员权限...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

REM 获取脚本所在目录并切换到该目录
cd /d "%~dp0"

echo ====================================
echo 文件重命名工具 - 卸载程序
echo ====================================
echo.

echo [1/1] 删除右键菜单注册表项...
reg delete "HKEY_CLASSES_ROOT\*\shell\BatchRename" /f >nul 2>&1
reg delete "HKEY_CLASSES_ROOT\*\shell\RestoreRename" /f >nul 2>&1
echo.

echo ====================================
echo 卸载完成!
echo ====================================
echo.
echo 窗口将在 3 秒后自动关闭...
timeout /t 3 /nobreak >nul
exit /b 0

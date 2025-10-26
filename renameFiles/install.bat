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
echo 文件重命名工具 - 安装程序
echo ====================================
echo.
echo 当前目录: %CD%
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未检测到Python环境!
    echo 请先安装Python 3.x: https://www.python.org/downloads/
    echo.
    echo 窗口将在 5 秒后自动关闭...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
python --version
echo.

echo [2/4] 创建图标文件...
python "%~dp0create_icons.py"
if %errorLevel% neq 0 (
    echo [警告] 图标创建失败,将使用默认图标
)
echo.

echo [3/4] 获取Python路径...
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i
echo Python路径: %PYTHON_PATH%

REM 获取pythonw.exe路径
set PYTHONW_PATH=%PYTHON_PATH:python.exe=pythonw.exe%
echo Pythonw路径: %PYTHONW_PATH%

if not exist "%PYTHONW_PATH%" (
    echo [警告] 未找到pythonw.exe,使用python.exe
    set PYTHONW_PATH=%PYTHON_PATH%
)
echo.

echo [4/4] 注册右键菜单...
REM 创建批量重命名菜单 - 显示在新版右键菜单顶部
reg add "HKEY_CLASSES_ROOT\*\shell\BatchRename" /ve /d "批量重命名" /f >nul
reg add "HKEY_CLASSES_ROOT\*\shell\BatchRename" /v "Icon" /d "%~dp0batch_rename.ico" /f >nul
reg add "HKEY_CLASSES_ROOT\*\shell\BatchRename" /v "Position" /d "Top" /f >nul
reg add "HKEY_CLASSES_ROOT\*\shell\BatchRename\command" /ve /d "\"%PYTHONW_PATH%\" \"%~dp0rename_tool.py\" batch \"%%1\"" /f >nul

REM 创建恢复重命名菜单 - 显示在新版右键菜单顶部
reg add "HKEY_CLASSES_ROOT\*\shell\RestoreRename" /ve /d "恢复重命名" /f >nul
reg add "HKEY_CLASSES_ROOT\*\shell\RestoreRename" /v "Icon" /d "%~dp0restore_rename.ico" /f >nul
reg add "HKEY_CLASSES_ROOT\*\shell\RestoreRename" /v "Position" /d "Top" /f >nul
reg add "HKEY_CLASSES_ROOT\*\shell\RestoreRename\command" /ve /d "\"%PYTHONW_PATH%\" \"%~dp0rename_tool.py\" restore \"%%1\"" /f >nul

if %errorLevel% neq 0 (
    echo [错误] 注册表添加失败!
    echo.
    echo 窗口将在 5 秒后自动关闭...
    timeout /t 5 /nobreak >nul
    exit /b 1
)
echo.

echo ====================================
echo 安装完成!
echo ====================================
echo.
echo 现在你可以:
echo 1. 选择一个或多个文件
echo 2. 右键点击,选择"批量重命名"
echo 3. 或选择"恢复重命名"
echo.
echo 窗口将在 3 秒后自动关闭...
timeout /t 3 /nobreak >nul
exit /b 0

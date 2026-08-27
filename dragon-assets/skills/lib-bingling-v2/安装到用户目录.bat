@echo off
chcp 65001 >nul
echo ============================================
echo   lib-bingling-v2 安装脚本
echo ============================================
echo.
echo 正在复制技能文件到用户目录...
echo.

REM 获取用户目录
set USER_SKILLS=%USERPROFILE%\.claude\skills\lib-bingling-v2

REM 创建目录
if not exist "%USER_SKILLS%" mkdir "%USER_SKILLS%"

REM 复制所有文件
xcopy /E /Y /Q "%~dp0*.*" "%USER_SKILLS%\" >nul 2>&1

echo.
echo ============================================
echo   安装完成！
echo ============================================
echo.
echo 技能已安装到：
echo %USER_SKILLS%
echo.
echo 依赖安装：
pip install Pillow --quiet
echo.
echo 使用方法：
echo   python "%USER_SKILLS%\cli.py" list
echo   python "%USER_SKILLS%\illustration_pipeline.py"
echo.
echo 按任意键退出...
pause >nul

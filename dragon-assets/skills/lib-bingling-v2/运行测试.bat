@echo off
chcp 65001 >nul
echo ============================================
echo   lib-bingling-v2 测试脚本
echo ============================================
echo.
echo 正在安装依赖（如果需要）...
pip install Pillow --quiet
echo.
echo 开始生成封面图...
echo.
python "%~dp0测试脚本.py"
pause

@echo off
chcp 65001 >nul
echo ============================================
echo   lib-bingling-v2 Test
echo ============================================
echo.
echo Installing Pillow if needed...
pip install Pillow --quiet
echo.
echo Running test...
echo.
python "%~dp0test.py"
echo.
echo ============================================
echo   Test Complete!
echo ============================================
pause

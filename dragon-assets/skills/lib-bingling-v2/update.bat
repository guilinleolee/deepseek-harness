@echo off
chcp 65001 >nul
echo ============================================
echo   Update lib-bingling-v2
echo ============================================
echo.
echo Copying fixed files...
copy /Y "%~dp0test.py" "%USERPROFILE%\.claude\skills\lib-bingling-v2\test.py"
copy /Y "%~dp0test.bat" "%USERPROFILE%\.claude\skills\lib-bingling-v2\test.bat"
copy /Y "%~dp0generator_v2.py" "%USERPROFILE%\.claude\skills\lib-bingling-v2\generator_v2.py"
copy /Y "%~dp0cli.py" "%USERPROFILE%\.claude\skills\lib-bingling-v2\cli.py"
copy /Y "%~dp0illustrator_engine.py" "%USERPROFILE%\.claude\skills\lib-bingling-v2\illustrator_engine.py"
echo.
echo ============================================
echo   Update Complete!
echo ============================================
echo.
echo Press Enter to exit...
pause >nul

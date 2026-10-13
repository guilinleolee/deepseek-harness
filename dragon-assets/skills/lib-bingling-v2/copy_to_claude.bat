@echo off
chcp 65001 >nul
echo ============================================
echo   Copy lib-bingling-v2 to Claude skills
echo ============================================
echo.
set SRC=%~dp0
set DST=%USERPROFILE%\.claude\skills\lib-bingling-v2

echo Source: %SRC%
echo Dest: %DST%
echo.
if not exist "%DST%" mkdir "%DST%"
echo.
echo Copying files...
for %%f in (*.py *.bat *.md) do copy /Y "%SRC%%%f" "%DST%\%%f" 2>nul
for %%f in (*.bat) do copy /Y "%SRC%%%f" "%DST%\%%f" 2>nul
for %%d in (references) do (
    if not exist "%DST%\%%d" mkdir "%DST%\%%d"
    for %%f in ("%SRC%%%d\*.md") do copy /Y "%%f" "%DST%\%%d\"
)
echo.
echo ============================================
echo   Done!
echo ============================================
echo.
echo Press Enter to exit...
pause >nul

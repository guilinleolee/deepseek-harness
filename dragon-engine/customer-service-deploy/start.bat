@echo off
chcp 65001 > nul
setlocal

echo ============================================
echo  客服工作台 V0.1 · 一键启动脚本
echo ============================================
echo.

REM 启动 Docker Desktop
echo [1/5] 检查 Docker Desktop...
tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>NUL | find /I "Docker Desktop.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo   Docker Desktop 已在运行
) else (
    echo   启动 Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo   等待 30 秒...
    timeout /t 30 /nobreak > nul
)

REM 等待 daemon
echo.
echo [2/5] 等待 Docker daemon...
set RETRY=0
:wait_loop
docker info > nul 2>&1
if "%ERRORLEVEL%"=="0" goto daemon_ready
set /a RETRY+=1
if %RETRY% GEQ 12 (
    echo   ERROR: Docker daemon 未就绪
    pause
    exit /b 1
)
echo   等待中... (%RETRY%/12)
timeout /t 5 /nobreak > nul
goto wait_loop
:daemon_ready
echo   Docker daemon 已就绪

REM 切目录
echo.
echo [3/5] 进入部署目录...
cd /d "%~dp0"
echo   当前目录: %CD%

REM 复制 .env
echo.
echo [4/5] 准备 .env...
if not exist .env.example (
    echo   ERROR: .env.example 不存在
    pause
    exit /b 1
)
if exist .env (
    echo   .env 已存在
) else (
    copy .env.example .env > nul
    echo   .env 创建成功 - 请编辑填入 OPENAI_API_KEY
)

REM 选择 compose 命令
echo.
echo [5/5] 启动所有服务（首次约 5-10 分钟）...
docker compose version > nul 2>&1
if "%ERRORLEVEL%"=="0" (
    set CMD=docker compose
) else (
    set CMD=docker-compose
)
echo   使用: %CMD%

%CMD% up -d

echo.
echo ============================================
echo  启动完成
echo ============================================
echo 状态: %CMD% ps
echo 日志: %CMD% logs -f backend
echo 健康: curl http://localhost:8080/health
echo.
pause

@echo off
REM deploy_daily.bat · 配套 deploy_daily.ps1 的双击运行器
REM
REM 用法：
REM   1. 双击运行
REM   2. 或任务计划程序调用本 bat（bat 会调 ps1）
REM
REM 日志：logs\deploy-daily-YYYYMMDD.log

setlocal

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%deploy_daily.ps1"

REM 检查 PowerShell 是否可用
where powershell >nul 2>&1
if errorlevel 1 (
    echo ❌ PowerShell 未找到
    pause
    exit /b 3
)

REM 跑 PS1（绕过 ExecutionPolicy）
powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%"

REM 退出码透传
exit /b %errorlevel%

@echo off
REM NeuroArxiv CLI - arXiv Prior Art检查工具
REM 使用方式: neuroxiv.bat "你的问题" [选项]

cd /d "%~dp0"
node cli.js %*

@echo off
setlocal
title Reparation du support BW16 pour PlatformIO
echo Le projet s'installe automatiquement au premier Build.
echo Cet outil sert uniquement a reparer une ancienne installation incomplete.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if errorlevel 1 (
    echo.
    echo L'installation a echoue. Lis le message ci-dessus.
    pause
    exit /b 1
)
echo.
echo Reparation terminee. Tu peux redemarrer VS Code et lancer Build.
pause

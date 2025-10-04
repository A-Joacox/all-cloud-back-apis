@echo off
echo ===============================================
echo   SISTEMA DE INGESTA A S3 - AWS ACADEMY
echo ===============================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo 💡 Instala Python desde https://python.org
    pause
    exit /b 1
)

REM Verificar si el script principal existe
if not exist "run-all-ingesta.py" (
    echo ❌ Script principal no encontrado: run-all-ingesta.py
    pause
    exit /b 1
)

REM Ejecutar el script principal
echo 🚀 Iniciando sistema de ingesta...
echo.
python run-all-ingesta.py %*

REM Verificar si hubo errores
if errorlevel 1 (
    echo.
    echo ❌ El script terminó con errores
    echo 💡 Revisa los mensajes de error arriba
) else (
    echo.
    echo ✅ Script ejecutado exitosamente
)

echo.
pause
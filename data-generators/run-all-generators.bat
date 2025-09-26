@echo off
echo 🚀 Iniciando generación de datos para microservicios de cine...
echo ================================================================

REM Verificar que las dependencias estén instaladas
echo 📦 Verificando dependencias...

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js no está instalado
    pause
    exit /b 1
)

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    pause
    exit /b 1
)

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no está instalado
    pause
    exit /b 1
)

echo ✅ Dependencias verificadas

REM Instalar dependencias de Node.js
echo 📦 Instalando dependencias de Node.js...
npm install

REM Instalar dependencias de Python
echo 📦 Instalando dependencias de Python...
pip install -r requirements.txt

echo.
echo 🗄️  Generando datos para MongoDB...
echo ==================================
node mongodb-data-generator.js

echo.
echo 🗄️  Generando datos para MySQL...
echo ================================
python mysql-data-generator.py

echo.
echo 🗄️  Generando datos para PostgreSQL...
echo =====================================
python postgresql-data-generator.py

echo.
echo 🔍 Verificando datos generados...
echo ================================
node verify-data.js

echo.
echo ✅ ¡Generación de datos completada!
echo ==================================
echo Total de registros generados:
echo - MongoDB: ~8,000 películas + 22 géneros
echo - MySQL: ~100 salas + ~15,000 asientos + 12,000 horarios
echo - PostgreSQL: ~2,000 usuarios + 15,000 reservas + 15,000 pagos
echo.
echo 🎯 Total aproximado: 20,000+ registros
pause
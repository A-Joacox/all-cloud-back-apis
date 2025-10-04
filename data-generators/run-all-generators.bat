@echo off
echo 🎬 GENERADOR DE DATOS - MICROSERVICIOS DE CINE
echo ============================================
echo.

REM Verificar que las dependencias estén instaladas
echo � Verificando requisitos del sistema...

REM Verificar Docker (recomendado)
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker no está instalado (recomendado para bases de datos)
    echo 💡 Puedes instalarlo desde https://docker.com
) else (
    echo ✅ Docker disponible
    echo.
    echo 🐳 ¿Quieres iniciar las bases de datos con Docker? (recomendado)
    echo    Esto iniciará MongoDB, MySQL y PostgreSQL automáticamente
    set /p docker_choice="Escribir 's' para usar Docker, o Enter para continuar: "
    
    if /i "!docker_choice!"=="s" (
        echo.
        echo 🚀 Iniciando bases de datos con Docker...
        cd ..
        docker-compose up -d mongodb mysql postgresql
        cd data-generators
        echo ✅ Bases de datos iniciadas
        timeout /t 10 /nobreak >nul
        echo.
    )
)

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js no está instalado
    echo 💡 Instala Node.js desde https://nodejs.org
    pause
    exit /b 1
) else (
    echo ✅ Node.js disponible
)

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado  
    echo 💡 Instala Python desde https://python.org
    pause
    exit /b 1
) else (
    echo ✅ Python disponible
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
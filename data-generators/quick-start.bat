@echo off
echo 🚀 INICIO RÁPIDO - SISTEMA DE CINE
echo ==================================
echo.
echo Este script va a:
echo 1. 🐳 Iniciar bases de datos con Docker
echo 2. ⏳ Esperar a que estén listas
echo 3. 📊 Generar datos de prueba
echo 4. ✅ Verificar que todo funcione
echo.

set /p confirm="¿Continuar? (s/N): "
if /i not "%confirm%"=="s" (
    echo Operación cancelada
    pause
    exit /b 0
)

echo.
echo 📍 Paso 1: Iniciando bases de datos...
cd ..
docker-compose up -d mongodb mysql postgresql

echo.
echo ⏳ Paso 2: Esperando a que las bases de datos estén listas...
echo    (Esto puede tomar 30-60 segundos)
timeout /t 30 /nobreak >nul

echo.
echo 📊 Paso 3: Generando datos de prueba...
cd data-generators
call run-all-generators.bat

echo.
echo 🎉 ¡SISTEMA LISTO!
echo ================
echo.
echo 🌐 Puedes probar las APIs en:
echo   • Movies API:    http://localhost:3001/api/movies
echo   • Rooms API:     http://localhost:3002/api/rooms  
echo   • Reservations:  http://localhost:3003/api/reservations
echo   • Gateway API:   http://localhost:3004
echo   • Analytics:     http://localhost:3005/api/analytics
echo.
echo 🛑 Para detener: docker-compose down
echo.
pause
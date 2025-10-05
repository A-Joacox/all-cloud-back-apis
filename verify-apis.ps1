# Verificación rápida de APIs y Swagger UI
# Ejecuta este script para verificar que todas las APIs estén funcionando

Write-Host "🔍 Verificando APIs del Sistema de Cine..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Lista de APIs y sus puertos
$apis = @{
    "Movies" = 3001
    "Rooms" = 3002
    "Reservations" = 3003
    "Gateway" = 3004
    "Analytics" = 3005
}

Write-Host ""
Write-Host "📋 Verificando Health Checks..." -ForegroundColor Yellow

foreach ($api in $apis.GetEnumerator()) {
    $name = $api.Key
    $port = $api.Value
    
    Write-Host "  ➤ $name API (puerto $port): " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port/health" -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ OK" -ForegroundColor Green
        } else {
            Write-Host "❌ Error HTTP $($response.StatusCode)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ No disponible" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📚 URLs de Documentación Swagger UI:" -ForegroundColor Yellow
Write-Host "======================================"
foreach ($api in $apis.GetEnumerator()) {
    $name = $api.Key
    $port = $api.Value
    Write-Host "  ➤ $name API: " -NoNewline
    Write-Host "http://localhost:$port/docs" -ForegroundColor Blue
}

Write-Host ""
Write-Host "🚀 Comandos para iniciar cada API:" -ForegroundColor Yellow
Write-Host "=================================="
Write-Host "  ➤ Movies API:       " -NoNewline; Write-Host "cd movies-api; npm run dev" -ForegroundColor Green
Write-Host "  ➤ Rooms API:        " -NoNewline; Write-Host "cd rooms-api; python app.py" -ForegroundColor Green
Write-Host "  ➤ Reservations API: " -NoNewline; Write-Host "cd reservations-api; ./mvnw spring-boot:run" -ForegroundColor Green
Write-Host "  ➤ Gateway API:      " -NoNewline; Write-Host "cd gateway-api; npm start" -ForegroundColor Green
Write-Host "  ➤ Analytics API:    " -NoNewline; Write-Host "cd analytics-api; npm start" -ForegroundColor Green

Write-Host ""
Write-Host "📦 O usar Docker Compose:" -ForegroundColor Yellow
Write-Host "========================"
Write-Host "  ➤ " -NoNewline; Write-Host "docker-compose up -d" -ForegroundColor Green

Write-Host ""
Write-Host "✨ ¡Todas las APIs incluyen documentación Swagger UI completa!" -ForegroundColor Magenta
Write-Host "   Navega a http://localhost:[PUERTO]/docs para explorar cada API" -ForegroundColor White
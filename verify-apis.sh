#!/bin/bash
# Verificación rápida de APIs y Swagger UI
# Ejecuta este script para verificar que todas las APIs estén funcionando

echo "🔍 Verificando APIs del Sistema de Cine..."
echo "========================================="

# Lista de APIs y sus puertos
declare -a apis=(
    "Movies:3001"
    "Rooms:3002" 
    "Reservations:3003"
    "Gateway:3004"
    "Analytics:3005"
)

echo ""
echo "📋 Verificando Health Checks..."
for api in "${apis[@]}"
do
    IFS=':' read -ra ADDR <<< "$api"
    name="${ADDR[0]}"
    port="${ADDR[1]}"
    
    echo -n "  ➤ $name API (puerto $port): "
    
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ No disponible"
    fi
done

echo ""
echo "📚 URLs de Documentación Swagger UI:"
echo "======================================"
for api in "${apis[@]}"
do
    IFS=':' read -ra ADDR <<< "$api"
    name="${ADDR[0]}"
    port="${ADDR[1]}"
    
    echo "  ➤ $name API: http://localhost:$port/docs"
done

echo ""
echo "🚀 Comandos para iniciar cada API:"
echo "=================================="
echo "  ➤ Movies API:       cd movies-api && npm run dev"
echo "  ➤ Rooms API:        cd rooms-api && python app.py" 
echo "  ➤ Reservations API: cd reservations-api && ./mvnw spring-boot:run"
echo "  ➤ Gateway API:      cd gateway-api && npm start"
echo "  ➤ Analytics API:    cd analytics-api && npm start"

echo ""
echo "📦 O usar Docker Compose:"
echo "========================"
echo "  ➤ docker-compose up -d"

echo ""
echo "✨ ¡Todas las APIs incluyen documentación Swagger UI completa!"
echo "   Navega a http://localhost:[PUERTO]/docs para explorar cada API"
#!/bin/bash

echo "🚀 Iniciando generación de datos para microservicios de cine..."
echo "================================================================"

# Verificar que las dependencias estén instaladas
echo "📦 Verificando dependencias..."

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado"
    exit 1
fi

echo "✅ Dependencias verificadas"

# Instalar dependencias de Node.js
echo "📦 Instalando dependencias de Node.js..."
npm install

# Instalar dependencias de Python
echo "📦 Instalando dependencias de Python..."
pip3 install -r requirements.txt

echo ""
echo "🗄️  Generando datos para MongoDB..."
echo "=================================="
node mongodb-data-generator.js

echo ""
echo "🗄️  Generando datos para MySQL..."
echo "================================"
python3 mysql-data-generator.py

echo ""
echo "🗄️  Generando datos para PostgreSQL..."
echo "====================================="
python3 postgresql-data-generator.py

echo ""
echo "🔍 Verificando datos generados..."
echo "================================"
node verify-data.js

echo ""
echo "✅ ¡Generación de datos completada!"
echo "=================================="
echo "Total de registros generados:"
echo "- MongoDB: ~8,000 películas + 22 géneros"
echo "- MySQL: ~100 salas + ~15,000 asientos + 12,000 horarios"
echo "- PostgreSQL: ~2,000 usuarios + 15,000 reservas + 15,000 pagos"
echo ""
echo "🎯 Total aproximado: 20,000+ registros"
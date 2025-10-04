#!/bin/bash

echo "==============================================="
echo "   SISTEMA DE INGESTA A S3 - AWS ACADEMY"
echo "==============================================="
echo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    echo "💡 Instala Python3: sudo apt-get install python3"
    exit 1
fi

# Verificar si el script principal existe
if [ ! -f "run-all-ingesta.py" ]; then
    echo "❌ Script principal no encontrado: run-all-ingesta.py"
    exit 1
fi

# Ejecutar el script principal
python3 run-all-ingesta.py "$@"

echo
read -p "Presiona Enter para continuar..."
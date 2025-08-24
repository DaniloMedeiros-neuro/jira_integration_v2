#!/bin/bash

# Script para iniciar o servidor Flask
echo "🚀 Iniciando servidor Flask..."

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se a porta 8081 está em uso
if lsof -Pi :8081 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Porta 8081 já está em uso. Parando processo anterior..."
    pkill -f "python.*app.py"
    sleep 2
fi

# Iniciar servidor
echo "✅ Iniciando servidor na porta 8081..."
python app.py

echo "❌ Servidor parou. Reiniciando em 5 segundos..."
sleep 5
exec "$0"

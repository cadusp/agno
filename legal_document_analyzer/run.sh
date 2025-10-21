#!/bin/bash

# Script de inicialização do Legal Document Analyzer

echo "🚀 Iniciando Legal Document Analyzer..."
echo ""

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8 ou superior."
    exit 1
fi

# Verifica se as dependências estão instaladas
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
    echo ""
fi

# Executa a aplicação
echo "✅ Iniciando aplicação Streamlit..."
echo ""
echo "A aplicação será aberta no seu navegador em alguns segundos..."
echo "Se não abrir automaticamente, acesse: http://localhost:8501"
echo ""
echo "Para parar a aplicação, pressione Ctrl+C"
echo ""

streamlit run app.py

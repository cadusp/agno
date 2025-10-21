# ⚡ Quick Start - Executive Board Analyzer

## 🚀 Execução em 3 Passos

### 1. Instalar dependências
```bash
pip install agno streamlit openai chromadb
```

### 2. Executar o sistema
```bash
cd legal_document_analyzer
streamlit run executive_board_analyzer.py
```

### 3. Configurar e usar
1. Abra http://localhost:8501
2. Cole sua chave OpenAI na barra lateral
3. Selecione os executivos na aba "Mesa Executiva"
4. Carregue seu documento
5. Clique em "Iniciar Análise"

---

## 📋 Exemplo Rápido

### Cenário: Análise de Política de Privacidade

**Mesa:** CEO + Legal + DPO + CMO

**Documento:** Política de Privacidade da empresa

**Rodadas:** 2

**Resultado:**
- CEO: Avalia clareza para stakeholders
- Legal: Verifica conformidade legal
- DPO: Analisa LGPD em detalhes
- CMO: Avalia comunicação com clientes

**Debate:** DPO vs CMO sobre linguagem técnica vs acessível
**Consenso:** Criar versão simplificada + versão completa

---

## 🎯 Combinações de Mesa Recomendadas

| Tipo de Documento | Mesa Recomendada |
|-------------------|------------------|
| **Contrato** | CEO + CFO + Legal + DPO |
| **Política Interna** | CHRO + Legal + CCO + DPO |
| **Projeto Técnico** | CTO + CISO + CFO + COO |
| **Estratégia** | CEO + CFO + CMO + COO |
| **Compliance** | CCO + Legal + DPO + CISO |
| **RH** | CHRO + Legal + COO + CEO |
| **Marketing** | CMO + Legal + DPO + CCO |

---

## 💡 Dicas de Uso

✅ **Use gpt-4o-mini** para análises rápidas (~$0.05 por análise)

✅ **3 rodadas** é ideal para maioria dos casos

✅ **Responda às perguntas** da mesa entre rodadas para melhor resultado

✅ **Habilite RAG** se estiver analisando múltiplos documentos relacionados

✅ **Baixe o relatório final** para documentação e governança

---

## 🆘 Problemas Comuns

**"Erro ao inicializar agentes"**
→ Verifique se a chave OpenAI está correta

**"Análise muito lenta"**
→ Use menos agentes ou gpt-4o-mini

**"Perguntas não claras"**
→ Adicione mais contexto no campo "contexto adicional"

---

**Pronto para começar!** 🎉

Execute `streamlit run executive_board_analyzer.py` e explore o poder da análise multidisciplinar com IA.

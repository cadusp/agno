# 🔧 Instalação do AutoGen Team Builder

## Guia de Instalação Corrigido

### 1. Criar Ambiente Virtual (Recomendado)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar Dependências

**Opção A: Instalação Completa (Recomendada)**

```bash
cd legal_document_analyzer
pip install -r requirements_autogen.txt
```

**Opção B: Instalação Manual por Etapas**

Se encontrar erros, instale em etapas:

```bash
# 1. Core AutoGen
pip install pyautogen

# 2. Streamlit
pip install streamlit

# 3. OpenAI
pip install openai

# 4. LangChain (IMPORTANTE: ordem correta)
pip install langchain-core
pip install langchain-text-splitters
pip install langchain-community
pip install langchain-openai
pip install langchain

# 5. Vector Store
pip install chromadb

# 6. Document Processing
pip install pypdf
pip install docx2txt
pip install unstructured

# 7. Utilities
pip install tiktoken
pip install python-dotenv
```

### 3. Verificar Instalação

```python
# Teste rápido
python -c "
import autogen
import streamlit
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
print('✅ Todas as dependências instaladas com sucesso!')
"
```

### 4. Executar a Aplicação

```bash
streamlit run autogen_team_builder.py
```

---

## 🔍 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'langchain.text_splitter'"

**Solução:**
```bash
# Instalar o novo pacote correto
pip install langchain-text-splitters
```

### Erro: "ModuleNotFoundError: No module named 'langchain_openai'"

**Solução:**
```bash
pip install langchain-openai
```

### Erro: "ModuleNotFoundError: No module named 'langchain_core'"

**Solução:**
```bash
pip install langchain-core
```

### Erro com ChromaDB

**Solução:**
```bash
# Reinstalar ChromaDB
pip uninstall chromadb -y
pip install chromadb --upgrade
```

### Erro com PyPDF

**Solução:**
```bash
# Usar pypdf ao invés de PyPDF2
pip install pypdf
```

---

## 📦 Versões Testadas

Estas versões foram testadas e funcionam:

```
pyautogen==0.2.18
streamlit==1.31.0
openai==1.12.0
langchain==0.1.9
langchain-community==0.0.24
langchain-openai==0.0.6
langchain-text-splitters==0.0.1
langchain-core==0.1.23
chromadb==0.4.24
pypdf==4.0.1
docx2txt==0.8
tiktoken==0.6.0
```

---

## 🐍 Versões Python Suportadas

- Python 3.9
- Python 3.10
- Python 3.11 ✅ Recomendado
- Python 3.12 (pode ter incompatibilidades com alguns pacotes)

---

## 💡 Dicas

### Performance

Para melhor performance, instale com:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements_autogen.txt
```

### Conflitos de Dependências

Se houver conflitos:
```bash
# Limpar cache
pip cache purge

# Reinstalar tudo
pip uninstall -r requirements_autogen.txt -y
pip install -r requirements_autogen.txt --no-cache-dir
```

### Ambiente Limpo

Para começar do zero:
```bash
# Desativar ambiente
deactivate

# Deletar ambiente
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows

# Recriar
python -m venv .venv
# ... ativar e reinstalar
```

---

## ✅ Checklist de Instalação

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] requirements_autogen.txt instalado
- [ ] Teste de imports bem-sucedido
- [ ] Streamlit executa sem erros
- [ ] OpenAI API key disponível

---

## 🚀 Próximos Passos

Após instalação bem-sucedida:

1. Execute: `streamlit run autogen_team_builder.py`
2. Configure sua OpenAI API key
3. Crie ou use templates de agentes
4. Comece a usar! 🎉

---

**Atualizado:** 2025-01-21
**Versão:** 4.0 - AutoGen Edition

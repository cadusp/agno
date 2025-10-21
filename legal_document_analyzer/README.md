# ⚖️ Legal Document Analyzer

Sistema inteligente de análise de documentos jurídicos usando múltiplos agentes de IA especializados, construído com Agno e Streamlit.

## 📋 Descrição

O Legal Document Analyzer é uma aplicação completa que utiliza um time de agentes de IA especializados para realizar análises multidimensionais de documentos jurídicos, contratos, políticas corporativas e outros documentos legais.

### 🤖 Time de Especialistas

O sistema conta com 5 agentes especializados:

1. **👔 Analista de Contratos**
   - Revisão detalhada de cláusulas contratuais
   - Identificação de obrigações e direitos das partes
   - Análise de prazos e condições
   - Identificação de riscos contratuais

2. **✅ Agente de Conformidade**
   - Verificação de conformidade com LGPD
   - Análise de adequação ao Código de Defesa do Consumidor
   - Verificação de legislação trabalhista
   - Análise de normas setoriais

3. **📋 Analista de Políticas**
   - Avaliação de clareza e objetividade
   - Comparação com melhores práticas
   - Análise de consistência interna
   - Sugestões de melhorias

4. **⚠️ Analista de Riscos Jurídicos**
   - Identificação de riscos legais, financeiros e reputacionais
   - Classificação de riscos por severidade
   - Avaliação de probabilidade e impacto
   - Estratégias de mitigação

5. **📊 Especialista em Resumos Executivos**
   - Síntese de análises complexas
   - Destaque de pontos-chave
   - Recomendações acionáveis
   - Comunicação executiva clara

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Chave API da OpenAI

### Passos de Instalação

1. Clone o repositório ou navegue até o diretório:
```bash
cd legal_document_analyzer
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app.py
```

## 🎯 Como Usar

### Primeira Configuração

1. **Configure sua chave API OpenAI**
   - Na barra lateral, clique na seção "🔑 Chave API OpenAI"
   - Cole sua chave API da OpenAI
   - Clique em "💾 Salvar Chave"
   - A chave será salva localmente em `~/.legal_document_analyzer/config.json`

2. **Escolha o modelo OpenAI**
   - Selecione entre: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`
   - Recomendado: `gpt-4o-mini` para análises rápidas e econômicas
   - Use `gpt-4o` para análises mais profundas e complexas

### Realizando uma Análise

1. **Carregue o documento**
   - Faça upload de um arquivo (TXT, MD, PDF), OU
   - Cole o texto diretamente na área de texto

2. **Selecione o tipo de análise**
   - **Análise Completa**: Todos os especialistas avaliam
   - **Análise de Contrato**: Foco em cláusulas contratuais
   - **Verificação de Conformidade**: Análise regulatória
   - **Análise de Política**: Avaliação de políticas corporativas
   - **Identificação de Riscos**: Mapeamento de riscos
   - **Resumo Executivo**: Síntese executiva

3. **Adicione instruções adicionais (opcional)**
   - Especifique aspectos específicos para focar
   - Exemplo: "Verifique conformidade com LGPD"

4. **Inicie a análise**
   - Clique em "🔍 Iniciar Análise"
   - Aguarde enquanto os agentes trabalham
   - Visualize os resultados detalhados

### Recursos Avançados

#### RAG (Retrieval-Augmented Generation)

Habilite o RAG para:
- Indexar documentos carregados
- Permitir que agentes usem documentos como contexto
- Realizar análises mais precisas e contextualizadas
- Comparar múltiplos documentos

**Como usar:**
1. Marque a opção "Habilitar RAG" na barra lateral
2. Carregue seus documentos
3. Os documentos serão automaticamente indexados
4. Os agentes usarão o contexto dos documentos nas análises

## 📁 Estrutura do Projeto

```
legal_document_analyzer/
├── app.py              # Interface Streamlit principal
├── agents.py           # Definição do time de agentes
├── config.py           # Gerenciamento de configurações e API key
├── requirements.txt    # Dependências do projeto
├── README.md          # Documentação
└── chroma_db/         # Banco de dados vetorial (criado automaticamente)
```

## 🔧 Configuração Técnica

### Modelos OpenAI

O sistema suporta os seguintes modelos:
- `gpt-4o-mini` - Rápido e econômico (recomendado para a maioria dos casos)
- `gpt-4o` - Modelo mais avançado para análises complexas
- `gpt-4-turbo` - Alto desempenho
- `gpt-3.5-turbo` - Opção econômica

### Embeddings

Para RAG, o sistema usa:
- Modelo: `text-embedding-3-small`
- Dimensões: 1536
- Provider: OpenAI

### Banco de Dados Vetorial

- Sistema: ChromaDB
- Collection: `legal_documents`
- Persistência: Diretório `./chroma_db`

## 💡 Exemplos de Uso

### Exemplo 1: Análise de Contrato de Prestação de Serviços

```
Tipo de Análise: Análise Completa
Instruções Adicionais: Foque nas cláusulas de rescisão e nas obrigações de confidencialidade
```

**Resultado esperado:**
- Análise detalhada de todas as cláusulas
- Identificação de riscos contratuais
- Verificação de conformidade legal
- Avaliação das condições de rescisão
- Resumo executivo com recomendações

### Exemplo 2: Verificação de Política de Privacidade

```
Tipo de Análise: Verificação de Conformidade
Instruções Adicionais: Verifique conformidade com a LGPD e identifique gaps
```

**Resultado esperado:**
- Análise de conformidade com LGPD
- Identificação de requisitos faltantes
- Sugestões de ajustes necessários
- Avaliação de riscos de não conformidade

### Exemplo 3: Revisão de Política Interna

```
Tipo de Análise: Análise de Política
Instruções Adicionais: Compare com melhores práticas de mercado
```

**Resultado esperado:**
- Avaliação de clareza e objetividade
- Comparação com benchmarks de mercado
- Sugestões de melhorias
- Recomendações de implementação

## 🔐 Segurança e Privacidade

### Armazenamento da Chave API

- A chave API é armazenada localmente em: `~/.legal_document_analyzer/config.json`
- O arquivo é criado com permissões restritas
- A chave nunca é enviada para servidores além da OpenAI
- Você pode remover a chave a qualquer momento

### Processamento de Documentos

- Documentos são processados apenas durante a sessão ativa
- Com RAG habilitado, embeddings são armazenados localmente em `./chroma_db`
- Nenhum documento é enviado para servidores externos além da API da OpenAI
- O histórico de análises é mantido apenas na sessão do navegador

## 📊 Custo Estimado

Os custos variam de acordo com o modelo escolhido:

| Modelo | Input (por 1M tokens) | Output (por 1M tokens) | Análise típica* |
|--------|----------------------|------------------------|-----------------|
| gpt-4o-mini | $0.15 | $0.60 | ~$0.01 - $0.05 |
| gpt-4o | $2.50 | $10.00 | ~$0.10 - $0.50 |
| gpt-4-turbo | $10.00 | $30.00 | ~$0.40 - $2.00 |

*Estimativa para um documento de 5 páginas com análise completa

## 🛠️ Troubleshooting

### Erro: "Chave API inválida"
- Verifique se a chave foi copiada corretamente
- Confirme que a chave está ativa na sua conta OpenAI
- Tente remover e adicionar a chave novamente

### Erro: "Modelo não encontrado"
- Verifique se sua conta OpenAI tem acesso ao modelo selecionado
- Alguns modelos requerem acesso especial (ex: GPT-4)
- Tente usar `gpt-4o-mini` como alternativa

### Análise muito lenta
- Use `gpt-4o-mini` para análises mais rápidas
- Desabilite RAG se não for necessário
- Reduza o tamanho do documento ou divida em partes menores

### ChromaDB não inicializa
- Verifique permissões de escrita no diretório
- Delete a pasta `chroma_db` e tente novamente
- Instale novamente o ChromaDB: `pip install --upgrade chromadb`

## 🤝 Contribuindo

Sugestões de melhorias:

1. **Novos Especialistas**: Adicione agentes especializados em outras áreas
2. **Suporte a mais formatos**: PDF com OCR, DOCX, etc.
3. **Exportação de relatórios**: PDF, DOCX, HTML
4. **Comparação de documentos**: Análise diff entre versões
5. **Modelos locais**: Suporte a modelos open-source via Ollama

## 📝 Licença

Este projeto usa o framework Agno. Consulte a licença do Agno para mais detalhes.

## 🙏 Agradecimentos

- [Agno Framework](https://github.com/agno-framework/agno) - Framework de agentes de IA
- [Streamlit](https://streamlit.io/) - Framework de interface web
- [OpenAI](https://openai.com/) - Modelos de linguagem e embeddings
- [ChromaDB](https://www.trychroma.com/) - Banco de dados vetorial

## 📞 Suporte

Para questões sobre:
- **Agno**: Consulte a [documentação oficial](https://docs.agno.com)
- **OpenAI**: Visite o [help center](https://help.openai.com)
- **Esta aplicação**: Abra uma issue no repositório

---

**Desenvolvido com ❤️ usando Agno**

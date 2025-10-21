# 🚀 Dynamic Team Builder

## Sistema Completo de Criação e Gestão de Times de Agentes IA

### 🌟 Visão Geral

O **Dynamic Team Builder** é a versão mais completa e avançada do sistema de agentes multidisciplinares. Permite criar agentes customizados, gerenciar bases de conhecimento, configurar fluxos dinâmicos e tanto **criar documentos do zero** quanto **analisar documentos existentes**.

---

## ✨ Funcionalidades Completas

### 👥 CRUD de Agentes
✅ **Criar** agentes personalizados com instruções específicas
✅ **Editar** agentes existentes (nome, role, instruções, modelo)
✅ **Deletar** agentes que não são mais necessários
✅ **Listar** todos os agentes criados

### 📚 Gestão de Base de Conhecimento
✅ **Upload** de múltiplos formatos (PDF, Markdown, TXT, DOCX, CSV)
✅ **Delete** de documentos da base
✅ **Conhecimento Global** - acessível a todos agentes
✅ **Conhecimento por Agente** - especialização individual

### 🔧 Chunking Strategies
✅ **Fixed Size** - Chunks de tamanho fixo
✅ **Semantic** - Chunks por significado semântico
✅ **Agentic** - IA decide os chunks
✅ **Document** - Documento completo sem divisão

### 💾 Persistência Completa
✅ **SQLite** - Armazena agentes, sessões, mensagens
✅ **LanceDB** - Armazena vetores e embeddings
✅ **Memória** - Agentes lembram conversas anteriores
✅ **Sessões** - Histórico completo de trabalho

### 🎯 Fluxo Dinâmico
✅ **Configurável** - Defina número de rodadas
✅ **Iterativo** - Múltiplas passadas de refinamento
✅ **Feedback entre rodadas** - Usuário pode intervir
✅ **Todos veem tudo** - Análises compartilhadas entre agentes

### 📝 Modos de Trabalho
✅ **Criar Documento** - Gera documentos do zero
✅ **Analisar Documento** - Avalia documentos existentes

### 🌊 Streaming e Output
✅ **Streaming em tempo real** - Veja respostas sendo geradas
✅ **Saída em Markdown** - Formatação profissional
✅ **Download** - Exporte resultados finais

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────┐
│          Dynamic Team Builder               │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Config       │  │ AgentManager │        │
│  │ - API Key    │  │ - CRUD       │        │
│  │ - Paths      │  │ - SQLite     │        │
│  └──────────────┘  └──────────────┘        │
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Knowledge    │  │ Session      │        │
│  │ Manager      │  │ Manager      │        │
│  │ - Docs       │  │ - History    │        │
│  │ - LanceDB    │  │ - Messages   │        │
│  └──────────────┘  └──────────────┘        │
│                                             │
│  ┌────────────────────────────────┐        │
│  │   Dynamic Team Creator         │        │
│  │   - Agents + Knowledge + Memory│        │
│  └────────────────────────────────┘        │
│                                             │
│  ┌────────────────────────────────┐        │
│  │   Streamlit Interface          │        │
│  │   - 5 Tabs (Agentes, Knowledge,│        │
│  │     Time, Executar, Ajuda)     │        │
│  └────────────────────────────────┘        │
└─────────────────────────────────────────────┘
```

### Estrutura de Dados (SQLite)

```sql
-- Agentes
agents (
  id, name, role, emoji, instructions,
  model_id, created_at, updated_at, metadata
)

-- Documentos de Conhecimento
knowledge_docs (
  id, name, content, file_type, agent_id,
  created_at, metadata
)

-- Sessões de Trabalho
sessions (
  id, name, mode, created_at, updated_at, metadata
)

-- Mensagens/Rodadas
messages (
  id, session_id, round_number, agent_ids,
  prompt, response, created_at
)
```

### Armazenamento de Vetores (LanceDB)

```
~/.dynamic_team_builder/lancedb/
├── knowledge_agent_xxx/  (tabela por agente)
├── knowledge_agent_yyy/
└── knowledge_global/     (conhecimento compartilhado)
```

---

## 🚀 Como Usar

### Instalação

```bash
# Instalar dependências
pip install agno streamlit openai lancedb sqlite3

# Executar
cd legal_document_analyzer
streamlit run dynamic_team_builder.py
```

### Fluxo de Trabalho Completo

#### 1️⃣ Configuração Inicial

```
Sidebar → Configurações
1. Cole chave OpenAI
2. Clique em "Salvar"
```

#### 2️⃣ Criar Agentes Customizados

```
Tab "Agentes" → "Criar"

Exemplo 1: Especialista Financeiro
┌────────────────────────────────┐
│ Nome: Analista Financeiro CFO  │
│ Emoji: 💰                      │
│ Role: Especialista em finanças │
│ Modelo: gpt-4o-mini            │
│ Instruções:                    │
│ - Você é um CFO experiente     │
│ - Analise sempre ROI e custos  │
│ - Foque em viabilidade         │
│ - Identifique riscos fiscais   │
└────────────────────────────────┘

Exemplo 2: Especialista Jurídico
┌────────────────────────────────┐
│ Nome: Advogado Contratual      │
│ Emoji: ⚖️                      │
│ Role: Especialista em contratos│
│ Modelo: gpt-4o                 │
│ Instruções:                    │
│ - Você é advogado especialista │
│ - Revise cláusulas legais      │
│ - Identifique riscos           │
│ - Sugira melhorias             │
└────────────────────────────────┘

Exemplo 3: Especialista LGPD
┌────────────────────────────────┐
│ Nome: DPO - Proteção de Dados  │
│ Emoji: 🔐                      │
│ Role: Data Protection Officer  │
│ Modelo: gpt-4o-mini            │
│ Instruções:                    │
│ - Você é DPO certificado       │
│ - Analise conformidade LGPD    │
│ - Verifique bases legais       │
│ - Avalie riscos de privacidade │
└────────────────────────────────┘
```

#### 3️⃣ Adicionar Base de Conhecimento

```
Tab "Conhecimento" → "Adicionar"

Opção A: Upload de Arquivo
┌────────────────────────────────┐
│ Associar a: Advogado Contratual│
│ Arquivo: modelo_contrato.pdf   │
│ [Adicionar]                    │
└────────────────────────────────┘

Opção B: Texto Direto
┌────────────────────────────────┐
│ Associar a: Global             │
│ Conteúdo:                      │
│ Art. 1º - Lei 13.709/2018 LGPD │
│ ...                            │
│ [Adicionar]                    │
└────────────────────────────────┘

Resultado:
✅ Cada agente pode ter sua base especializada
✅ Conhecimento global para todos
✅ LanceDB indexa automaticamente
```

#### 4️⃣ Montar o Time

```
Tab "Time"

Selecione os agentes que participarão:
☑️ 💰 Analista Financeiro CFO
☑️ ⚖️ Advogado Contratual
☑️ 🔐 DPO - Proteção de Dados

✅ 3 agente(s) selecionado(s)
```

#### 5️⃣ Executar - Criar Documento

```
Tab "Executar"

Modo: 📝 Criar Documento

Configurações:
- Rodadas: 3
- Chunking: fixed
- Chunk Size: 1000

Instruções:
┌────────────────────────────────────────┐
│ Criar uma Política de Privacidade      │
│ completa conforme LGPD, incluindo:     │
│ - Tipos de dados coletados             │
│ - Finalidades de tratamento            │
│ - Bases legais                         │
│ - Direitos dos titulares               │
│ - Medidas de segurança                 │
│ - Contato do DPO                       │
│                                        │
│ Público-alvo: E-commerce B2C brasileiro│
└────────────────────────────────────────┘

Contexto Adicional:
┌────────────────────────────────────────┐
│ Empresa: Loja Virtual XYZ              │
│ Setor: Varejo online                   │
│ Dados sensíveis: Não                   │
└────────────────────────────────────────┘

[🚀 Executar]
```

**Execução (3 Rodadas):**

```
🔄 Rodada 1/3
──────────────

💰 Analista Financeiro:
"Precisamos balancear conformidade com
custos de implementação. Sugiro..."

⚖️ Advogado Contratual:
"A política deve incluir cláusulas de
isenção e limitação de responsabilidade..."

🔐 DPO:
"CRÍTICO: Bases legais para cada
finalidade. Consentimento deve ser..."

[Streaming em tempo real... ████████░░ 80%]

──────────────

Feedback para Rodada 2 (opcional):
┌────────────────────────────────────────┐
│ Detalhe mais sobre cookies e           │
│ rastreamento. Inclua seção sobre       │
│ transferência internacional de dados.  │
└────────────────────────────────────────┘

🔄 Rodada 2/3
──────────────

[Time incorpora feedback e refina...]

💰 Analista Financeiro:
"Com base no feedback, sobre cookies:
custos de infraestrutura para consent
management são..."

⚖️ Advogado Contratual:
"Adicionei cláusula de transferência
internacional com SCCs..."

🔐 DPO:
"Política de cookies agora conforme
Art. 8º LGPD. Banner de consentimento..."

──────────────

🔄 Rodada 3/3 (Final)
──────────────

[Versão final polida e consolidada]

📄 POLÍTICA DE PRIVACIDADE

# Política de Privacidade - Loja Virtual XYZ

**Última atualização:** [data]

## 1. Introdução
A Loja Virtual XYZ ("nós", "nosso"...)
[documento completo em Markdown]

...

[📥 Download Markdown]

✅ Documento final criado com sucesso!
```

#### 6️⃣ Executar - Analisar Documento

```
Tab "Executar"

Modo: 🔍 Analisar Documento

[Upload: contrato_fornecedor.pdf]

Instruções:
┌────────────────────────────────────────┐
│ Analisar este contrato sob perspectivas│
│ financeira, jurídica e de privacidade. │
│ Identificar riscos e sugestões.        │
└────────────────────────────────────────┘

[🚀 Executar]

Resultado:
──────────────

🔄 Rodada 1/3

💰 CFO:
"ALTO RISCO: Multa de 100% do valor
contratual em rescisão antecipada..."

⚖️ Legal:
"CRÍTICO: Foro de Nova York é
desvantajoso. Sugiro São Paulo..."

🔐 DPO:
"BLOQUEADOR: Transferência para EUA
sem SCCs. Não conforme Art. 33 LGPD..."

[Continua refinando em 3 rodadas...]
```

---

## 🎯 Casos de Uso Detalhados

### Caso 1: Criação de Política Corporativa

**Objetivo:** Criar política de home office completa

**Time:**
- 👥 CHRO - Recursos Humanos
- ⚖️ Legal - Jurídico
- 🛡️ CISO - Segurança da Informação
- ⚙️ COO - Operações

**Conhecimento:**
- Upload: `CLT.pdf` (para Legal)
- Upload: `normas_seguranca.md` (para CISO)
- Upload: `politicas_rh_existentes.txt` (para CHRO)

**Rodadas:** 4

**Rodada 1:**
- CHRO: Define diretrizes de elegibilidade
- Legal: Garante conformidade CLT
- CISO: Especifica requisitos técnicos
- COO: Define processos operacionais

**Rodada 2:**
- Time debate frequência (híbrido vs full remote)
- Legal e CHRO discutem horas extras
- CISO detalha VPN e segurança

**Rodada 3:**
- Refinamento com feedback do usuário
- Adição de seção sobre equipamentos

**Rodada 4:**
- Versão final consolidada
- Todos aprovam
- Download do documento

**Resultado:** Política de 15 páginas, revisada por 4 especialistas, pronta para implementação.

---

### Caso 2: Análise de Contrato Complexo

**Objetivo:** Avaliar contrato SaaS internacional

**Time:**
- 👔 CEO - Visão estratégica
- 💰 CFO - Financeiro
- ⚖️ Legal - Jurídico
- 🔐 DPO - Privacidade
- 💻 CTO - Técnico

**Documento:** `contrato_salesforce.pdf`

**Conhecimento:**
- Upload: `contratos_similares.pdf` (Global)
- Upload: `orcamento_ti.xlsx` (para CFO)

**Rodadas:** 3

**Execução:**

**Rodada 1 - Análise Inicial:**

```markdown
👔 CEO:
Alinhado com estratégia de digitalização.
PREOCUPAÇÃO: Lock-in de 5 anos.

💰 CFO:
Valor: $500k/ano = R$ 2.5M/ano (câmbio 5.0)
CRÍTICO: Exposição cambial não mitigada.
Multa rescisória de 100% é inaceitável.
Questão: Há budget para hedge cambial?

⚖️ Legal:
Foro de Delaware é problemático.
Lei aplicável: Delaware Corporate Law.
ALTO RISCO: Limitação de indenização baixa.
Cláusula de arbitragem favorável.

🔐 DPO:
BLOQUEADOR CRÍTICO:
- Transferência EUA sem SCCs
- Não conforme Art. 33 LGPD
- Subprocessadores não listados
NÃO PODE ASSINAR na versão atual.

💻 CTO:
Stack compatível com sistemas atuais.
APIs disponíveis para integração.
PREOCUPAÇÃO: Vendor lock-in técnico.
SLA 99.5% é adequado mas penalidades baixas.
```

**Feedback Usuário:**
```
Budget para hedge: Sim, até R$ 200k/ano
Prazo ideal: 2-3 anos (não 5)
Vendor alternativo: HubSpot também avaliado
```

**Rodada 2 - Debate:**

```markdown
💬 DEBATE CFO vs Legal vs CEO:

CFO: "Multa 100% protege investimento vendor"
Legal: "Sim, mas nos expõe demais. Sugiro 30%"
CEO: "Concordo. Se vendor recusar, HubSpot"

💬 DEBATE DPO vs Legal:

DPO: "SCCs são obrigatórias, sem exceção"
Legal: "Correto. Posso incluir anexo padrão"
DPO: "Vendor deve assinar. Caso contrário, bloqueio"

💬 DEBATE CTO vs CFO:

CTO: "Lock-in técnico é real. Migração custará $100k"
CFO: "Logo, contrato máximo 2 anos para reavaliar"
CEO: "Decisão: Máximo 2 anos, renegociável"
```

**Rodada 3 - Consenso Final:**

```markdown
✅ CONSENSO DA MESA EXECUTIVA:

DECISÃO: NÃO ASSINAR versão atual

EMENDAS OBRIGATÓRIAS:
1. Prazo: 2 anos (não 5)
2. Multa: 30% (não 100%)
3. Adicionar: Anexo SCCs LGPD
4. Alterar: Foro para São Paulo
5. Incluir: Lista de subprocessadores
6. Aumentar: Penalidades por SLA
7. Adicionar: Cláusula de saída (portabilidade)

CONDIÇÕES FINANCEIRAS:
- CFO aprova até $520k/ano se emendas aceitas
- Budget hedge cambial: R$ 200k/ano
- Contingência legal: R$ 50k

PLANO DE AÇÃO:
1. Legal lidera renegociação (prazo: 15 dias)
2. SE vendor aceita emendas → CEO aprova assinatura
3. SE vendor recusa → CTO avalia HubSpot
4. DPO deve aprovar SCCs antes de assinar

RESPONSÁVEIS:
- Legal: Redigir emendas e negociar
- CFO: Aprovar termos financeiros finais
- DPO: Revisar e aprovar SCCs
- CTO: Preparar POC HubSpot (plano B)
- CEO: Decisão final após renegociação

📅 Revisão: 15 dias
```

**Resultado:** Decisão clara, consensual, acionável, com plano B.

---

## 💡 Recursos Avançados

### Conhecimento Especializado por Agente

```python
# Advogado tem acesso a:
- codigo_civil.pdf
- jurisprudencia_contratos.md
- modelos_clausulas.txt

# CFO tem acesso a:
- normas_contabeis.pdf
- historico_orcamento.csv
- análises_roi.xlsx

# DPO tem acesso a:
- lgpd_comentada.pdf
- decisoes_anpd.md
- modelos_politicas.txt

# Conhecimento Global (todos):
- missao_visao_valores.md
- politicas_corporativas.pdf
```

### Chunking Strategies

**Fixed Size:**
```
Documento dividido em chunks de 1000 chars
Overlap de 100 chars entre chunks
Rápido, previsível
```

**Semantic:**
```
IA identifica quebras semânticas
Respeita contexto e significado
Mais lento, mais preciso
```

**Agentic:**
```
Agente decide como chunkar
Adaptativo ao conteúdo
Melhor para documentos complexos
```

### Memória Persistente

```
Agent A em Rodada 1:
"Identificamos risco X"

Agent A em Rodada 2:
"Como mencionei na rodada anterior,
o risco X agora foi mitigado por..."

[Memória via SqliteDb]
```

### Fluxo Configurável

```yaml
Configuração 1: Rápida
- Rodadas: 1
- Agentes: 2-3
- Chunking: fixed
- Uso: Análises simples

Configuração 2: Padrão
- Rodadas: 2-3
- Agentes: 4-6
- Chunking: semantic
- Uso: Maioria dos casos

Configuração 3: Profunda
- Rodadas: 4-6
- Agentes: 8-10
- Chunking: agentic
- Uso: Decisões críticas
```

---

## 📊 Comparação de Versões

| Característica | v1.0 Basic | v2.0 Executive Board | v3.0 Dynamic Team |
|----------------|------------|----------------------|-------------------|
| Agentes | 5 fixos | 10 pré-definidos | ∞ customizáveis |
| CRUD Agentes | ❌ | ❌ | ✅ |
| Conhecimento | ChromaDB | ChromaDB | LanceDB + SQLite |
| Upload Docs | ❌ | ❌ | ✅ Multi-formato |
| Chunking | Fixed | Fixed | 4 estratégias |
| Persistência | Sessão | Sessão | SQLite completo |
| Memória | ❌ | ❌ | ✅ Persistente |
| Criar Docs | ❌ | ❌ | ✅ |
| Analisar Docs | ✅ | ✅ | ✅ |
| Streaming | ❌ | ❌ | ✅ |
| Fluxo Config | Fixo | Configurável | Totalmente dinâmico |
| Arquivos | 3 | 1 | 1 |

---

## 🎓 Melhores Práticas

### Criação de Agentes

**✅ BOM:**
```
Nome: Analista de Segurança Cibernética
Role: Especialista em ISO 27001 e NIST
Instruções:
- Você é CISO com 10 anos de experiência
- Foque em controles técnicos e administrativos
- Priorize riscos por severidade (C-I-A triad)
- Sempre cite frameworks (ISO 27001, NIST CSF)
- Proponha controles compensatórios
```

**❌ RUIM:**
```
Nome: Agente 1
Role: Ajuda com segurança
Instruções:
- Ajude com coisas de segurança
```

### Gestão de Conhecimento

**✅ BOM:**
- Documente origem e data dos documentos
- Use conhecimento específico para especialização
- Mantenha conhecimento global atualizado
- Delete documentos obsoletos

**❌ RUIM:**
- Upload indiscriminado de tudo para todos
- Documentos conflitantes sem versionamento
- Base desorganizada

### Configuração de Rodadas

**1 Rodada:**
- Análise rápida
- Decisão simples
- Tempo limitado

**2-3 Rodadas:**
- Maioria dos casos
- Debate e refinamento
- Qualidade boa

**4-6 Rodadas:**
- Decisões críticas
- Alto impacto
- Máxima qualidade

**7+ Rodadas:**
- Raramente necessário
- Pode causar repetição
- Retornos decrescentes

---

## 🔧 Troubleshooting

**Erro: "Agent not found"**
→ Agente foi deletado. Recrie ou selecione outro.

**Erro: "LanceDB connection failed"**
→ Verifique permissões em `~/.dynamic_team_builder/lancedb`

**Streaming lento**
→ Use menos agentes ou gpt-4o-mini

**Memória não persiste**
→ Verifique se `team_builder.db` existe

**Knowledge não encontrado**
→ Recarregue documentos após adicionar novos

---

## 📦 Estrutura de Arquivos

```
~/.dynamic_team_builder/
├── config.json              # API key
├── team_builder.db          # SQLite (agentes, docs, sessões)
└── lancedb/                 # Vetores
    ├── knowledge_global/
    ├── knowledge_agent_xxx/
    └── knowledge_agent_yyy/
```

---

## 🚀 Roadmap Futuro

- [ ] Suporte a mais modelos (Claude, Gemini)
- [ ] Export para PDF
- [ ] Templates de agentes
- [ ] Templates de times
- [ ] Colaboração multi-usuário
- [ ] API REST
- [ ] Integração com GitHub/GitLab
- [ ] Workflow automation
- [ ] Analytics e insights

---

## 💰 Custos Estimados

**Configuração Leve:**
- 2 agentes, 2 rodadas, gpt-4o-mini
- ~$0.03 por execução

**Configuração Padrão:**
- 5 agentes, 3 rodadas, gpt-4o-mini
- ~$0.10 por execução

**Configuração Profunda:**
- 10 agentes, 5 rodadas, gpt-4o
- ~$2.00 por execução

---

## 🎉 Conclusão

O **Dynamic Team Builder v3.0** é o sistema mais completo para:

✅ Criar e gerenciar times de agentes customizados
✅ Criar documentos do zero com colaboração multi-agente
✅ Analisar documentos com expertise multidisciplinar
✅ Persistir conhecimento e memória
✅ Configurar fluxos dinâmicos e adaptativos

**Comece agora:**
```bash
streamlit run dynamic_team_builder.py
```

---

**🚀 Dynamic Team Builder - Powered by Agno**
*Crie, gerencie e execute times de agentes IA como nunca antes*

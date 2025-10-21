# 🚀 AutoGen Multi-Agent Team Builder

## Sistema Completo com Microsoft AutoGen - O Melhor Orquestrador de Agentes

### 🌟 Visão Geral

O **AutoGen Multi-Agent Team Builder** é a implementação mais avançada, usando **Microsoft AutoGen** - considerado o **melhor framework para orquestração de agentes colaborativos**.

AutoGen foi desenvolvido pela **Microsoft Research** especificamente para permitir que múltiplos agentes de IA trabalhem juntos de forma natural, debatam, colaborem e cheguem a consensos.

---

## 🏆 Por Que AutoGen é o Melhor?

### Vantagens do AutoGen

| Recurso | AutoGen | Outros Frameworks |
|---------|---------|-------------------|
| **GroupChat Nativo** | ✅ Built-in | ❌ Precisa implementar |
| **Conversação Natural** | ✅ Agentes falam naturalmente | ⚠️ Turnos forçados |
| **Auto-seleção** | ✅ Agentes decidem quando falar | ❌ Ordem pré-definida |
| **Debate Real** | ✅ Discussão autêntica | ⚠️ Simulada |
| **RAG Integrado** | ✅ RetrieveAssistantAgent | ⚠️ Integração manual |
| **Multi-LLM** | ✅ OpenAI + Azure + Anthropic | ⚠️ Limitado |
| **Production-Ready** | ✅ Empresas usam | ⚠️ Experimental |
| **Manutenção** | ✅ Microsoft Research | ⚠️ Comunidade |

### Diferenciais Únicos

```python
# GroupChat Automático
groupchat = GroupChat(
    agents=[cfo, legal, dpo, ciso],
    messages=[],
    max_round=20,
    speaker_selection_method="auto"  # ✨ Mágica aqui!
)

# Agentes decidem quem fala próximo
# Debate flui naturalmente
# Sem ordem fixa ou turnos forçados
```

---

## ✨ Funcionalidades Completas

### ✅ Todas as Premissas Implementadas

#### 👥 CRUD de Agentes
- Criar agentes AutoGen customizados
- Editar agentes existentes
- Deletar agentes
- Templates prontos (CFO, Legal, DPO, CISO, CTO)
- Agentes ilimitados

#### 📚 Base de Conhecimento
- Upload: PDF, Markdown, TXT, DOCX, CSV
- Delete seletivo
- Conhecimento Global vs Por Agente
- RAG com RetrieveAssistantAgent

#### 🔧 Chunking Avançado
- Recursive Character
- Character Split
- Markdown Split
- Fixed Size

#### 💾 Persistência Total
- SQLite: Agentes, documentos, sessões, mensagens
- ChromaDB: Vetores e embeddings
- Histórico completo de conversas
- Cache de resultados

#### 🎯 GroupChat Colaborativo
- Múltiplos agentes conversam
- Debate natural e orgânico
- Auto-seleção de speaker
- Todos veem mensagens de todos

#### 📝 Dual Mode
- Criar Documentos: Co-criação colaborativa
- Analisar Documentos: Análise multidisciplinar

#### 🌊 Output e Interface
- Display em tempo real
- Saída Markdown formatada
- Download de conversas
- Interface Streamlit intuitiva

#### 🔌 Flexibilidade de API
- OpenAI (GPT-4, GPT-4o, GPT-4o-mini)
- Azure OpenAI (totalmente suportado)
- Configuração simples

---

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.8+
- Chave OpenAI ou Azure OpenAI

### Instalação

```bash
# Instalar dependências
pip install -r requirements_autogen.txt

# Ou manualmente
pip install pyautogen streamlit openai langchain langchain-openai chromadb pypdf python-docx
```

### Execução

```bash
cd legal_document_analyzer
streamlit run autogen_team_builder.py
```

Abrirá em `http://localhost:8501`

---

## 🎯 Como Usar

### 1️⃣ Configurar API

**Opção A: OpenAI**
```
Sidebar → API Type: OpenAI
→ Cole sua chave OpenAI
→ Salvar
```

**Opção B: Azure OpenAI**
```
Sidebar → API Type: Azure OpenAI
→ Azure Endpoint: https://your-resource.openai.azure.com/
→ API Key: sua-chave-azure
→ API Version: 2024-02-01
→ Salvar Azure Config
```

### 2️⃣ Criar Agentes

**Opção A: Usar Templates**
```
Tab "Agentes" → "Templates"

Templates Disponíveis:
- 💰 CFO - Chief Financial Officer
- ⚖️ Legal - Diretor Jurídico
- 🔐 DPO - Data Protection Officer
- 🛡️ CISO - Chief Information Security Officer
- 💻 CTO - Chief Technology Officer

→ Clique no template desejado
→ Agente criado automaticamente!
```

**Opção B: Criar Customizado**
```
Tab "Agentes" → "Criar"

Nome: Especialista_Financeiro_Senior
Emoji: 💰
Role: CFO especialista em M&A e valuation
System Message:
  Você é um CFO com 15 anos de experiência...
  Expertise em análise de valuation, M&A, reestruturação...
  Sempre cite métricas financeiras concretas...

Max Auto Replies: 10
Human Input Mode: NEVER

→ Criar Agente
```

### 3️⃣ Adicionar Conhecimento (RAG)

```
Tab "Conhecimento" → "Adicionar"

Associar a: 💰 CFO
Upload: [analises_mercado.pdf]
→ Adicionar

Associar a: ⚖️ Legal
Upload: [codigo_civil.pdf]
→ Adicionar

Associar a: Global
Upload: [politicas_internas.md]
→ Adicionar
```

### 4️⃣ Montar Time

```
Tab "Time"

Selecione pelo menos 2 agentes:
☑️ 💰 CFO
☑️ ⚖️ Legal
☑️ 🔐 DPO
☑️ 🛡️ CISO

✅ 4 agente(s) no team
```

### 5️⃣ Executar GroupChat

```
Tab "Executar"

Modo: [📝 Criar Documento]

Configurações:
- Max Rounds: 15
- Modelo: gpt-4o-mini
- Habilitar RAG: ✅
- Chunking: recursive

Instruções:
┌────────────────────────────────────────┐
│ Criar uma Política de Segurança da    │
│ Informação completa conforme ISO 27001,│
│ incluindo:                             │
│ - Controles técnicos e administrativos │
│ - Gestão de incidentes                │
│ - Conformidade LGPD                    │
│ - Plano de continuidade               │
│                                        │
│ Público: Empresa de tecnologia 200    │
│ funcionários                           │
└────────────────────────────────────────┘

[🚀 Executar AutoGen GroupChat]
```

**Execução (exemplo):**

```markdown
💬 Conversa do GroupChat
─────────────────────────────────

**User:**
Criar uma Política de Segurança da Informação completa...

---

**CISO:**
Excelente! Vou iniciar estruturando os controles de segurança
baseados na ISO 27001. Começarei pelos controles críticos:

1. **Controles de Acesso (A.9)**
   - Autenticação multifator obrigatória
   - Gestão de identidades e acessos (IAM)
   - Revisão trimestral de permissões

2. **Criptografia (A.10)**
   - TLS 1.3 para dados em trânsito
   - AES-256 para dados em repouso
   - Gestão segura de chaves

DPO e Legal, gostaria que validassem os aspectos de conformidade
LGPD nos controles de acesso.

---

**DPO:**
Obrigado CISO! Sobre os controles de acesso sob a ótica da LGPD:

**Conformidade LGPD:**
- Autenticação MFA atende Art. 46 (medidas de segurança) ✅
- IAM deve incluir logs de acesso (Art. 37 - relatório de impacto)
- Revisão trimestral adequada para auditoria ANPD

**Adições Necessárias:**
1. Implementar Privacy by Design nos controles
2. Adicionar seção sobre Direitos dos Titulares:
   - Acesso (Art. 18, I)
   - Correção (Art. 18, III)
   - Portabilidade (Art. 18, V)

Legal, poderia validar se há conflitos com outras legislações?

---

**Legal:**
Perfeito DPO! Sob perspectiva jurídica:

**Marco Legal:**
- ISO 27001 + LGPD: Totalmente compatíveis ✅
- CDC Art. 43 §1º: Direito de acesso aos dados ✅

**Risco Legal Identificado:**
A retenção de logs precisa de base legal clara.

**Sugestão:**
Adicionar cláusula: "Logs mantidos por 6 meses (obrigação
legal - Lei 12.965/2014, Art. 15)"

CFO, qual o impacto financeiro dessas implementações?

---

**CFO:**
Analisando os custos de implementação:

**CAPEX Estimado:**
- MFA (solução enterprise): R$ 50k implementação + R$ 15k/ano
- IAM (Azure AD Premium): R$ 80/usuário/ano = R$ 192k/ano
- Criptografia (HSM): R$ 120k + R$ 30k/ano manutenção
- Total CAPEX Ano 1: ~R$ 360k

**OPEX Recorrente:** ~R$ 237k/ano

**ROI Positivo:**
- Evita multas LGPD (até 2% faturamento ou R$ 50mi)
- Reduz risco de data breach (custo médio: R$ 5mi no Brasil)
- Payback: 1.2 anos

CISO, sugiro priorizar MFA e IAM no Q1, HSM no Q2
para diluir investimento.

---

**CISO:**
Excelente análise CFO! Concordo com a priorização.

**Roadmap Revisado:**

**Q1/2025:**
- Implementar MFA (R$ 50k)
- Contratar Azure AD Premium (R$ 48k Q1)
- Definir políticas de acesso

**Q2/2025:**
- Implementar HSM (R$ 120k)
- Iniciar criptografia de databases
- Treinamento equipes

Todos concordam com este approach?

---

**Legal:**
Concordo ✅

**DPO:**
Aprovado ✅ - Permite adequação LGPD progressiva

**CFO:**
Alinhado com budget ✅

---

**CISO:**
Perfeito! Então vou consolidar a Política final...

# POLÍTICA DE SEGURANÇA DA INFORMAÇÃO

## 1. Objetivo e Escopo
[... documento completo ...]

## 2. Controles de Segurança (ISO 27001)
[... seções detalhadas ...]

## 3. Conformidade LGPD
[... requisitos DPO ...]

## 4. Aspectos Legais
[... validações Legal ...]

## 5. Roadmap de Implementação
[... plano CFO ...]

---

✅ Conversa concluída!

[📥 Download Markdown]
```

---

## 🎯 Casos de Uso Reais

### Caso 1: Criar Política Corporativa

**Objetivo:** Política de Home Office

**Team AutoGen:**
- 👥 CHRO (RH)
- ⚖️ Legal (Jurídico)
- 🛡️ CISO (Segurança)
- ⚙️ COO (Operações)

**Conhecimento:**
- Upload: CLT.pdf (para Legal)
- Upload: normas_seguranca.md (para CISO)
- Upload: politicas_existentes.txt (para CHRO)

**Execução:**
```
Modo: Criar Documento
Max Rounds: 20
RAG: Habilitado

GroupChat:
1. CHRO propõe estrutura de elegibilidade
2. Legal valida conformidade CLT
3. CISO adiciona requisitos técnicos
4. COO define processos operacionais
5. Debate: CHRO vs COO sobre frequência
6. Consenso: Híbrido 3 dias/semana
7. Legal drafta cláusulas
8. CISO especifica VPN e segurança
9. Todos revisam versão final
10. Documento aprovado!

Resultado: Política de 15 páginas,
co-criada por 4 especialistas,
pronta para implementação
```

### Caso 2: Analisar Contrato SaaS Internacional

**Objetivo:** Avaliar contrato antes de assinar

**Team AutoGen:**
- 👔 CEO
- 💰 CFO
- ⚖️ Legal
- 🔐 DPO
- 💻 CTO

**Documento:** contrato_salesforce.pdf

**Execução:**
```
Modo: Analisar Documento
Max Rounds: 15
RAG: Habilitado

GroupChat:
1. User carrega contrato
2. Legal identifica: Foro NY problemático
3. DPO identifica: Falta SCCs para LGPD
4. CFO identifica: Multa 100% inaceitável
5. CTO identifica: Lock-in técnico
6. CEO pede: Debater riscos
7. Debate Legal vs CFO: Multa
8. Debate DPO vs Legal: SCCs obrigatórias
9. CEO pede: Consenso
10. Todos concordam: NÃO assinar sem emendas
11. Legal lista emendas necessárias
12. CFO aprova budget para renegociação
13. Consenso final: Renegociar ou alternativa

Resultado: Decisão clara, consensual,
com plano de ação específico
```

### Caso 3: Criar Resposta a RFP

**Objetivo:** Responder RFP de cliente

**Team AutoGen:**
- 💰 CFO (Pricing)
- 💻 CTO (Solução Técnica)
- ⚙️ COO (Operações)
- 📢 CMO (Proposta de Valor)

**Conhecimento:**
- Upload: rfp_cliente.pdf (Global)
- Upload: casos_sucesso.md (para CMO)
- Upload: arquitetura_solucoes.pdf (para CTO)

**Execução:**
```
Modo: Criar Documento
Max Rounds: 25
RAG: Habilitado

GroupChat:
1. CTO analisa requisitos técnicos RFP
2. CFO calcula custos de entrega
3. COO avalia capacidade operacional
4. CMO drafta proposta de valor
5. Debate: CTO vs COO sobre prazo
6. Consenso: 6 meses (não 4)
7. CFO ajusta pricing baseado em 6 meses
8. CMO refina narrativa
9. Todos revisam seção por seção
10. CTO adiciona diagramas técnicos
11. CFO finaliza pricing com 15% margem
12. Versão final co-criada

Resultado: Proposta RFP completa,
tecnicamente viável,
financeiramente sólida,
operacionalmente executável
```

---

## 💡 Arquitetura AutoGen

### Como Funciona

```
┌─────────────────────────────────────────┐
│        AutoGen GroupChat                │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │ CFO  │  │Legal │  │ DPO  │         │
│  └──┬───┘  └──┬───┘  └──┬───┘         │
│     │         │         │              │
│     └─────────┼─────────┘              │
│               │                        │
│        ┌──────▼──────┐                 │
│        │ GroupChat   │                 │
│        │  Manager    │                 │
│        └──────┬──────┘                 │
│               │                        │
│     ┌─────────┼─────────┐              │
│     │         │         │              │
│  ┌──▼───┐  ┌─▼────┐  ┌─▼────┐         │
│  │CISO  │  │ CTO  │  │ CEO  │         │
│  └──────┘  └──────┘  └──────┘         │
│                                         │
│  Todos veem mensagens de todos          │
│  Auto-seleção de próximo speaker        │
│  Debate natural e orgânico              │
└─────────────────────────────────────────┘
```

### Componentes

**1. Agents (AssistantAgent)**
```python
cfo = AssistantAgent(
    name="CFO",
    system_message="Você é o CFO...",
    llm_config=llm_config,
)
```

**2. RAG Agents (RetrieveAssistantAgent)**
```python
legal = RetrieveAssistantAgent(
    name="Legal",
    system_message="Você é advogado...",
    llm_config=llm_config,
    # Acesso automático a documentos
)
```

**3. GroupChat**
```python
groupchat = GroupChat(
    agents=[cfo, legal, dpo, ciso],
    messages=[],
    max_round=20,
    speaker_selection_method="auto",  # Mágica!
)
```

**4. Manager**
```python
manager = GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
)
```

**5. Execução**
```python
user_proxy.initiate_chat(
    manager,
    message="Criar política de segurança..."
)
# Agentes conversam automaticamente!
```

---

## 🔥 Diferenciais AutoGen vs Outros

### Comparação Técnica

| Aspecto | AutoGen | LangGraph | CrewAI | Agno |
|---------|---------|-----------|--------|------|
| **GroupChat** | ✅ Nativo | ❌ Manual | ⚠️ Sequencial | ⚠️ Sequencial |
| **Auto-seleção** | ✅ Sim | ❌ Não | ❌ Não | ❌ Não |
| **Debate Natural** | ✅ Real | ❌ Simulado | ⚠️ Parcial | ⚠️ Parcial |
| **RAG** | ✅ RetrieveAssistant | ⚠️ Manual | ⚠️ Manual | ✅ Nativo |
| **Multi-LLM** | ✅ Sim | ✅ Sim | ⚠️ Limitado | ⚠️ OpenAI only |
| **Manutenção** | ✅ Microsoft | ⚠️ Comunidade | ⚠️ Startup | ⚠️ Startup |
| **Produção** | ✅ Enterprise | ⚠️ Experimental | ⚠️ Beta | ⚠️ Beta |

### Por Que AutoGen Vence?

**1. Conversação Natural**
```python
# AutoGen
groupchat = GroupChat(agents=[...])
# Agentes decidem quem fala próximo baseado no contexto!

# Outros
for agent in agents:
    agent.run()  # Ordem fixa, sem flexibilidade
```

**2. Debate Autêntico**
```python
# Com AutoGen
CFO: "Custos muito altos!"
Legal: "Mas é obrigatório por lei"
CFO: "Existe alternativa mais barata?"
CISO: "Sim, posso propor..."
# ↑ Fluxo natural, decidido pelos agentes

# Sem AutoGen
Agent1 → Agent2 → Agent3 → Agent4
# ↑ Sequencial, sem debate real
```

**3. RAG Integrado**
```python
# AutoGen
agent = RetrieveAssistantAgent(
    # RAG automático nos documentos!
)

# Outros
agent = Agent()
# Você precisa implementar RAG manualmente
```

---

## 📊 Performance e Custos

### Custos Estimados (gpt-4o-mini)

| Cenário | Agentes | Rounds | Custo |
|---------|---------|--------|-------|
| Simples | 2 | 5 | ~$0.03 |
| Padrão | 4 | 15 | ~$0.15 |
| Complexo | 6 | 25 | ~$0.40 |
| Enterprise | 10 | 50 | ~$1.50 |

### Tempos Típicos

- Criação de política: 5-10 min
- Análise de contrato: 3-7 min
- Resposta RFP: 10-20 min

---

## 🔧 Configuração Avançada

### Azure OpenAI

```python
# Configuração na interface
API Type: Azure OpenAI
Azure Endpoint: https://your-resource.openai.azure.com/
API Key: sua-chave
API Version: 2024-02-01

# AutoGen usa automaticamente!
```

### Chunking Strategies

**Recursive (Recomendado):**
- Melhor para textos gerais
- Preserva contexto
- Separadores: \n\n, \n, ., espaço

**Markdown:**
- Preserva estrutura MD
- Ideal para documentação

**Character:**
- Simples e rápido
- Tamanho fixo

### RAG Configuration

```python
# Por agente
Legal → codigo_civil.pdf
DPO → lgpd_comentada.pdf
CFO → normas_contabeis.pdf

# Global
politicas_internas.md → Todos agentes
```

---

## 🎓 Melhores Práticas

### Criação de Agentes

**✅ BOM:**
```python
name: "CFO_Financeiro"  # Sem espaços
system_message: """
Você é o CFO com 15 anos de experiência.

Responsabilidades:
- Analisar viabilidade financeira
- Calcular ROI e payback
- Identificar riscos fiscais

Sempre:
- Quantifique valores
- Cite normas contábeis
- Proponha alternativas
"""
```

**❌ RUIM:**
```python
name: "Agente 1"  # Nome genérico
system_message: "Ajude com finanças"  # Vago
```

### Configuração de Rounds

- **5-10 rounds:** Análises simples
- **15-20 rounds:** Criação de documentos
- **25-50 rounds:** Projetos complexos

### RAG Effectiveness

- Documente fontes dos PDFs
- Mantenha documentos atualizados
- Use chunks de 1000-2000 caracteres
- Overlap de 200 caracteres

---

## 🚀 Roadmap Futuro

- [ ] Suporte a Claude (Anthropic)
- [ ] Suporte a Gemini
- [ ] Code execution para agentes
- [ ] Visualização de grafos de conversa
- [ ] Templates de teams completos
- [ ] Export para PDF com formatação
- [ ] API REST
- [ ] Colaboração multi-usuário

---

## 🎉 Conclusão

O **AutoGen Multi-Agent Team Builder** é a solução mais avançada para:

✅ Orquestração de múltiplos agentes colaborativos
✅ Debate natural e autêntico entre agentes
✅ RAG integrado e nativo
✅ Flexibilidade total (OpenAI ou Azure)
✅ Production-ready para empresas

**AutoGen da Microsoft Research é o melhor framework para agentes colaborativos.**

### Comece Agora

```bash
pip install -r requirements_autogen.txt
streamlit run autogen_team_builder.py
```

---

**🚀 AutoGen Multi-Agent Team Builder**
*Powered by Microsoft AutoGen - The Best Agent Orchestrator*

**Desenvolvido com ❤️ para colaboração real entre agentes IA**

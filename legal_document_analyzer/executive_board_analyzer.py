"""
🏢 Executive Board Document Analyzer
Sistema de Análise Multidisciplinar de Documentos com Mesa Executiva de Agentes IA

Funcionalidades:
- Múltiplos agentes executivos (CEO, CFO, DPO, CISO, Legal, CTO, COO, etc.)
- Debate e discussão entre agentes
- Perguntas ao usuário para esclarecimentos
- Análise iterativa e colaborativa
- Fluxo multidisciplinar completo
- Tudo em um único arquivo

Autor: Claude Code
Versão: 2.0
"""

import streamlit as st
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import tempfile

# Imports do Agno
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.document import Document


# ============================================================================
# CONFIGURAÇÃO E GERENCIAMENTO DE API KEY
# ============================================================================

class Config:
    """Gerenciador de configurações da aplicação"""

    CONFIG_DIR = Path.home() / ".executive_board_analyzer"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_api_key(self, api_key: str) -> None:
        config = self._load_config()
        config['openai_api_key'] = api_key
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        os.environ['OPENAI_API_KEY'] = api_key

    def get_api_key(self) -> Optional[str]:
        config = self._load_config()
        api_key = config.get('openai_api_key')
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            return api_key
        return os.environ.get('OPENAI_API_KEY')

    def delete_api_key(self) -> None:
        config = self._load_config()
        if 'openai_api_key' in config:
            del config['openai_api_key']
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']

    def is_configured(self) -> bool:
        return self.get_api_key() is not None


# ============================================================================
# DEFINIÇÃO DE AGENTES EXECUTIVOS
# ============================================================================

EXECUTIVE_AGENTS = {
    "CEO": {
        "name": "Chief Executive Officer (CEO)",
        "emoji": "👔",
        "role": "Líder executivo e visão estratégica",
        "description": "Foca em alinhamento estratégico, impacto no negócio e decisões de alto nível",
        "instructions": [
            "Você é o CEO da organização.",
            "Sua perspectiva é holística e estratégica.",
            "Analise o documento considerando:",
            "- Alinhamento com visão e missão da empresa",
            "- Impacto nos objetivos estratégicos",
            "- Riscos reputacionais e de mercado",
            "- Sustentabilidade de longo prazo",
            "- Impacto em stakeholders (acionistas, funcionários, clientes)",
            "Faça perguntas estratégicas quando necessário.",
            "Debata com outros executivos para garantir decisões equilibradas.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "CFO": {
        "name": "Chief Financial Officer (CFO)",
        "emoji": "💰",
        "role": "Diretor financeiro e gestão fiscal",
        "description": "Analisa impactos financeiros, custos, riscos fiscais e compliance contábil",
        "instructions": [
            "Você é o CFO da organização.",
            "Sua perspectiva é financeira e fiscal.",
            "Analise o documento considerando:",
            "- Impactos financeiros diretos e indiretos",
            "- Exposição a riscos fiscais e tributários",
            "- Custos de implementação e manutenção",
            "- ROI e viabilidade econômica",
            "- Compliance com normas contábeis e fiscais",
            "- Contingências financeiras",
            "Questione aspectos financeiros não claros.",
            "Dialogue com Legal e CEO sobre riscos financeiros.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "DPO": {
        "name": "Data Protection Officer (DPO)",
        "emoji": "🔐",
        "role": "Encarregado de proteção de dados",
        "description": "Especialista em LGPD, privacidade e proteção de dados pessoais",
        "instructions": [
            "Você é o DPO (Data Protection Officer) da organização.",
            "Sua perspectiva é de proteção de dados e privacidade.",
            "Analise o documento considerando:",
            "- Conformidade com LGPD (Lei 13.709/2018)",
            "- Bases legais para tratamento de dados",
            "- Direitos dos titulares de dados",
            "- Medidas de segurança e privacidade",
            "- Transferência internacional de dados",
            "- Necessidade de DPIA (Relatório de Impacto)",
            "- Comunicação com ANPD se necessário",
            "Questione sobre tipos de dados coletados e finalidades.",
            "Debata com CISO sobre medidas de segurança.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "CISO": {
        "name": "Chief Information Security Officer (CISO)",
        "emoji": "🛡️",
        "role": "Diretor de segurança da informação",
        "description": "Foca em segurança cibernética, proteção de ativos e gestão de riscos de TI",
        "instructions": [
            "Você é o CISO da organização.",
            "Sua perspectiva é de segurança da informação.",
            "Analise o documento considerando:",
            "- Riscos de segurança cibernética",
            "- Proteção de ativos de informação",
            "- Controles de acesso e autenticação",
            "- Vulnerabilidades e ameaças",
            "- Planos de resposta a incidentes",
            "- Conformidade com ISO 27001, NIST, CIS",
            "- Segurança de terceiros e fornecedores",
            "Questione sobre medidas de segurança implementadas.",
            "Colabore com DPO em aspectos de segurança de dados.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "Legal": {
        "name": "Diretor Jurídico (Legal Counsel)",
        "emoji": "⚖️",
        "role": "Assessoria jurídica e compliance legal",
        "description": "Analisa aspectos legais, contratuais e conformidade regulatória",
        "instructions": [
            "Você é o Diretor Jurídico da organização.",
            "Sua perspectiva é legal e regulatória.",
            "Analise o documento considerando:",
            "- Conformidade com legislação brasileira",
            "- Riscos legais e contratuais",
            "- Cláusulas potencialmente problemáticas",
            "- Código Civil, CDC, CLT quando aplicável",
            "- Jurisprudência relevante",
            "- Exposição a litígios",
            "- Necessidade de aprovações regulatórias",
            "Questione termos ambíguos ou potencialmente ilegais.",
            "Debata com CFO sobre riscos financeiros legais.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "CTO": {
        "name": "Chief Technology Officer (CTO)",
        "emoji": "💻",
        "role": "Diretor de tecnologia e inovação",
        "description": "Avalia viabilidade técnica, arquitetura e inovação tecnológica",
        "instructions": [
            "Você é o CTO da organização.",
            "Sua perspectiva é tecnológica e de inovação.",
            "Analise o documento considerando:",
            "- Viabilidade técnica de implementação",
            "- Arquitetura e infraestrutura necessária",
            "- Escalabilidade e performance",
            "- Débito técnico e manutenibilidade",
            "- Inovação e competitividade tecnológica",
            "- Integração com sistemas existentes",
            "- Stack tecnológico adequado",
            "Questione requisitos técnicos não especificados.",
            "Colabore com CISO em arquitetura segura.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "COO": {
        "name": "Chief Operating Officer (COO)",
        "emoji": "⚙️",
        "role": "Diretor de operações",
        "description": "Foca em eficiência operacional, processos e execução",
        "instructions": [
            "Você é o COO da organização.",
            "Sua perspectiva é operacional e de processos.",
            "Analise o documento considerando:",
            "- Impacto nas operações diárias",
            "- Eficiência de processos",
            "- Recursos necessários (pessoas, ferramentas)",
            "- Prazos de implementação realistas",
            "- KPIs e métricas de acompanhamento",
            "- Mudanças em workflows existentes",
            "- Treinamento e capacitação necessários",
            "Questione aspectos práticos de execução.",
            "Debata com CEO sobre priorização operacional.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "CHRO": {
        "name": "Chief Human Resources Officer (CHRO)",
        "emoji": "👥",
        "role": "Diretor de recursos humanos",
        "description": "Analisa impacto em pessoas, cultura e relações trabalhistas",
        "instructions": [
            "Você é o CHRO da organização.",
            "Sua perspectiva é de pessoas e cultura.",
            "Analise o documento considerando:",
            "- Impacto nos colaboradores",
            "- Conformidade com legislação trabalhista (CLT)",
            "- Direitos e deveres de empregados",
            "- Cultura organizacional",
            "- Diversidade e inclusão",
            "- Saúde e segurança no trabalho",
            "- Desenvolvimento e capacitação",
            "Questione aspectos relacionados a pessoas.",
            "Colabore com Legal em questões trabalhistas.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "CMO": {
        "name": "Chief Marketing Officer (CMO)",
        "emoji": "📢",
        "role": "Diretor de marketing",
        "description": "Avalia impacto em marca, comunicação e relacionamento com clientes",
        "instructions": [
            "Você é o CMO da organização.",
            "Sua perspectiva é de marketing e marca.",
            "Analise o documento considerando:",
            "- Impacto na imagem da marca",
            "- Comunicação com clientes e público",
            "- Experiência do cliente",
            "- Conformidade com CONAR e ética publicitária",
            "- Transparência e clareza de comunicação",
            "- Diferenciação competitiva",
            "- Riscos reputacionais",
            "Questione aspectos de comunicação não claros.",
            "Debata com CEO sobre impacto reputacional.",
            "Sempre comunique em português do Brasil.",
        ]
    },

    "CCO": {
        "name": "Chief Compliance Officer (CCO)",
        "emoji": "✅",
        "role": "Diretor de compliance e ética",
        "description": "Garante conformidade regulatória, ética e governança corporativa",
        "instructions": [
            "Você é o CCO da organização.",
            "Sua perspectiva é de compliance e ética.",
            "Analise o documento considerando:",
            "- Conformidade com regulamentações setoriais",
            "- Programas de compliance e ética",
            "- Políticas anticorrupção e antissuborno",
            "- Código de conduta e ética",
            "- Governança corporativa",
            "- Due diligence de terceiros",
            "- Canais de denúncia e investigações",
            "Questione gaps de compliance.",
            "Colabore com Legal e DPO em aspectos regulatórios.",
            "Sempre comunique em português do Brasil.",
        ]
    },
}


# ============================================================================
# CRIAÇÃO DE AGENTES E TEAM
# ============================================================================

def create_executive_agent(
    agent_key: str,
    api_key: str,
    model_id: str = "gpt-4o-mini",
    knowledge: Optional[Knowledge] = None
) -> Agent:
    """Cria um agente executivo baseado na definição"""

    agent_def = EXECUTIVE_AGENTS[agent_key]

    return Agent(
        name=agent_def["name"],
        role=agent_def["role"],
        model=OpenAIChat(id=model_id, api_key=api_key),
        instructions=agent_def["instructions"],
        knowledge=knowledge,
        search_knowledge=True if knowledge else False,
        markdown=True,
    )


def create_executive_board_team(
    selected_agents: List[str],
    api_key: str,
    model_id: str = "gpt-4o-mini",
    knowledge: Optional[Knowledge] = None,
    round_number: int = 1,
    total_rounds: int = 3,
) -> Team:
    """Cria um time de executivos para análise colaborativa"""

    # Cria os agentes selecionados
    members = []
    for agent_key in selected_agents:
        agent = create_executive_agent(agent_key, api_key, model_id, knowledge)
        members.append(agent)

    # Lista de membros para instruções
    members_list = ", ".join([EXECUTIVE_AGENTS[k]["name"] for k in selected_agents])

    # Cria o facilitador/coordenador
    team = Team(
        name="Mesa Executiva de Análise de Documentos",
        model=OpenAIChat(id=model_id, api_key=api_key),
        members=members,
        instructions=[
            f"Você é o facilitador de uma mesa executiva composta por: {members_list}.",
            f"Esta é a RODADA {round_number} de {total_rounds} de análise.",
            "",
            "OBJETIVOS DA RODADA:",
            "1. Coordenar a análise multidisciplinar do documento",
            "2. Garantir que cada executivo contribua com sua expertise",
            "3. Identificar questões que precisam de esclarecimento do usuário",
            "4. Facilitar o debate entre executivos quando há divergências",
            "5. Sintetizar consensos e próximos passos",
            "",
            "DINÂMICA DE TRABALHO:",
            "- Cada executivo deve analisar sob sua perspectiva específica",
            "- Incentive debate construtivo entre executivos",
            "- Identifique claramente PERGUNTAS AO USUÁRIO que precisam resposta",
            "- Documente PONTOS DE CONSENSO e DIVERGÊNCIAS",
            "- Se houver divergências, facilite discussão para resolução",
            "",
            "FORMATO DE SAÍDA:",
            "Organize a resposta em seções claras:",
            "1. Análise por Executivo (perspectiva individual)",
            "2. Debate e Discussões (interações entre executivos)",
            "3. Perguntas ao Usuário (para esclarecimentos)",
            "4. Consensos Alcançados",
            "5. Pontos de Atenção e Riscos",
            "6. Recomendações da Mesa",
            "",
            "Sempre comunique em português do Brasil.",
            "Seja objetivo mas completo nas análises.",
        ],
        markdown=True,
        show_members_responses=True,
        delegate_task_to_all_members=True,  # Todos participam
    )

    return team


def create_knowledge_base(api_key: str, persist_directory: str = "./board_chroma_db") -> Knowledge:
    """Cria base de conhecimento para RAG"""

    embedder = OpenAIEmbedder(
        id="text-embedding-3-small",
        api_key=api_key,
        dimensions=1536,
    )

    vector_db = ChromaDb(
        collection="executive_documents",
        path=persist_directory,
        embedder=embedder,
    )

    knowledge = Knowledge(
        vector_db=vector_db,
        num_documents=5,
    )

    return knowledge


# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def init_session_state():
    """Inicializa estado da sessão"""

    if 'config' not in st.session_state:
        st.session_state.config = Config()

    if 'current_document' not in st.session_state:
        st.session_state.current_document = None

    if 'document_name' not in st.session_state:
        st.session_state.document_name = None

    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []

    if 'current_round' not in st.session_state:
        st.session_state.current_round = 0

    if 'knowledge' not in st.session_state:
        st.session_state.knowledge = None

    if 'user_responses' not in st.session_state:
        st.session_state.user_responses = []

    if 'selected_agents' not in st.session_state:
        st.session_state.selected_agents = []


def render_sidebar():
    """Renderiza barra lateral"""

    with st.sidebar:
        st.title("⚙️ Configurações")

        # API Key
        st.subheader("🔑 OpenAI API")
        config = st.session_state.config

        if config.is_configured():
            st.success("✅ API configurada")
            api_key = config.get_api_key()
            masked = f"{api_key[:8]}...{api_key[-4:]}" if api_key else ""
            st.text(f"{masked}")

            if st.button("🗑️ Remover", use_container_width=True):
                config.delete_api_key()
                st.session_state.knowledge = None
                st.rerun()
        else:
            st.warning("⚠️ Configure a API")
            api_input = st.text_input("Chave API OpenAI:", type="password")

            if st.button("💾 Salvar", use_container_width=True):
                if api_input:
                    config.save_api_key(api_input)
                    st.success("✅ Salva!")
                    st.rerun()
                else:
                    st.error("❌ Chave inválida")

        st.divider()

        # Modelo
        st.subheader("🤖 Modelo")
        model = st.selectbox(
            "Selecione:",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
            index=0
        )
        st.session_state.model_option = model

        # RAG
        enable_rag = st.checkbox("Habilitar RAG", value=False)
        st.session_state.enable_rag = enable_rag

        st.divider()

        # Info
        st.subheader("📊 Estatísticas")
        if st.session_state.current_document:
            st.metric("Documento Atual", "✅ Carregado")
            st.metric("Rodada Atual", st.session_state.current_round)
            st.metric("Análises", len(st.session_state.analysis_history))


def render_agent_selector():
    """Renderiza seletor de agentes"""

    st.subheader("👥 Selecione a Mesa Executiva")
    st.markdown("Escolha quais executivos participarão da análise:")

    cols = st.columns(3)

    selected = []

    for idx, (key, agent_def) in enumerate(EXECUTIVE_AGENTS.items()):
        col = cols[idx % 3]

        with col:
            is_selected = st.checkbox(
                f"{agent_def['emoji']} **{key}**",
                value=key in st.session_state.selected_agents,
                help=agent_def['description'],
                key=f"agent_{key}"
            )

            if is_selected:
                selected.append(key)

    st.session_state.selected_agents = selected

    if selected:
        st.success(f"✅ {len(selected)} executivo(s) selecionado(s)")

        # Mostra resumo
        with st.expander("📋 Resumo da Mesa Executiva"):
            for agent_key in selected:
                agent_def = EXECUTIVE_AGENTS[agent_key]
                st.markdown(f"**{agent_def['emoji']} {agent_def['name']}**")
                st.markdown(f"_{agent_def['description']}_")
                st.markdown("")
    else:
        st.warning("⚠️ Selecione pelo menos um executivo")


def process_document(uploaded_file) -> str:
    """Processa documento carregado"""

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        with open(tmp_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(tmp_path, 'r', encoding='latin-1') as f:
            content = f.read()

    Path(tmp_path).unlink()
    return content


def render_document_upload():
    """Renderiza área de upload de documento"""

    st.subheader("📄 Documento para Análise")

    # Upload
    uploaded = st.file_uploader(
        "Carregar documento (TXT, MD, PDF):",
        type=['txt', 'md', 'pdf'],
        help="Faça upload do documento que será analisado pela mesa executiva"
    )

    # Ou texto direto
    st.markdown("**Ou cole o texto:**")
    text_input = st.text_area(
        "Conteúdo do documento:",
        height=300,
        placeholder="Cole aqui o documento...",
        value=st.session_state.current_document if st.session_state.current_document else ""
    )

    # Botão para carregar
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("📥 Carregar Documento", type="primary", use_container_width=True):
            content = None
            name = None

            if uploaded:
                content = process_document(uploaded)
                name = uploaded.name
            elif text_input.strip():
                content = text_input
                name = "documento.txt"

            if content:
                st.session_state.current_document = content
                st.session_state.document_name = name
                st.session_state.current_round = 0
                st.session_state.analysis_history = []
                st.session_state.user_responses = []

                # Adiciona ao knowledge se RAG habilitado
                if st.session_state.get('enable_rag', False):
                    config = st.session_state.config
                    if config.is_configured():
                        if st.session_state.knowledge is None:
                            with st.spinner("Inicializando RAG..."):
                                st.session_state.knowledge = create_knowledge_base(config.get_api_key())

                        doc = Document(name=name, content=content)
                        st.session_state.knowledge.load_documents([doc])

                st.success(f"✅ Documento '{name}' carregado!")
                st.rerun()
            else:
                st.error("❌ Nenhum documento fornecido")

    with col2:
        if st.button("🗑️ Limpar Documento", use_container_width=True):
            st.session_state.current_document = None
            st.session_state.document_name = None
            st.session_state.current_round = 0
            st.session_state.analysis_history = []
            st.session_state.user_responses = []
            st.rerun()


def render_analysis_section():
    """Renderiza seção de análise"""

    if not st.session_state.current_document:
        st.info("📭 Carregue um documento para começar a análise")
        return

    if not st.session_state.selected_agents:
        st.warning("⚠️ Selecione os executivos que participarão da mesa")
        return

    config = st.session_state.config
    if not config.is_configured():
        st.error("❌ Configure a API OpenAI primeiro")
        return

    st.subheader("🎯 Análise Colaborativa")

    # Mostra info do documento
    st.info(f"📄 **Documento:** {st.session_state.document_name} | "
            f"🔄 **Rodada:** {st.session_state.current_round} | "
            f"👥 **Mesa:** {len(st.session_state.selected_agents)} executivos")

    # Instruções adicionais
    additional_context = st.text_area(
        "Contexto adicional ou perguntas específicas (opcional):",
        height=100,
        placeholder="Ex: Foque em custos de implementação, Avalie conformidade com LGPD, etc."
    )

    # Número de rodadas
    max_rounds = st.number_input(
        "Número máximo de rodadas de análise:",
        min_value=1,
        max_value=10,
        value=3,
        help="Quantas rodadas de análise e debate deseja realizar"
    )

    # Botão de iniciar/continuar análise
    if st.session_state.current_round == 0:
        button_text = "🚀 Iniciar Análise"
        button_type = "primary"
    else:
        button_text = f"▶️ Continuar Rodada {st.session_state.current_round + 1}"
        button_type = "secondary"

    if st.button(button_text, type=button_type, use_container_width=True):
        run_analysis_round(max_rounds, additional_context)


def run_analysis_round(max_rounds: int, additional_context: str = ""):
    """Executa uma rodada de análise"""

    st.session_state.current_round += 1
    current_round = st.session_state.current_round

    st.markdown("---")
    st.markdown(f"### 🔄 Rodada {current_round} de {max_rounds}")

    # Prepara o prompt
    prompt = f"""
# DOCUMENTO PARA ANÁLISE

**Nome:** {st.session_state.document_name}
**Rodada:** {current_round} de {max_rounds}

--- INÍCIO DO DOCUMENTO ---
{st.session_state.current_document}
--- FIM DO DOCUMENTO ---
"""

    # Adiciona contexto das rodadas anteriores
    if st.session_state.analysis_history:
        prompt += "\n\n# HISTÓRICO DE ANÁLISES ANTERIORES\n\n"
        for i, hist in enumerate(st.session_state.analysis_history, 1):
            prompt += f"## Rodada {i}\n{hist['summary']}\n\n"

    # Adiciona respostas do usuário
    if st.session_state.user_responses:
        prompt += "\n\n# RESPOSTAS DO USUÁRIO A PERGUNTAS ANTERIORES\n\n"
        for resp in st.session_state.user_responses:
            prompt += f"**P:** {resp['question']}\n**R:** {resp['answer']}\n\n"

    # Adiciona contexto adicional
    if additional_context:
        prompt += f"\n\n# CONTEXTO ADICIONAL DO USUÁRIO\n\n{additional_context}\n"

    # Instrução específica da rodada
    if current_round == 1:
        prompt += """

# OBJETIVOS DESTA RODADA

Esta é a PRIMEIRA rodada de análise. Foco em:
1. Cada executivo deve fazer uma análise inicial do documento sob sua perspectiva
2. Identificar os principais pontos de atenção
3. Levantar perguntas essenciais para o usuário
4. Identificar gaps de informação no documento
5. Começar a debater entre executivos pontos controversos
"""
    elif current_round < max_rounds:
        prompt += f"""

# OBJETIVOS DESTA RODADA

Esta é a rodada {current_round} de {max_rounds}. Foco em:
1. Refinar a análise com base em feedback anterior
2. Aprofundar debates entre executivos
3. Buscar consenso em pontos divergentes
4. Fazer perguntas de esclarecimento ao usuário se necessário
5. Propor ajustes ou melhorias ao documento
"""
    else:
        prompt += """

# OBJETIVOS DESTA RODADA FINAL

Esta é a ÚLTIMA rodada de análise. Foco em:
1. Consolidar todas as análises
2. Finalizar debates pendentes
3. Apresentar consenso da mesa executiva
4. Fornecer recomendações finais claras e acionáveis
5. Sugerir versão final ou revisões do documento
"""

    # Cria o team
    config = st.session_state.config

    with st.spinner(f"🤖 Mesa executiva trabalhando na rodada {current_round}... Isso pode levar alguns minutos."):
        try:
            team = create_executive_board_team(
                selected_agents=st.session_state.selected_agents,
                api_key=config.get_api_key(),
                model_id=st.session_state.get('model_option', 'gpt-4o-mini'),
                knowledge=st.session_state.knowledge,
                round_number=current_round,
                total_rounds=max_rounds,
            )

            response = team.run(prompt, stream=False)

            # Salva no histórico
            analysis_data = {
                'round': current_round,
                'timestamp': datetime.now().isoformat(),
                'agents': st.session_state.selected_agents,
                'summary': response.content,
            }

            st.session_state.analysis_history.append(analysis_data)

            # Exibe resultado
            st.success(f"✅ Rodada {current_round} concluída!")

            with st.expander(f"📊 Resultado da Rodada {current_round}", expanded=True):
                st.markdown(response.content)

            # Área para respostas do usuário
            st.markdown("### 💬 Sua Resposta")
            st.markdown("Se a mesa fez perguntas, responda abaixo antes de continuar para a próxima rodada:")

            user_answer = st.text_area(
                "Suas respostas e esclarecimentos:",
                height=150,
                key=f"user_response_{current_round}",
                placeholder="Responda às perguntas dos executivos aqui..."
            )

            if st.button("📝 Adicionar Resposta", key=f"add_response_{current_round}"):
                if user_answer.strip():
                    st.session_state.user_responses.append({
                        'round': current_round,
                        'question': "Perguntas da rodada " + str(current_round),
                        'answer': user_answer
                    })
                    st.success("✅ Resposta adicionada! Continue para a próxima rodada.")

            # Verifica se deve continuar
            if current_round < max_rounds:
                st.info(f"▶️ Clique em 'Continuar Rodada {current_round + 1}' acima para prosseguir")
            else:
                st.success("🎉 Análise completa! Todas as rodadas foram concluídas.")

                if st.button("📄 Gerar Relatório Final Consolidado", type="primary"):
                    generate_final_report()

        except Exception as e:
            st.error(f"❌ Erro na análise: {str(e)}")


def generate_final_report():
    """Gera relatório final consolidado"""

    st.markdown("---")
    st.markdown("## 📋 Relatório Final Consolidado")

    report = f"""
# RELATÓRIO FINAL DE ANÁLISE MULTIDISCIPLINAR

**Documento:** {st.session_state.document_name}
**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Rodadas de Análise:** {st.session_state.current_round}
**Mesa Executiva:** {', '.join([EXECUTIVE_AGENTS[a]['name'] for a in st.session_state.selected_agents])}

---

"""

    # Adiciona cada rodada
    for analysis in st.session_state.analysis_history:
        report += f"\n## Rodada {analysis['round']}\n\n"
        report += f"**Data:** {analysis['timestamp']}\n\n"
        report += analysis['summary']
        report += "\n\n---\n\n"

    # Adiciona respostas do usuário
    if st.session_state.user_responses:
        report += "\n## Esclarecimentos do Usuário\n\n"
        for resp in st.session_state.user_responses:
            report += f"**Rodada {resp['round']}**\n\n"
            report += f"{resp['answer']}\n\n"
        report += "---\n\n"

    # Exibe
    st.markdown(report)

    # Botão de download
    st.download_button(
        label="📥 Download Relatório (Markdown)",
        data=report,
        file_name=f"relatorio_analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )


def render_history():
    """Renderiza histórico de análises"""

    st.subheader("📚 Histórico de Rodadas")

    if not st.session_state.analysis_history:
        st.info("📭 Nenhuma análise realizada ainda")
        return

    for analysis in reversed(st.session_state.analysis_history):
        agents_names = [EXECUTIVE_AGENTS[a]['emoji'] for a in analysis['agents']]

        with st.expander(
            f"🔄 Rodada {analysis['round']} - {' '.join(agents_names)}",
            expanded=False
        ):
            st.markdown(f"**Data:** {analysis['timestamp']}")
            st.markdown("---")
            st.markdown(analysis['summary'])


def main():
    """Função principal"""

    # Config
    st.set_page_config(
        page_title="Executive Board Analyzer",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # Header
    st.title("🏢 Executive Board Document Analyzer")
    st.markdown("### Análise Multidisciplinar com Mesa Executiva de Agentes IA")
    st.markdown("---")

    # Sidebar
    render_sidebar()

    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Análise",
        "👥 Mesa Executiva",
        "📚 Histórico",
        "❓ Ajuda"
    ])

    with tab1:
        render_document_upload()
        st.markdown("---")
        render_analysis_section()

    with tab2:
        render_agent_selector()

        st.markdown("---")
        st.subheader("📖 Sobre os Executivos")

        for key, agent_def in EXECUTIVE_AGENTS.items():
            with st.expander(f"{agent_def['emoji']} {agent_def['name']}"):
                st.markdown(f"**Função:** {agent_def['role']}")
                st.markdown(f"**Foco:** {agent_def['description']}")

    with tab3:
        render_history()

    with tab4:
        st.markdown("""
## 🚀 Como Usar

### 1. Configurar API
- Configure sua chave OpenAI na barra lateral
- Escolha o modelo (recomendado: gpt-4o-mini para começar)

### 2. Selecionar Mesa Executiva
- Na aba "Mesa Executiva", selecione os executivos que participarão
- Cada executivo traz uma perspectiva única:
  - **CEO**: Visão estratégica e impacto no negócio
  - **CFO**: Análise financeira e fiscal
  - **DPO**: Proteção de dados e LGPD
  - **CISO**: Segurança da informação
  - **Legal**: Aspectos jurídicos e contratuais
  - **CTO**: Viabilidade técnica
  - **COO**: Operações e processos
  - **CHRO**: Impacto em pessoas e RH
  - **CMO**: Marca e comunicação
  - **CCO**: Compliance e ética

### 3. Carregar Documento
- Faça upload ou cole o documento
- Pode ser contrato, política, procedimento, etc.

### 4. Executar Análise
- Defina quantas rodadas de análise deseja
- Clique em "Iniciar Análise"
- Aguarde a mesa executiva trabalhar

### 5. Interagir
- Leia as análises de cada executivo
- Responda perguntas que a mesa fizer
- Continue para próximas rodadas
- Os executivos debaterão entre si e refinarão análises

### 6. Relatório Final
- Ao final, gere o relatório consolidado
- Faça download para seus registros

## 💡 Diferenciais

✅ **Múltiplas perspectivas** - Análise sob diferentes ângulos executivos
✅ **Debate colaborativo** - Agentes discutem e refinam ideias
✅ **Interação com usuário** - Mesa pode fazer perguntas para esclarecer
✅ **Análise iterativa** - Múltiplas rodadas de refinamento
✅ **RAG opcional** - Contexto de documentos anteriores
✅ **Relatório completo** - Consolidação de todas as análises

## 🎯 Casos de Uso

- **Contratos**: Análise multidisciplinar antes de assinar
- **Políticas**: Validação por múltiplas áreas
- **Projetos**: Avaliação de viabilidade
- **Compliance**: Verificação regulatória completa
- **Estratégia**: Análise de planos estratégicos

## 🔐 Privacidade

- Chave API salva em: `~/.executive_board_analyzer/config.json`
- Documentos processados apenas na sessão
- Nada enviado além da OpenAI API

---

**Desenvolvido com ❤️ usando Agno Framework**
        """)


if __name__ == "__main__":
    main()

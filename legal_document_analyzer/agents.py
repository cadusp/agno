"""
Time de agentes especializados para análise de documentos jurídicos
"""
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.openai import OpenAIEmbedder
from typing import Optional


def create_legal_analysis_team(
    api_key: str,
    knowledge: Optional[Knowledge] = None,
    model_id: str = "gpt-4o-mini"
) -> Team:
    """
    Cria um time de agentes especializados em análise jurídica

    Args:
        api_key: Chave API da OpenAI
        knowledge: Base de conhecimento opcional para RAG
        model_id: ID do modelo OpenAI a ser usado

    Returns:
        Team: Time de agentes configurado
    """

    # Agente de Análise de Contratos
    contract_analyst = Agent(
        name="Analista de Contratos",
        role="Especialista em análise e revisão de contratos",
        model=OpenAIChat(id=model_id, api_key=api_key),
        instructions=[
            "Você é um especialista em análise de contratos legais.",
            "Sua função é revisar contratos e identificar:",
            "- Cláusulas potencialmente problemáticas",
            "- Obrigações e direitos das partes",
            "- Prazos e condições importantes",
            "- Riscos legais e comerciais",
            "- Sugestões de melhorias ou ajustes",
            "Forneça análises detalhadas, precisas e em português.",
        ],
        knowledge=knowledge,
        search_knowledge=True if knowledge else False,
        markdown=True,
    )

    # Agente de Conformidade Legal
    compliance_agent = Agent(
        name="Agente de Conformidade",
        role="Especialista em conformidade legal e regulatória",
        model=OpenAIChat(id=model_id, api_key=api_key),
        instructions=[
            "Você é um especialista em conformidade legal e regulatória.",
            "Sua função é verificar:",
            "- Conformidade com leis e regulamentos aplicáveis",
            "- LGPD (Lei Geral de Proteção de Dados)",
            "- Código de Defesa do Consumidor",
            "- Legislação trabalhista",
            "- Normas setoriais específicas",
            "- Requisitos de compliance corporativo",
            "Identifique possíveis violações e recomende ações corretivas.",
        ],
        knowledge=knowledge,
        search_knowledge=True if knowledge else False,
        markdown=True,
    )

    # Agente de Análise de Políticas
    policy_analyst = Agent(
        name="Analista de Políticas",
        role="Especialista em análise de políticas corporativas",
        model=OpenAIChat(id=model_id, api_key=api_key),
        instructions=[
            "Você é um especialista em políticas corporativas.",
            "Sua função é avaliar:",
            "- Clareza e objetividade das políticas",
            "- Alinhamento com melhores práticas de mercado",
            "- Consistência interna e com outras políticas",
            "- Aplicabilidade prática",
            "- Proteção adequada para a organização",
            "- Equilíbrio entre direitos e deveres",
            "Sugira melhorias para tornar as políticas mais efetivas.",
        ],
        knowledge=knowledge,
        search_knowledge=True if knowledge else False,
        markdown=True,
    )

    # Agente de Resumo Executivo
    executive_summary_agent = Agent(
        name="Especialista em Resumos Executivos",
        role="Especialista em síntese e comunicação executiva",
        model=OpenAIChat(id=model_id, api_key=api_key),
        instructions=[
            "Você é um especialista em criar resumos executivos claros e concisos.",
            "Sua função é:",
            "- Sintetizar análises complexas em pontos-chave",
            "- Destacar riscos e oportunidades principais",
            "- Fornecer recomendações acionáveis",
            "- Usar linguagem clara e acessível",
            "- Organizar informações por ordem de importância",
            "- Criar sumários executivos que facilitem tomada de decisão",
        ],
        markdown=True,
    )

    # Agente de Identificação de Riscos
    risk_analyst = Agent(
        name="Analista de Riscos Jurídicos",
        role="Especialista em identificação e avaliação de riscos legais",
        model=OpenAIChat(id=model_id, api_key=api_key),
        instructions=[
            "Você é um especialista em identificação de riscos jurídicos.",
            "Sua função é:",
            "- Identificar riscos legais, financeiros e reputacionais",
            "- Classificar riscos por severidade (alto, médio, baixo)",
            "- Avaliar probabilidade e impacto de cada risco",
            "- Sugerir estratégias de mitigação",
            "- Identificar exposições ocultas",
            "- Priorizar ações de gestão de risco",
        ],
        knowledge=knowledge,
        search_knowledge=True if knowledge else False,
        markdown=True,
    )

    # Cria o time com um líder coordenador
    team = Team(
        name="Time de Análise Jurídica",
        model=OpenAIChat(id=model_id, api_key=api_key),
        members=[
            contract_analyst,
            compliance_agent,
            policy_analyst,
            risk_analyst,
            executive_summary_agent,
        ],
        instructions=[
            "Você é o coordenador de um time de especialistas em análise jurídica.",
            "Sua função é:",
            "- Delegar tarefas aos especialistas apropriados",
            "- Integrar as análises de diferentes especialistas",
            "- Garantir análise completa e multidimensional",
            "- Apresentar resultados de forma clara e organizada",
            "- Priorizar insights mais relevantes",
            "Sempre forneça análises em português do Brasil.",
        ],
        markdown=True,
        show_members_responses=True,
        delegate_task_to_all_members=False,
    )

    return team


def create_knowledge_base(api_key: str, persist_directory: str = "./chroma_db") -> Knowledge:
    """
    Cria uma base de conhecimento com embeddings OpenAI

    Args:
        api_key: Chave API da OpenAI
        persist_directory: Diretório para persistir o banco vetorial

    Returns:
        Knowledge: Base de conhecimento configurada
    """
    embedder = OpenAIEmbedder(
        id="text-embedding-3-small",
        api_key=api_key,
        dimensions=1536,
    )

    vector_db = ChromaDb(
        collection="legal_documents",
        path=persist_directory,
        embedder=embedder,
    )

    knowledge = Knowledge(
        vector_db=vector_db,
        num_documents=5,  # Número de documentos para recuperar no RAG
    )

    return knowledge

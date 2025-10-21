"""
Complete Agent Library - Master Aggregator
Biblioteca completa de agentes para cobertura de 100% das operações empresariais
Modelo padrão: gpt-4o-mini

Total de agentes: 30
- C-Level Executives: 11
- Management: 9
- Operational & Specialists: 10
"""

from agent_library import C_LEVEL_AGENTS, MANAGEMENT_AGENTS
from agent_library_extended import EXTENDED_C_LEVEL, TACTICAL_MANAGERS
from agent_library_operational import OPERATIONAL_AGENTS


# ============================================
# AGREGAÇÃO COMPLETA
# ============================================

def get_all_agents():
    """
    Retorna todos os agentes de todas as bibliotecas

    Returns:
        dict: Dicionário com todos os agentes {id: dados}
    """
    all_agents = {}

    # C-Level Executives (11 agentes)
    all_agents.update(C_LEVEL_AGENTS)
    all_agents.update(EXTENDED_C_LEVEL)

    # Management (9 agentes)
    all_agents.update(MANAGEMENT_AGENTS)
    all_agents.update(TACTICAL_MANAGERS)

    # Operational & Specialists (10 agentes)
    all_agents.update(OPERATIONAL_AGENTS)

    return all_agents


def get_agents_by_category():
    """
    Retorna agentes organizados por categoria

    Returns:
        dict: Dicionário com categorias e seus agentes
    """
    return {
        "C-Level Executives": {**C_LEVEL_AGENTS, **EXTENDED_C_LEVEL},
        "Management": {**MANAGEMENT_AGENTS, **TACTICAL_MANAGERS},
        "Operational & Specialists": OPERATIONAL_AGENTS
    }


def get_agent_by_id(agent_id: str):
    """
    Busca um agente específico pelo ID

    Args:
        agent_id (str): ID do agente

    Returns:
        dict: Dados do agente ou None se não encontrado
    """
    all_agents = get_all_agents()
    return all_agents.get(agent_id)


def search_agents(query: str):
    """
    Busca agentes por nome ou role

    Args:
        query (str): Termo de busca

    Returns:
        dict: Agentes que correspondem à busca
    """
    query_lower = query.lower()
    all_agents = get_all_agents()

    results = {}
    for agent_id, agent_data in all_agents.items():
        name_match = query_lower in agent_data['name'].lower()
        role_match = query_lower in agent_data['role'].lower()

        if name_match or role_match:
            results[agent_id] = agent_data

    return results


def get_statistics():
    """
    Retorna estatísticas da biblioteca de agentes

    Returns:
        dict: Estatísticas completas
    """
    categories = get_agents_by_category()

    return {
        "total_agents": len(get_all_agents()),
        "c_level": len(categories["C-Level Executives"]),
        "management": len(categories["Management"]),
        "operational": len(categories["Operational & Specialists"]),
        "categories": {
            cat: len(agents) for cat, agents in categories.items()
        }
    }


# ============================================
# DISPLAY E UTILIDADES
# ============================================

def print_all_agents():
    """Imprime todos os agentes organizados por categoria"""
    categories = get_agents_by_category()

    print("=" * 80)
    print("BIBLIOTECA COMPLETA DE AGENTES - 100% COBERTURA EMPRESARIAL")
    print("=" * 80)

    for category_name, agents in categories.items():
        print(f"\n{'='*80}")
        print(f"{category_name.upper()} ({len(agents)} agentes)")
        print(f"{'='*80}")

        for agent_id, agent_data in agents.items():
            print(f"\n{agent_data['emoji']} {agent_data['name']}")
            print(f"   Role: {agent_data['role']}")
            print(f"   ID: {agent_id}")
            print(f"   Modelo: {agent_data['model']}")

    stats = get_statistics()
    print("\n" + "=" * 80)
    print("ESTATÍSTICAS")
    print("=" * 80)
    print(f"Total de agentes: {stats['total_agents']}")
    for cat, count in stats['categories'].items():
        print(f"  - {cat}: {count}")


def export_agents_for_database():
    """
    Exporta agentes em formato pronto para inserção no banco de dados

    Returns:
        list: Lista de tuplas (id, name, role, system_message, emoji, model)
    """
    all_agents = get_all_agents()
    agents_list = []

    for agent_id, agent_data in all_agents.items():
        agents_list.append((
            agent_id,
            agent_data['name'],
            agent_data['role'],
            agent_data['system_message'],
            agent_data['emoji'],
            agent_data['model']
        ))

    return agents_list


# ============================================
# MAPEAMENTO DE ÁREAS
# ============================================

AREA_MAPPING = {
    "Estratégia e Governança": [
        "CEO", "CFO", "COO", "CRO", "CDO"
    ],
    "Tecnologia e Inovação": [
        "CTO", "CISO", "Gerente_TI", "Gerente_Inovacao", "Analista_BI"
    ],
    "Legal, Compliance e Riscos": [
        "DPO", "Legal_Officer", "CCO", "CRO", "Gerente_Riscos", "Gerente_Auditoria"
    ],
    "Operações e Supply Chain": [
        "COO", "Gerente_Supply_Chain", "Gerente_Compras", "Gerente_Facilities",
        "Gerente_Processos"
    ],
    "Pessoas e Cultura": [
        "CHRO", "Gerente_RH"
    ],
    "Marketing e Vendas": [
        "CMO", "Gerente_Vendas", "Gerente_Produto"
    ],
    "Cliente e Atendimento": [
        "Gerente_CS", "Gerente_Atendimento"
    ],
    "Finanças e Controles": [
        "CFO", "Gerente_Financeiro", "Gerente_Auditoria"
    ],
    "Qualidade e Excelência": [
        "Gerente_Qualidade", "Gerente_Processos"
    ],
    "Sustentabilidade e ESG": [
        "Especialista_ESG", "Gerente_Relacoes_Institucionais"
    ],
    "Projetos": [
        "Gerente_Projetos"
    ]
}


def get_agents_by_area(area: str):
    """
    Retorna agentes de uma área específica

    Args:
        area (str): Nome da área

    Returns:
        dict: Agentes da área
    """
    agent_ids = AREA_MAPPING.get(area, [])
    all_agents = get_all_agents()

    return {
        agent_id: all_agents[agent_id]
        for agent_id in agent_ids
        if agent_id in all_agents
    }


def suggest_team_for_task(task_description: str):
    """
    Sugere time de agentes com base na descrição da tarefa

    Args:
        task_description (str): Descrição da tarefa

    Returns:
        list: IDs dos agentes sugeridos
    """
    task_lower = task_description.lower()
    suggested = []

    # Mapeamento de palavras-chave para agentes
    keyword_mapping = {
        "contrato": ["Legal_Officer", "CFO", "DPO"],
        "segurança": ["CISO", "DPO", "Gerente_Riscos"],
        "dados": ["DPO", "CDO", "CISO", "Analista_BI"],
        "financeiro": ["CFO", "Gerente_Financeiro", "Gerente_Auditoria"],
        "tecnologia": ["CTO", "CISO", "Gerente_TI"],
        "marketing": ["CMO", "Gerente_Vendas"],
        "produto": ["Gerente_Produto", "CMO", "CTO"],
        "compliance": ["CCO", "Legal_Officer", "DPO"],
        "risco": ["CRO", "Gerente_Riscos", "Gerente_Auditoria"],
        "sustentabilidade": ["Especialista_ESG"],
        "cliente": ["Gerente_CS", "Gerente_Atendimento", "CMO"],
        "processo": ["Gerente_Processos", "Gerente_Qualidade"],
        "supply": ["Gerente_Supply_Chain", "Gerente_Compras"],
        "projeto": ["Gerente_Projetos"],
        "inovação": ["Gerente_Inovacao", "CTO"],
        "rh": ["CHRO"],
        "auditoria": ["Gerente_Auditoria", "CFO"]
    }

    for keyword, agents in keyword_mapping.items():
        if keyword in task_lower:
            suggested.extend(agents)

    # Remover duplicatas mantendo ordem
    seen = set()
    unique_suggested = []
    for agent_id in suggested:
        if agent_id not in seen:
            seen.add(agent_id)
            unique_suggested.append(agent_id)

    # Se não encontrou nada, sugere time executivo básico
    if not unique_suggested:
        unique_suggested = ["CEO", "CFO", "Legal_Officer"]

    return unique_suggested


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print_all_agents()

    print("\n" + "=" * 80)
    print("EXEMPLOS DE USO")
    print("=" * 80)

    # Exemplo 1: Busca
    print("\n1. Busca por 'segurança':")
    results = search_agents("segurança")
    for agent_id, agent_data in results.items():
        print(f"   {agent_data['emoji']} {agent_data['name']}")

    # Exemplo 2: Agentes por área
    print("\n2. Agentes da área 'Tecnologia e Inovação':")
    tech_agents = get_agents_by_area("Tecnologia e Inovação")
    for agent_id, agent_data in tech_agents.items():
        print(f"   {agent_data['emoji']} {agent_data['name']}")

    # Exemplo 3: Sugestão de time
    print("\n3. Time sugerido para 'Análise de contrato de dados':")
    suggested = suggest_team_for_task("Análise de contrato de dados")
    all_agents = get_all_agents()
    for agent_id in suggested:
        if agent_id in all_agents:
            print(f"   {all_agents[agent_id]['emoji']} {all_agents[agent_id]['name']}")

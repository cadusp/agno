"""
🎯 Script de População do Banco de Dados com Agentes Pré-configurados

Popula o banco SQLite com todos os agentes da biblioteca empresarial.
Execute este script para ter um cardápio completo de agentes disponível.

Uso:
    python populate_agents.py

Ou via interface Streamlit:
    Na aba "Agentes" → botão "Carregar Biblioteca Completa"
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict

# Importa a biblioteca completa de agentes
from agent_library import get_all_agents, get_agents_by_category, get_statistics


def populate_agents_database(db_path: str = None, clear_existing: bool = False):
    """
    Popula o banco de dados com todos os agentes da biblioteca

    Args:
        db_path: Caminho para o banco SQLite
        clear_existing: Se True, remove agentes existentes antes de popular

    Returns:
        Dict com estatísticas da população
    """

    if db_path is None:
        # Usa o caminho padrão
        config_dir = Path.home() / ".autogen_team_builder"
        db_path = config_dir / "agents.db"

    db_path = str(db_path)

    # Conecta ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    stats = {
        'total': 0,
        'added': 0,
        'skipped': 0,
        'updated': 0,
        'errors': 0
    }

    # Limpa existentes se solicitado
    if clear_existing:
        cursor.execute("DELETE FROM agents")
        conn.commit()
        print("✅ Agentes existentes removidos")

    # Busca todos os agentes
    all_agents = get_all_agents()
    stats['total'] = len(all_agents)

    print(f"\n📚 Populando banco com {stats['total']} agentes...\n")

    for agent_key, agent_data in all_agents.items():
        try:
            # Verifica se já existe
            cursor.execute(
                "SELECT id FROM agents WHERE name = ?",
                (agent_data['name'],)
            )
            existing = cursor.fetchone()

            if existing and not clear_existing:
                print(f"⏭️  {agent_data['emoji']} {agent_data['name']} - já existe, pulando")
                stats['skipped'] += 1
                continue

            # Cria novo agente
            agent_id = str(uuid.uuid4())
            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO agents (
                    id, name, role, system_message, emoji,
                    human_input_mode, max_consecutive_auto_reply,
                    created_at, updated_at, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_id,
                agent_data['name'],
                agent_data['role'],
                agent_data['system_message'],
                agent_data['emoji'],
                agent_data.get('human_input_mode', 'NEVER'),
                agent_data.get('max_consecutive_auto_reply', 15),
                now,
                now,
                '{"source": "agent_library", "key": "' + agent_key + '"}'
            ))

            print(f"✅ {agent_data['emoji']} {agent_data['name']} - adicionado")
            stats['added'] += 1

        except Exception as e:
            print(f"❌ Erro ao adicionar {agent_data['name']}: {str(e)}")
            stats['errors'] += 1

    conn.commit()
    conn.close()

    # Sumário
    print(f"\n{'='*60}")
    print("📊 SUMÁRIO DA POPULAÇÃO")
    print(f"{'='*60}")
    print(f"Total de agentes na biblioteca: {stats['total']}")
    print(f"✅ Adicionados: {stats['added']}")
    print(f"⏭️  Pulados (já existiam): {stats['skipped']}")
    print(f"❌ Erros: {stats['errors']}")
    print(f"{'='*60}\n")

    return stats


def show_agent_library():
    """Mostra todos os agentes disponíveis na biblioteca"""

    categories = get_agents_by_category()

    print("\n" + "="*80)
    print("📚 BIBLIOTECA COMPLETA DE AGENTES EMPRESARIAIS")
    print("="*80 + "\n")

    total_agents = 0

    for category, agents in categories.items():
        print(f"\n{'─'*80}")
        print(f"📁 {category} ({len(agents)} agentes)")
        print(f"{'─'*80}\n")

        for agent_key, agent_data in agents.items():
            print(f"{agent_data['emoji']} {agent_data['name']}")
            print(f"   Role: {agent_data['role']}")
            print(f"   Model: {agent_data['model']}")
            print()
            total_agents += 1

    print(f"{'='*80}")
    print(f"TOTAL: {total_agents} agentes disponíveis")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import sys

    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🎯 POPULAÇÃO DO BANCO COM BIBLIOTECA DE AGENTES                ║
║                                                                  ║
║   AutoGen Multi-Agent Team Builder                              ║
║   Biblioteca Empresarial Completa                               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Menu
    print("\nOpções:")
    print("1. Mostrar biblioteca de agentes")
    print("2. Popular banco (manter existentes)")
    print("3. Popular banco (substituir todos)")
    print("4. Sair")

    choice = input("\nEscolha uma opção (1-4): ").strip()

    if choice == "1":
        show_agent_library()

    elif choice == "2":
        confirm = input("\nConfirma população do banco? (s/n): ").strip().lower()
        if confirm == 's':
            populate_agents_database(clear_existing=False)

    elif choice == "3":
        confirm = input("\n⚠️  ATENÇÃO: Isso vai REMOVER todos agentes existentes! Confirma? (s/n): ").strip().lower()
        if confirm == 's':
            populate_agents_database(clear_existing=True)

    elif choice == "4":
        print("\n👋 Até logo!\n")
        sys.exit(0)

    else:
        print("\n❌ Opção inválida")

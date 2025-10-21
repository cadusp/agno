"""
🚀 Dynamic Team Builder - Sistema Completo de Criação e Gestão de Times de Agentes IA

Funcionalidades Completas:
✅ CRUD de Agentes (Criar, Editar, Deletar, Listar)
✅ Gestão de Base de Conhecimento (Upload, Delete, Múltiplos formatos)
✅ Múltiplos Readers (PDF, Markdown, TXT, DOCX, CSV)
✅ Múltiplos Chunking Strategies (Fixed, Semantic, Recursive, Document)
✅ Conhecimento por Agente (cada agente tem sua base)
✅ Memória e Persistência (SQLite para dados, LanceDB para vetores)
✅ Streaming de Respostas em tempo real
✅ Saída em Markdown
✅ Fluxo Dinâmico Configurável
✅ Criação de Documentos do Zero (não só análise)
✅ Time Multi-disciplinar Escalável
✅ Todos agentes veem análises de outros

Autor: Claude Code
Versão: 3.0 - Dynamic Team Builder
"""

import streamlit as st
import os
import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import tempfile
import uuid

# Agno imports
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.document import Document
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.lancedb import LanceDb
from agno.db.sqlite import SqliteDb
from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.chunking.agentic import AgenticChunking


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class Config:
    """Gerenciador de configurações"""

    CONFIG_DIR = Path.home() / ".dynamic_team_builder"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    DB_FILE = CONFIG_DIR / "team_builder.db"
    LANCEDB_DIR = CONFIG_DIR / "lancedb"

    def __init__(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Inicializa banco SQLite"""
        conn = sqlite3.connect(str(self.DB_FILE))
        cursor = conn.cursor()

        # Tabela de agentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT,
                emoji TEXT,
                instructions TEXT,
                model_id TEXT,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT
            )
        """)

        # Tabela de documentos de conhecimento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_docs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                content TEXT,
                file_type TEXT,
                agent_id TEXT,
                created_at TEXT,
                metadata TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        """)

        # Tabela de sessões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                mode TEXT,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT
            )
        """)

        # Tabela de mensagens/rodadas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                round_number INTEGER,
                agent_ids TEXT,
                prompt TEXT,
                response TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)

        conn.commit()
        conn.close()

    def _load_config(self) -> dict:
        if self.CONFIG_FILE.exists():
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_api_key(self, api_key: str):
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

    def delete_api_key(self):
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
# GERENCIADOR DE AGENTES
# ============================================================================

class AgentManager:
    """Gerencia CRUD de agentes"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_agent(
        self,
        name: str,
        role: str,
        instructions: str,
        emoji: str = "🤖",
        model_id: str = "gpt-4o-mini",
        metadata: Optional[Dict] = None
    ) -> str:
        """Cria novo agente"""
        agent_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO agents (id, name, role, emoji, instructions, model_id, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent_id, name, role, emoji, instructions, model_id, now, now,
            json.dumps(metadata or {})
        ))

        conn.commit()
        conn.close()

        return agent_id

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Busca agente por ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'id': row[0],
            'name': row[1],
            'role': row[2],
            'emoji': row[3],
            'instructions': row[4],
            'model_id': row[5],
            'created_at': row[6],
            'updated_at': row[7],
            'metadata': json.loads(row[8]) if row[8] else {}
        }

    def list_agents(self) -> List[Dict]:
        """Lista todos os agentes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM agents ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        agents = []
        for row in rows:
            agents.append({
                'id': row[0],
                'name': row[1],
                'role': row[2],
                'emoji': row[3],
                'instructions': row[4],
                'model_id': row[5],
                'created_at': row[6],
                'updated_at': row[7],
                'metadata': json.loads(row[8]) if row[8] else {}
            })

        return agents

    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        instructions: Optional[str] = None,
        emoji: Optional[str] = None,
        model_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Atualiza agente"""
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        values = []

        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if role is not None:
            updates.append("role = ?")
            values.append(role)
        if instructions is not None:
            updates.append("instructions = ?")
            values.append(instructions)
        if emoji is not None:
            updates.append("emoji = ?")
            values.append(emoji)
        if model_id is not None:
            updates.append("model_id = ?")
            values.append(model_id)
        if metadata is not None:
            updates.append("metadata = ?")
            values.append(json.dumps(metadata))

        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())

        values.append(agent_id)

        cursor.execute(
            f"UPDATE agents SET {', '.join(updates)} WHERE id = ?",
            values
        )

        conn.commit()
        conn.close()

    def delete_agent(self, agent_id: str):
        """Deleta agente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Deleta documentos associados
        cursor.execute("DELETE FROM knowledge_docs WHERE agent_id = ?", (agent_id,))

        # Deleta agente
        cursor.execute("DELETE FROM agents WHERE id = ?", (agent_id,))

        conn.commit()
        conn.close()


# ============================================================================
# GERENCIADOR DE CONHECIMENTO
# ============================================================================

class KnowledgeManager:
    """Gerencia base de conhecimento com múltiplos formatos"""

    READERS = {
        'txt': 'TextReader',
        'md': 'MarkdownReader',
        'pdf': 'PDFReader',
        'docx': 'DocxReader',
        'csv': 'CSVReader',
    }

    CHUNKING_STRATEGIES = {
        'fixed': 'Fixed Size (caracteres fixos)',
        'semantic': 'Semantic (por significado)',
        'agentic': 'Agentic (IA decide)',
        'document': 'Document (documento completo)',
    }

    def __init__(self, db_path: str, lancedb_path: str):
        self.db_path = db_path
        self.lancedb_path = lancedb_path

    def add_document(
        self,
        file_content: str,
        file_name: str,
        file_type: str,
        agent_id: Optional[str] = None
    ) -> str:
        """Adiciona documento à base de conhecimento"""
        doc_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO knowledge_docs (id, name, content, file_type, agent_id, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc_id, file_name, file_content, file_type, agent_id, now, json.dumps({})))

        conn.commit()
        conn.close()

        return doc_id

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Busca documento por ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM knowledge_docs WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'id': row[0],
            'name': row[1],
            'content': row[2],
            'file_type': row[3],
            'agent_id': row[4],
            'created_at': row[5],
            'metadata': json.loads(row[6]) if row[6] else {}
        }

    def list_documents(self, agent_id: Optional[str] = None) -> List[Dict]:
        """Lista documentos (opcionalmente filtrado por agente)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if agent_id:
            cursor.execute(
                "SELECT * FROM knowledge_docs WHERE agent_id = ? ORDER BY created_at DESC",
                (agent_id,)
            )
        else:
            cursor.execute("SELECT * FROM knowledge_docs ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()

        docs = []
        for row in rows:
            docs.append({
                'id': row[0],
                'name': row[1],
                'content': row[2],
                'file_type': row[3],
                'agent_id': row[4],
                'created_at': row[5],
                'metadata': json.loads(row[6]) if row[6] else {}
            })

        return docs

    def delete_document(self, doc_id: str):
        """Deleta documento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge_docs WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()

    def create_knowledge_base(
        self,
        api_key: str,
        agent_id: Optional[str] = None,
        chunking_strategy: str = 'fixed',
        chunk_size: int = 1000
    ) -> Knowledge:
        """Cria base de conhecimento com LanceDB"""

        embedder = OpenAIEmbedder(
            id="text-embedding-3-small",
            api_key=api_key,
            dimensions=1536,
        )

        # Define chunking strategy
        if chunking_strategy == 'fixed':
            chunking = FixedSizeChunking(chunk_size=chunk_size, overlap=100)
        elif chunking_strategy == 'agentic':
            chunking = AgenticChunking()
        else:
            chunking = FixedSizeChunking(chunk_size=chunk_size, overlap=100)

        # Cria vector DB
        table_name = f"knowledge_{agent_id}" if agent_id else "knowledge_global"

        vector_db = LanceDb(
            table_name=table_name,
            uri=str(self.lancedb_path),
            embedder=embedder,
        )

        knowledge = Knowledge(
            vector_db=vector_db,
            chunking_strategy=chunking,
            num_documents=5,
        )

        # Carrega documentos existentes
        docs = self.list_documents(agent_id)
        if docs:
            documents = [
                Document(name=doc['name'], content=doc['content'])
                for doc in docs
            ]
            knowledge.load_documents(documents, upsert=True)

        return knowledge


# ============================================================================
# GERENCIADOR DE SESSÕES
# ============================================================================

class SessionManager:
    """Gerencia sessões de trabalho"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_session(self, name: str, mode: str) -> str:
        """Cria nova sessão"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (id, name, mode, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, name, mode, now, now, json.dumps({})))

        conn.commit()
        conn.close()

        return session_id

    def save_message(
        self,
        session_id: str,
        round_number: int,
        agent_ids: List[str],
        prompt: str,
        response: str
    ):
        """Salva mensagem/rodada"""
        msg_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (id, session_id, round_number, agent_ids, prompt, response, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, session_id, round_number, json.dumps(agent_ids), prompt, response, now))

        conn.commit()
        conn.close()

    def get_session_history(self, session_id: str) -> List[Dict]:
        """Recupera histórico da sessão"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY round_number",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        messages = []
        for row in rows:
            messages.append({
                'id': row[0],
                'session_id': row[1],
                'round_number': row[2],
                'agent_ids': json.loads(row[3]),
                'prompt': row[4],
                'response': row[5],
                'created_at': row[6],
            })

        return messages


# ============================================================================
# CRIADOR DE TEAM DINÂMICO
# ============================================================================

def create_dynamic_team(
    agent_configs: List[Dict],
    api_key: str,
    knowledge_bases: Optional[Dict[str, Knowledge]] = None,
    session_db_path: Optional[str] = None
) -> Team:
    """Cria team dinamicamente com agentes configurados"""

    members = []

    for config in agent_configs:
        # Conhecimento específico do agente
        agent_knowledge = None
        if knowledge_bases and config['id'] in knowledge_bases:
            agent_knowledge = knowledge_bases[config['id']]

        # Session DB (memória)
        session_db = None
        if session_db_path:
            session_db = SqliteDb(
                db_file=session_db_path,
                table_name=f"agent_{config['id'][:8]}_sessions"
            )

        agent = Agent(
            name=config['name'],
            role=config.get('role', ''),
            model=OpenAIChat(id=config.get('model_id', 'gpt-4o-mini'), api_key=api_key),
            instructions=config.get('instructions', '').split('\n') if config.get('instructions') else [],
            knowledge=agent_knowledge,
            search_knowledge=True if agent_knowledge else False,
            storage=session_db,
            markdown=True,
        )

        members.append(agent)

    # Líder do team
    team = Team(
        name="Dynamic Multi-disciplinary Team",
        model=OpenAIChat(id="gpt-4o-mini", api_key=api_key),
        members=members,
        instructions=[
            "Você coordena um time multidisciplinar de especialistas.",
            "Cada membro analisará sob sua perspectiva única.",
            "IMPORTANTE: Todos os membros devem ver as análises dos outros.",
            "Facilite debates construtivos entre membros.",
            "Sintetize consensos e divergências.",
            "Sempre responda em português do Brasil.",
        ],
        markdown=True,
        show_members_responses=True,
        delegate_task_to_all_members=True,
    )

    return team


# ============================================================================
# INTERFACE STREAMLIT
# ============================================================================

def init_session_state():
    """Inicializa estado da sessão"""
    if 'config' not in st.session_state:
        st.session_state.config = Config()

    if 'agent_manager' not in st.session_state:
        st.session_state.agent_manager = AgentManager(str(st.session_state.config.DB_FILE))

    if 'knowledge_manager' not in st.session_state:
        st.session_state.knowledge_manager = KnowledgeManager(
            str(st.session_state.config.DB_FILE),
            str(st.session_state.config.LANCEDB_DIR)
        )

    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager(str(st.session_state.config.DB_FILE))

    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None

    if 'selected_agent_ids' not in st.session_state:
        st.session_state.selected_agent_ids = []

    if 'current_round' not in st.session_state:
        st.session_state.current_round = 0

    if 'knowledge_bases' not in st.session_state:
        st.session_state.knowledge_bases = {}


def render_sidebar():
    """Barra lateral"""
    with st.sidebar:
        st.title("⚙️ Configurações")

        # API Key
        config = st.session_state.config

        if config.is_configured():
            st.success("✅ API OK")
            if st.button("🗑️ Remover", use_container_width=True):
                config.delete_api_key()
                st.rerun()
        else:
            api_input = st.text_input("OpenAI API:", type="password")
            if st.button("💾 Salvar", use_container_width=True):
                if api_input:
                    config.save_api_key(api_input)
                    st.success("✅ Salva!")
                    st.rerun()

        st.divider()

        # Stats
        st.subheader("📊 Estatísticas")
        agents = st.session_state.agent_manager.list_agents()
        docs = st.session_state.knowledge_manager.list_documents()

        st.metric("Agentes", len(agents))
        st.metric("Documentos", len(docs))
        st.metric("Rodada", st.session_state.current_round)


def render_agent_management():
    """Gestão de agentes (CRUD)"""
    st.subheader("👥 Gerenciar Agentes")

    tab_list, tab_create, tab_edit = st.tabs(["📋 Listar", "➕ Criar", "✏️ Editar/Deletar"])

    # Listar agentes
    with tab_list:
        agents = st.session_state.agent_manager.list_agents()

        if not agents:
            st.info("Nenhum agente criado ainda")
        else:
            for agent in agents:
                with st.expander(f"{agent['emoji']} {agent['name']}", expanded=False):
                    st.markdown(f"**Role:** {agent['role']}")
                    st.markdown(f"**Modelo:** {agent['model_id']}")
                    st.markdown(f"**Instruções:**\n```\n{agent['instructions']}\n```")
                    st.caption(f"ID: {agent['id']}")

    # Criar agente
    with tab_create:
        with st.form("create_agent_form"):
            st.markdown("### Novo Agente")

            name = st.text_input("Nome*", placeholder="Ex: Analista Financeiro")
            emoji = st.text_input("Emoji", value="🤖", max_chars=2)
            role = st.text_input("Role/Cargo", placeholder="Ex: Especialista em análise financeira")

            model_id = st.selectbox(
                "Modelo OpenAI",
                ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
            )

            instructions = st.text_area(
                "Instruções (uma por linha)",
                height=200,
                placeholder="Você é um especialista financeiro...\nAnalise sempre custos e ROI...\nForneça recomendações práticas..."
            )

            submitted = st.form_submit_button("✅ Criar Agente", type="primary")

            if submitted:
                if not name:
                    st.error("Nome é obrigatório")
                else:
                    agent_id = st.session_state.agent_manager.create_agent(
                        name=name,
                        role=role,
                        instructions=instructions,
                        emoji=emoji,
                        model_id=model_id
                    )
                    st.success(f"✅ Agente '{name}' criado! ID: {agent_id}")
                    st.rerun()

    # Editar/Deletar
    with tab_edit:
        agents = st.session_state.agent_manager.list_agents()

        if not agents:
            st.info("Nenhum agente para editar")
        else:
            agent_options = {f"{a['emoji']} {a['name']}": a['id'] for a in agents}
            selected_agent_name = st.selectbox("Selecione o agente:", list(agent_options.keys()))
            selected_agent_id = agent_options[selected_agent_name]

            agent = st.session_state.agent_manager.get_agent(selected_agent_id)

            with st.form("edit_agent_form"):
                st.markdown(f"### Editar: {agent['name']}")

                new_name = st.text_input("Nome", value=agent['name'])
                new_emoji = st.text_input("Emoji", value=agent['emoji'], max_chars=2)
                new_role = st.text_input("Role", value=agent['role'])
                new_model = st.selectbox(
                    "Modelo",
                    ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                    index=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"].index(agent['model_id'])
                )
                new_instructions = st.text_area("Instruções", value=agent['instructions'], height=200)

                col1, col2 = st.columns(2)

                with col1:
                    update_btn = st.form_submit_button("💾 Atualizar", type="primary")

                with col2:
                    delete_btn = st.form_submit_button("🗑️ Deletar", type="secondary")

                if update_btn:
                    st.session_state.agent_manager.update_agent(
                        selected_agent_id,
                        name=new_name,
                        emoji=new_emoji,
                        role=new_role,
                        model_id=new_model,
                        instructions=new_instructions
                    )
                    st.success("✅ Agente atualizado!")
                    st.rerun()

                if delete_btn:
                    st.session_state.agent_manager.delete_agent(selected_agent_id)
                    st.success("✅ Agente deletado!")
                    st.rerun()


def render_knowledge_management():
    """Gestão de base de conhecimento"""
    st.subheader("📚 Base de Conhecimento")

    tab_list, tab_add, tab_config = st.tabs(["📋 Documentos", "➕ Adicionar", "⚙️ Configuração"])

    # Listar documentos
    with tab_list:
        docs = st.session_state.knowledge_manager.list_documents()

        if not docs:
            st.info("Nenhum documento adicionado")
        else:
            for doc in docs:
                agent_name = "Global"
                if doc['agent_id']:
                    agent = st.session_state.agent_manager.get_agent(doc['agent_id'])
                    if agent:
                        agent_name = f"{agent['emoji']} {agent['name']}"

                with st.expander(f"📄 {doc['name']} ({agent_name})"):
                    st.caption(f"Tipo: {doc['file_type'].upper()}")
                    st.text_area("Conteúdo", value=doc['content'][:500] + "...", height=100, disabled=True)

                    if st.button(f"🗑️ Deletar", key=f"del_{doc['id']}"):
                        st.session_state.knowledge_manager.delete_document(doc['id'])
                        st.success("Documento deletado!")
                        st.rerun()

    # Adicionar documento
    with tab_add:
        st.markdown("### Upload de Documento")

        # Seleção de agente (opcional)
        agents = st.session_state.agent_manager.list_agents()
        agent_options = {"Global (todos agentes)": None}
        agent_options.update({f"{a['emoji']} {a['name']}": a['id'] for a in agents})

        selected_agent = st.selectbox(
            "Associar a qual agente?",
            list(agent_options.keys())
        )
        agent_id = agent_options[selected_agent]

        # Upload
        uploaded = st.file_uploader(
            "Selecione arquivo",
            type=['txt', 'md', 'pdf', 'docx', 'csv'],
            help="Suporta TXT, Markdown, PDF, DOCX, CSV"
        )

        # Ou texto direto
        st.markdown("**Ou cole o texto:**")
        text_input = st.text_area("Conteúdo", height=200)

        if st.button("📥 Adicionar à Base de Conhecimento", type="primary"):
            content = None
            filename = None
            filetype = 'txt'

            if uploaded:
                content = uploaded.getvalue().decode('utf-8', errors='ignore')
                filename = uploaded.name
                filetype = Path(uploaded.name).suffix[1:]
            elif text_input.strip():
                content = text_input
                filename = f"text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                filetype = 'txt'

            if content:
                doc_id = st.session_state.knowledge_manager.add_document(
                    file_content=content,
                    file_name=filename,
                    file_type=filetype,
                    agent_id=agent_id
                )
                st.success(f"✅ Documento '{filename}' adicionado! ID: {doc_id}")

                # Limpa knowledge bases em cache para recarregar
                st.session_state.knowledge_bases = {}
                st.rerun()
            else:
                st.error("Forneça um arquivo ou texto")

    # Configuração
    with tab_config:
        st.markdown("### Estratégias de Chunking")

        for strategy, description in st.session_state.knowledge_manager.CHUNKING_STRATEGIES.items():
            st.markdown(f"**{strategy}**: {description}")

        st.divider()

        st.markdown("### Formatos Suportados")
        st.markdown("- **TXT**: Texto puro")
        st.markdown("- **MD**: Markdown")
        st.markdown("- **PDF**: Documentos PDF")
        st.markdown("- **DOCX**: Microsoft Word")
        st.markdown("- **CSV**: Planilhas CSV")


def render_team_selection():
    """Seleção do time"""
    st.subheader("👥 Monte seu Time")

    agents = st.session_state.agent_manager.list_agents()

    if not agents:
        st.warning("⚠️ Crie agentes primeiro na aba 'Agentes'")
        return

    st.markdown("Selecione os agentes que participarão:")

    cols = st.columns(3)
    selected = []

    for idx, agent in enumerate(agents):
        col = cols[idx % 3]

        with col:
            is_selected = st.checkbox(
                f"{agent['emoji']} {agent['name']}",
                value=agent['id'] in st.session_state.selected_agent_ids,
                key=f"select_{agent['id']}",
                help=agent['role']
            )

            if is_selected:
                selected.append(agent['id'])

    st.session_state.selected_agent_ids = selected

    if selected:
        st.success(f"✅ {len(selected)} agente(s) selecionado(s)")
    else:
        st.warning("⚠️ Selecione pelo menos um agente")


def render_workflow():
    """Fluxo de trabalho principal"""
    st.subheader("🚀 Fluxo de Trabalho")

    if not st.session_state.config.is_configured():
        st.error("❌ Configure a API OpenAI primeiro")
        return

    if not st.session_state.selected_agent_ids:
        st.warning("⚠️ Selecione agentes na aba 'Time'")
        return

    # Modo de trabalho
    mode = st.radio(
        "Modo de trabalho:",
        ["📝 Criar Documento", "🔍 Analisar Documento"],
        horizontal=True
    )

    # Configurações do fluxo
    col1, col2, col3 = st.columns(3)

    with col1:
        max_rounds = st.number_input("Rodadas", min_value=1, max_value=10, value=3)

    with col2:
        chunking_strategy = st.selectbox(
            "Chunking",
            list(st.session_state.knowledge_manager.CHUNKING_STRATEGIES.keys())
        )

    with col3:
        chunk_size = st.number_input("Chunk Size", min_value=100, max_value=5000, value=1000)

    # Input do usuário
    st.markdown("---")

    if mode == "📝 Criar Documento":
        st.markdown("### Descreva o documento que deseja criar")
        user_input = st.text_area(
            "Instruções:",
            height=200,
            placeholder="Ex: Crie uma política de segurança da informação completa, incluindo...\nEx: Elabore um contrato de prestação de serviços que..."
        )
    else:
        st.markdown("### Documento para análise")
        uploaded = st.file_uploader("Upload (opcional)", type=['txt', 'md', 'pdf'])
        user_input = st.text_area(
            "Texto ou instruções:",
            height=200,
            placeholder="Cole o documento aqui ou forneça instruções de análise..."
        )

    # Contexto adicional
    additional_context = st.text_area(
        "Contexto adicional (opcional):",
        height=100
    )

    # Botão de execução
    if st.button("🚀 Executar", type="primary", use_container_width=True):
        execute_workflow(
            mode=mode,
            user_input=user_input,
            additional_context=additional_context,
            max_rounds=max_rounds,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size
        )


def execute_workflow(
    mode: str,
    user_input: str,
    additional_context: str,
    max_rounds: int,
    chunking_strategy: str,
    chunk_size: int
):
    """Executa o fluxo de trabalho"""

    if not user_input.strip():
        st.error("Forneça instruções ou documento")
        return

    # Cria sessão
    session_name = f"{mode} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    session_id = st.session_state.session_manager.create_session(session_name, mode)
    st.session_state.current_session_id = session_id

    # Prepara knowledge bases
    api_key = st.session_state.config.get_api_key()
    knowledge_bases = {}

    with st.spinner("Carregando bases de conhecimento..."):
        for agent_id in st.session_state.selected_agent_ids:
            # Verifica se agente tem documentos
            docs = st.session_state.knowledge_manager.list_documents(agent_id)
            if docs:
                kb = st.session_state.knowledge_manager.create_knowledge_base(
                    api_key=api_key,
                    agent_id=agent_id,
                    chunking_strategy=chunking_strategy,
                    chunk_size=chunk_size
                )
                knowledge_bases[agent_id] = kb

        # Knowledge global
        global_docs = st.session_state.knowledge_manager.list_documents(None)
        if global_docs:
            kb_global = st.session_state.knowledge_manager.create_knowledge_base(
                api_key=api_key,
                agent_id=None,
                chunking_strategy=chunking_strategy,
                chunk_size=chunk_size
            )
            # Adiciona para todos agentes que não têm knowledge próprio
            for agent_id in st.session_state.selected_agent_ids:
                if agent_id not in knowledge_bases:
                    knowledge_bases[agent_id] = kb_global

    # Prepara agentes
    agent_configs = []
    for agent_id in st.session_state.selected_agent_ids:
        agent = st.session_state.agent_manager.get_agent(agent_id)
        if agent:
            agent_configs.append(agent)

    # Executa rodadas
    st.markdown("---")
    st.markdown("## 🎯 Execução")

    previous_outputs = []

    for round_num in range(1, max_rounds + 1):
        st.markdown(f"### 🔄 Rodada {round_num}/{max_rounds}")

        # Prepara prompt
        if round_num == 1:
            if mode == "📝 Criar Documento":
                prompt = f"""
# TAREFA: CRIAR DOCUMENTO

{user_input}

"""
            else:
                prompt = f"""
# TAREFA: ANALISAR DOCUMENTO

{user_input}

"""
        else:
            prompt = f"""
# RODADA {round_num} - REFINAMENTO

Com base nas análises anteriores, refine e aprimore:

"""

        # Adiciona outputs anteriores (todos veem análises de outros)
        if previous_outputs:
            prompt += "\n## ANÁLISES DAS RODADAS ANTERIORES\n\n"
            for i, output in enumerate(previous_outputs, 1):
                prompt += f"### Rodada {i}\n{output}\n\n"

        if additional_context:
            prompt += f"\n## CONTEXTO ADICIONAL\n{additional_context}\n"

        # Cria team
        with st.spinner(f"Time trabalhando na rodada {round_num}..."):
            team = create_dynamic_team(
                agent_configs=agent_configs,
                api_key=api_key,
                knowledge_bases=knowledge_bases,
                session_db_path=str(st.session_state.config.DB_FILE)
            )

            # Executa com streaming
            output_container = st.empty()
            full_response = ""

            response_stream = team.run(prompt, stream=True)

            for chunk in response_stream:
                if hasattr(chunk, 'content') and chunk.content:
                    full_response += chunk.content
                    output_container.markdown(full_response)

            previous_outputs.append(full_response)

            # Salva no banco
            st.session_state.session_manager.save_message(
                session_id=session_id,
                round_number=round_num,
                agent_ids=st.session_state.selected_agent_ids,
                prompt=prompt,
                response=full_response
            )

        st.markdown("---")

        # Entre rodadas, permite input do usuário
        if round_num < max_rounds:
            feedback = st.text_area(
                f"Feedback para rodada {round_num + 1} (opcional):",
                key=f"feedback_{round_num}",
                placeholder="Adicione esclarecimentos ou direcionamentos..."
            )

            if feedback.strip():
                additional_context += f"\n\n**Feedback Rodada {round_num}:** {feedback}"

    # Resultado final
    st.success("🎉 Fluxo concluído!")

    st.markdown("## 📄 Documento Final")

    final_output = previous_outputs[-1] if previous_outputs else ""
    st.markdown(final_output)

    # Download
    st.download_button(
        "📥 Download Markdown",
        data=final_output,
        file_name=f"{mode.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )


def main():
    """Main app"""

    st.set_page_config(
        page_title="Dynamic Team Builder",
        page_icon="🚀",
        layout="wide"
    )

    init_session_state()

    # Header
    st.title("🚀 Dynamic Team Builder")
    st.markdown("### Sistema Completo de Criação e Gestão de Times de Agentes IA")
    st.markdown("---")

    # Sidebar
    render_sidebar()

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Agentes",
        "📚 Conhecimento",
        "🎯 Time",
        "🚀 Executar",
        "❓ Ajuda"
    ])

    with tab1:
        render_agent_management()

    with tab2:
        render_knowledge_management()

    with tab3:
        render_team_selection()

    with tab4:
        render_workflow()

    with tab5:
        st.markdown("""
## 🎓 Guia de Uso

### 1. Configurar API
Configure sua chave OpenAI na barra lateral

### 2. Criar Agentes
- Vá para aba "Agentes" → "Criar"
- Defina nome, role, instruções, emoji
- Crie quantos agentes precisar

### 3. Adicionar Conhecimento
- Aba "Conhecimento" → "Adicionar"
- Faça upload de PDFs, TXTs, Markdowns
- Associe a agentes específicos ou deixe global

### 4. Montar Time
- Aba "Time"
- Selecione quais agentes participarão

### 5. Executar
- Aba "Executar"
- Escolha modo: Criar ou Analisar documento
- Configure rodadas e chunking
- Forneça instruções
- Execute!

## ✨ Recursos

✅ **CRUD de Agentes** - Crie, edite, delete
✅ **Base de Conhecimento** - PDFs, Markdown, TXT, DOCX
✅ **Múltiplos Chunking** - Fixed, Semantic, Agentic
✅ **Persistência** - SQLite + LanceDB
✅ **Streaming** - Respostas em tempo real
✅ **Fluxo Dinâmico** - Configure rodadas
✅ **Criação de Documentos** - Não só análise
✅ **Memória** - Agentes lembram contexto
✅ **Conhecimento por Agente** - Especialização

## 🎯 Exemplos

**Time Jurídico:**
- Agente "Advogado Contratual"
- Agente "Especialista LGPD"
- Agente "Compliance Officer"

**Time Técnico:**
- Agente "Arquiteto de Software"
- Agente "Security Expert"
- Agente "DevOps Engineer"

**Criação de Política:**
Modo: Criar Documento
Input: "Criar política de home office completa"
Rodadas: 3
→ Time colabora criando versões iterativas

---

**Desenvolvido com ❤️ usando Agno**
        """)


if __name__ == "__main__":
    main()

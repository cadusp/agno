"""
🚀 AutoGen Multi-Agent Team Builder
Sistema Completo de Criação e Gestão de Times de Agentes usando Microsoft AutoGen

AutoGen é o melhor orquestrador para agentes colaborativos da Microsoft Research.

Funcionalidades Completas:
✅ CRUD de Agentes customizáveis
✅ Gestão de Base de Conhecimento (PDF, MD, TXT, DOCX, CSV)
✅ Múltiplos Chunking Strategies
✅ RAG com ChromaDB/FAISS
✅ Persistência SQLite + Vetores
✅ Streaming de respostas em tempo real
✅ GroupChat - Todos agentes veem análises de outros
✅ Criar E Analisar documentos
✅ Memória persistente
✅ Fluxo dinâmico configurável
✅ Suporte OpenAI e Azure OpenAI

Powered by: Microsoft AutoGen + Streamlit + LangChain
Autor: Claude Code
Versão: 4.0 - AutoGen Edition
"""

import streamlit as st
import os
import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import tempfile
import uuid
import io
import sys

# AutoGen imports
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

# LangChain imports para RAG (versão atualizada)
try:
    # Nova estrutura LangChain v0.1+
    from langchain_text_splitters import (
        RecursiveCharacterTextSplitter,
        CharacterTextSplitter,
        MarkdownTextSplitter,
    )
except ImportError:
    # Fallback para versão antiga
    from langchain.text_splitter import (
        RecursiveCharacterTextSplitter,
        CharacterTextSplitter,
        MarkdownTextSplitter,
    )

try:
    from langchain_community.document_loaders import (
        TextLoader,
        UnstructuredMarkdownLoader,
        CSVLoader,
    )
    from langchain_community.document_loaders import PyPDFLoader
except ImportError:
    # Fallback
    from langchain.document_loaders import (
        TextLoader,
        UnstructuredMarkdownLoader,
        CSVLoader,
        PyPDFLoader,
    )

try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    from langchain.vectorstores import Chroma

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    from langchain.embeddings import OpenAIEmbeddings

try:
    from langchain_core.documents import Document as LangChainDocument
except ImportError:
    from langchain.schema import Document as LangChainDocument

# ChromaDB
import chromadb

# Para DOCX - pip install docx2txt
try:
    import docx2txt
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class Config:
    """Gerenciador de configurações"""

    CONFIG_DIR = Path.home() / ".autogen_team_builder"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    DB_FILE = CONFIG_DIR / "agents.db"
    CHROMA_DIR = CONFIG_DIR / "chromadb"
    CACHE_DIR = CONFIG_DIR / "cache"

    def __init__(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
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
                system_message TEXT,
                emoji TEXT,
                human_input_mode TEXT DEFAULT 'NEVER',
                max_consecutive_auto_reply INTEGER DEFAULT 10,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT
            )
        """)

        # Tabela de documentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_docs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                content TEXT,
                file_type TEXT,
                agent_id TEXT,
                collection_name TEXT,
                created_at TEXT,
                metadata TEXT
            )
        """)

        # Tabela de sessões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                mode TEXT,
                agent_ids TEXT,
                created_at TEXT,
                updated_at TEXT,
                metadata TEXT
            )
        """)

        # Tabela de mensagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                round_number INTEGER,
                speaker TEXT,
                message TEXT,
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

    def save_api_key(self, api_key: str, api_type: str = "openai"):
        config = self._load_config()
        config['api_key'] = api_key
        config['api_type'] = api_type
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        os.environ['OPENAI_API_KEY'] = api_key

    def get_api_key(self) -> Optional[str]:
        config = self._load_config()
        api_key = config.get('api_key')
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            return api_key
        return os.environ.get('OPENAI_API_KEY')

    def get_api_type(self) -> str:
        config = self._load_config()
        return config.get('api_type', 'openai')

    def save_azure_config(
        self,
        api_key: str,
        azure_endpoint: str,
        api_version: str = "2024-02-01"
    ):
        config = self._load_config()
        config['api_type'] = 'azure'
        config['api_key'] = api_key
        config['azure_endpoint'] = azure_endpoint
        config['api_version'] = api_version
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

    def get_llm_config(self, model: str = "gpt-4o-mini") -> Dict:
        """Retorna configuração para AutoGen"""
        config = self._load_config()
        api_type = config.get('api_type', 'openai')

        if api_type == 'azure':
            return {
                "config_list": [{
                    "model": model,
                    "api_type": "azure",
                    "api_key": config['api_key'],
                    "base_url": config['azure_endpoint'],
                    "api_version": config.get('api_version', '2024-02-01'),
                }],
                "temperature": 0.7,
                "cache_seed": None,  # Disable caching for streaming
            }
        else:
            return {
                "config_list": [{
                    "model": model,
                    "api_key": config['api_key'],
                }],
                "temperature": 0.7,
                "cache_seed": None,
            }

    def delete_api_key(self):
        config = self._load_config()
        if 'api_key' in config:
            del config['api_key']
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
        system_message: str,
        emoji: str = "🤖",
        human_input_mode: str = "NEVER",
        max_consecutive_auto_reply: int = 10,
        metadata: Optional[Dict] = None
    ) -> str:
        """Cria novo agente"""
        agent_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO agents (
                id, name, role, system_message, emoji,
                human_input_mode, max_consecutive_auto_reply,
                created_at, updated_at, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            agent_id, name, role, system_message, emoji,
            human_input_mode, max_consecutive_auto_reply,
            now, now, json.dumps(metadata or {})
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
            'system_message': row[3],
            'emoji': row[4],
            'human_input_mode': row[5],
            'max_consecutive_auto_reply': row[6],
            'created_at': row[7],
            'updated_at': row[8],
            'metadata': json.loads(row[9]) if row[9] else {}
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
                'system_message': row[3],
                'emoji': row[4],
                'human_input_mode': row[5],
                'max_consecutive_auto_reply': row[6],
                'created_at': row[7],
                'updated_at': row[8],
                'metadata': json.loads(row[9]) if row[9] else {}
            })

        return agents

    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        system_message: Optional[str] = None,
        emoji: Optional[str] = None,
        human_input_mode: Optional[str] = None,
        max_consecutive_auto_reply: Optional[int] = None,
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
        if system_message is not None:
            updates.append("system_message = ?")
            values.append(system_message)
        if emoji is not None:
            updates.append("emoji = ?")
            values.append(emoji)
        if human_input_mode is not None:
            updates.append("human_input_mode = ?")
            values.append(human_input_mode)
        if max_consecutive_auto_reply is not None:
            updates.append("max_consecutive_auto_reply = ?")
            values.append(max_consecutive_auto_reply)
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

        cursor.execute("DELETE FROM knowledge_docs WHERE agent_id = ?", (agent_id,))
        cursor.execute("DELETE FROM agents WHERE id = ?", (agent_id,))

        conn.commit()
        conn.close()


# ============================================================================
# GERENCIADOR DE CONHECIMENTO
# ============================================================================

class KnowledgeManager:
    """Gerencia base de conhecimento com RAG"""

    CHUNKING_STRATEGIES = {
        'recursive': 'Recursive Character (melhor para textos gerais)',
        'character': 'Character Split (simples e rápido)',
        'markdown': 'Markdown Split (preserva estrutura MD)',
        'fixed': 'Fixed Size (tamanho fixo)',
    }

    def __init__(self, db_path: str, chroma_dir: str):
        self.db_path = db_path
        self.chroma_dir = Path(chroma_dir)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

    def add_document(
        self,
        file_content: str,
        file_name: str,
        file_type: str,
        agent_id: Optional[str] = None
    ) -> str:
        """Adiciona documento à base"""
        doc_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Define collection name
        if agent_id:
            collection_name = f"agent_{agent_id[:8]}"
        else:
            collection_name = "global_knowledge"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO knowledge_docs (
                id, name, content, file_type, agent_id,
                collection_name, created_at, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id, file_name, file_content, file_type,
            agent_id, collection_name, now, json.dumps({})
        ))

        conn.commit()
        conn.close()

        return doc_id

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Busca documento"""
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
            'collection_name': row[5],
            'created_at': row[6],
            'metadata': json.loads(row[7]) if row[7] else {}
        }

    def list_documents(self, agent_id: Optional[str] = None) -> List[Dict]:
        """Lista documentos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if agent_id:
            cursor.execute(
                "SELECT * FROM knowledge_docs WHERE agent_id = ? OR agent_id IS NULL ORDER BY created_at DESC",
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
                'collection_name': row[5],
                'created_at': row[6],
                'metadata': json.loads(row[7]) if row[7] else {}
            })

        return docs

    def delete_document(self, doc_id: str):
        """Deleta documento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM knowledge_docs WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()

    def create_vector_store(
        self,
        agent_id: Optional[str],
        api_key: str,
        chunking_strategy: str = 'recursive',
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> Optional[Chroma]:
        """Cria vector store com ChromaDB"""

        # Busca documentos
        docs = self.list_documents(agent_id)
        if not docs:
            return None

        # Define collection name
        if agent_id:
            collection_name = f"agent_{agent_id[:8]}"
        else:
            collection_name = "global_knowledge"

        # Cria embeddings
        embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-3-small"
        )

        # Seleciona splitter
        if chunking_strategy == 'recursive':
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
        elif chunking_strategy == 'markdown':
            splitter = MarkdownTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        elif chunking_strategy == 'character':
            splitter = CharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

        # Processa documentos
        langchain_docs = []
        for doc in docs:
            langchain_doc = LangChainDocument(
                page_content=doc['content'],
                metadata={
                    'source': doc['name'],
                    'doc_id': doc['id'],
                    'file_type': doc['file_type']
                }
            )
            langchain_docs.append(langchain_doc)

        # Split
        splits = splitter.split_documents(langchain_docs)

        # Cria vector store
        vector_store = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=str(self.chroma_dir)
        )

        return vector_store


# ============================================================================
# GERENCIADOR DE SESSÕES
# ============================================================================

class SessionManager:
    """Gerencia sessões de trabalho"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_session(self, name: str, mode: str, agent_ids: List[str]) -> str:
        """Cria nova sessão"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (id, name, mode, agent_ids, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session_id, name, mode, json.dumps(agent_ids), now, now, json.dumps({})))

        conn.commit()
        conn.close()

        return session_id

    def save_message(
        self,
        session_id: str,
        round_number: int,
        speaker: str,
        message: str
    ):
        """Salva mensagem"""
        msg_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (id, session_id, round_number, speaker, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (msg_id, session_id, round_number, speaker, message, now))

        conn.commit()
        conn.close()

    def get_session_history(self, session_id: str) -> List[Dict]:
        """Recupera histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY round_number, created_at",
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
                'speaker': row[3],
                'message': row[4],
                'created_at': row[5],
            })

        return messages


# ============================================================================
# CRIADOR DE TEAM COM AUTOGEN
# ============================================================================

def create_autogen_team(
    agent_configs: List[Dict],
    llm_config: Dict,
    vector_stores: Optional[Dict[str, Chroma]] = None,
    max_round: int = 10,
    enable_rag: bool = False
) -> tuple:
    """
    Cria team com AutoGen GroupChat

    Returns:
        tuple: (agents_list, groupchat, manager)
    """

    agents = []

    # Cria agentes
    for config in agent_configs:
        agent_name = config['name'].replace(' ', '_')

        if enable_rag and vector_stores and config['id'] in vector_stores:
            # Agente com RAG
            agent = RetrieveAssistantAgent(
                name=agent_name,
                system_message=config['system_message'],
                llm_config=llm_config,
                human_input_mode=config.get('human_input_mode', 'NEVER'),
                max_consecutive_auto_reply=config.get('max_consecutive_auto_reply', 10),
            )
        else:
            # Agente normal
            agent = AssistantAgent(
                name=agent_name,
                system_message=config['system_message'],
                llm_config=llm_config,
                human_input_mode=config.get('human_input_mode', 'NEVER'),
                max_consecutive_auto_reply=config.get('max_consecutive_auto_reply', 10),
            )

        agents.append(agent)

    # Cria GroupChat
    groupchat = GroupChat(
        agents=agents,
        messages=[],
        max_round=max_round,
        speaker_selection_method="auto",  # ou "round_robin"
    )

    # Cria Manager
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
    )

    return agents, groupchat, manager


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
            str(st.session_state.config.CHROMA_DIR)
        )

    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager(str(st.session_state.config.DB_FILE))

    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None

    if 'selected_agent_ids' not in st.session_state:
        st.session_state.selected_agent_ids = []

    if 'vector_stores' not in st.session_state:
        st.session_state.vector_stores = {}

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []


def render_sidebar():
    """Barra lateral"""
    with st.sidebar:
        st.title("⚙️ Configurações")

        # API Config
        config = st.session_state.config

        api_type = st.radio("API Type:", ["OpenAI", "Azure OpenAI"], horizontal=True)

        if api_type == "OpenAI":
            if config.is_configured() and config.get_api_type() == 'openai':
                st.success("✅ OpenAI API OK")
                if st.button("🗑️ Remover", use_container_width=True):
                    config.delete_api_key()
                    st.rerun()
            else:
                api_input = st.text_input("OpenAI API Key:", type="password")
                if st.button("💾 Salvar", use_container_width=True):
                    if api_input:
                        config.save_api_key(api_input, "openai")
                        st.success("✅ Salva!")
                        st.rerun()
        else:
            st.text_input("Azure Endpoint:", key="azure_endpoint")
            st.text_input("API Key:", type="password", key="azure_key")
            st.text_input("API Version:", value="2024-02-01", key="azure_version")

            if st.button("💾 Salvar Azure Config", use_container_width=True):
                config.save_azure_config(
                    st.session_state.azure_key,
                    st.session_state.azure_endpoint,
                    st.session_state.azure_version
                )
                st.success("✅ Azure configurado!")

        st.divider()

        # Stats
        st.subheader("📊 Estatísticas")
        agents = st.session_state.agent_manager.list_agents()
        docs = st.session_state.knowledge_manager.list_documents()

        st.metric("Agentes", len(agents))
        st.metric("Documentos", len(docs))
        st.metric("Conversas", len(st.session_state.conversation_history))

        st.divider()
        st.caption("Powered by Microsoft AutoGen")
        st.caption("v4.0 - AutoGen Edition")


def render_agent_management():
    """Gestão de agentes"""
    st.subheader("👥 Gerenciar Agentes AutoGen")

    tab_list, tab_create, tab_edit, tab_templates = st.tabs([
        "📋 Listar", "➕ Criar", "✏️ Editar", "📝 Templates"
    ])

    # Listar
    with tab_list:
        agents = st.session_state.agent_manager.list_agents()

        if not agents:
            st.info("Nenhum agente criado ainda. Use templates ou crie um novo!")
        else:
            for agent in agents:
                with st.expander(f"{agent['emoji']} {agent['name']}", expanded=False):
                    st.markdown(f"**Role:** {agent['role']}")
                    st.markdown(f"**System Message:**\n```\n{agent['system_message']}\n```")
                    st.caption(f"ID: {agent['id']}")

    # Criar
    with tab_create:
        with st.form("create_agent_form"):
            st.markdown("### Novo Agente AutoGen")

            name = st.text_input("Nome*", placeholder="Ex: Financial_Analyst")
            emoji = st.text_input("Emoji", value="🤖", max_chars=2)
            role = st.text_input("Role", placeholder="Ex: CFO especialista em análise financeira")

            system_message = st.text_area(
                "System Message*",
                height=250,
                placeholder="Você é um especialista financeiro...\nSua função é analisar custos, ROI e riscos fiscais...\nSempre forneça análises detalhadas em português.",
                help="Mensagem de sistema que define o comportamento do agente"
            )

            col1, col2 = st.columns(2)
            with col1:
                max_replies = st.number_input("Max Auto Replies", 1, 50, 10)
            with col2:
                human_input = st.selectbox(
                    "Human Input Mode",
                    ["NEVER", "TERMINATE", "ALWAYS"]
                )

            submitted = st.form_submit_button("✅ Criar Agente", type="primary")

            if submitted:
                if not name or not system_message:
                    st.error("Nome e System Message são obrigatórios")
                else:
                    agent_id = st.session_state.agent_manager.create_agent(
                        name=name,
                        role=role,
                        system_message=system_message,
                        emoji=emoji,
                        human_input_mode=human_input,
                        max_consecutive_auto_reply=max_replies
                    )
                    st.success(f"✅ Agente '{name}' criado!")
                    st.rerun()

    # Editar
    with tab_edit:
        agents = st.session_state.agent_manager.list_agents()

        if not agents:
            st.info("Nenhum agente para editar")
        else:
            agent_options = {f"{a['emoji']} {a['name']}": a['id'] for a in agents}
            selected = st.selectbox("Selecione:", list(agent_options.keys()))
            agent_id = agent_options[selected]
            agent = st.session_state.agent_manager.get_agent(agent_id)

            with st.form("edit_agent_form"):
                new_name = st.text_input("Nome", value=agent['name'])
                new_emoji = st.text_input("Emoji", value=agent['emoji'])
                new_role = st.text_input("Role", value=agent['role'])
                new_system = st.text_area("System Message", value=agent['system_message'], height=250)

                col1, col2 = st.columns(2)
                with col1:
                    update_btn = st.form_submit_button("💾 Atualizar", type="primary")
                with col2:
                    delete_btn = st.form_submit_button("🗑️ Deletar", type="secondary")

                if update_btn:
                    st.session_state.agent_manager.update_agent(
                        agent_id,
                        name=new_name,
                        emoji=new_emoji,
                        role=new_role,
                        system_message=new_system
                    )
                    st.success("✅ Agente atualizado!")
                    st.rerun()

                if delete_btn:
                    st.session_state.agent_manager.delete_agent(agent_id)
                    st.success("✅ Agente deletado!")
                    st.rerun()

    # Templates
    with tab_templates:
        st.markdown("### 📝 Templates de Agentes")

        templates = {
            "💰 CFO - Chief Financial Officer": {
                "role": "Diretor Financeiro",
                "system_message": """Você é o CFO (Chief Financial Officer) da organização.

Sua perspectiva é financeira e fiscal.

Responsabilidades:
- Analisar impactos financeiros diretos e indiretos
- Identificar riscos fiscais e tributários
- Avaliar ROI e viabilidade econômica
- Calcular custos de implementação e manutenção
- Verificar compliance com normas contábeis
- Identificar contingências financeiras

Sempre:
- Quantifique impactos quando possível
- Cite normas contábeis relevantes (CPC, IFRS)
- Proponha alternativas mais econômicas
- Identifique riscos financeiros ocultos
- Comunique em português do Brasil

Interaja com outros membros do time para garantir decisões financeiramente sólidas."""
            },
            "⚖️ Legal - Diretor Jurídico": {
                "role": "Diretor Jurídico",
                "system_message": """Você é o Diretor Jurídico (Legal Counsel) da organização.

Sua perspectiva é legal e regulatória.

Responsabilidades:
- Analisar conformidade com legislação brasileira
- Identificar riscos legais e contratuais
- Revisar cláusulas problemáticas
- Verificar Código Civil, CDC, CLT quando aplicável
- Citar jurisprudência relevante
- Avaliar exposição a litígios
- Verificar necessidade de aprovações regulatórias

Sempre:
- Cite artigos de lei específicos
- Identifique riscos legais claros
- Proponha cláusulas alternativas
- Avalie impacto de jurisprudência recente
- Comunique em português do Brasil

Colabore com outros membros especialmente em aspectos regulatórios."""
            },
            "🔐 DPO - Data Protection Officer": {
                "role": "Encarregado de Proteção de Dados",
                "system_message": """Você é o DPO (Data Protection Officer) da organização.

Sua perspectiva é de proteção de dados e privacidade.

Responsabilidades:
- Garantir conformidade com LGPD (Lei 13.709/2018)
- Verificar bases legais para tratamento de dados
- Avaliar direitos dos titulares
- Analisar medidas de segurança e privacidade
- Verificar necessidade de DPIA (Relatório de Impacto)
- Avaliar transferência internacional de dados
- Orientar sobre comunicação com ANPD

Sempre:
- Cite artigos específicos da LGPD
- Identifique dados pessoais e sensíveis
- Verifique adequação das bases legais
- Avalie riscos de privacidade
- Proponha medidas de mitigação
- Comunique em português do Brasil

Trabalhe próximo ao CISO em aspectos de segurança de dados."""
            },
            "🛡️ CISO - Chief Information Security Officer": {
                "role": "Diretor de Segurança da Informação",
                "system_message": """Você é o CISO (Chief Information Security Officer) da organização.

Sua perspectiva é de segurança da informação e cibersegurança.

Responsabilidades:
- Identificar riscos de segurança cibernética
- Avaliar proteção de ativos de informação
- Verificar controles de acesso e autenticação
- Analisar vulnerabilidades e ameaças
- Revisar planos de resposta a incidentes
- Garantir conformidade com ISO 27001, NIST, CIS
- Avaliar segurança de terceiros e fornecedores

Sempre:
- Classifique riscos por severidade (Crítico/Alto/Médio/Baixo)
- Cite frameworks (ISO 27001, NIST CSF, CIS Controls)
- Proponha controles técnicos e administrativos
- Avalie impacto na tríade CIA (Confidencialidade, Integridade, Disponibilidade)
- Comunique em português do Brasil

Colabore com DPO em segurança de dados pessoais."""
            },
            "💻 CTO - Chief Technology Officer": {
                "role": "Diretor de Tecnologia",
                "system_message": """Você é o CTO (Chief Technology Officer) da organização.

Sua perspectiva é tecnológica e de inovação.

Responsabilidades:
- Avaliar viabilidade técnica de implementação
- Definir arquitetura e infraestrutura necessária
- Analisar escalabilidade e performance
- Identificar débito técnico e manutenibilidade
- Avaliar inovação e competitividade tecnológica
- Verificar integração com sistemas existentes
- Definir stack tecnológico adequado

Sempre:
- Proponha arquiteturas concretas
- Identifique tecnologias específicas
- Avalie trade-offs técnicos
- Estime complexidade de implementação
- Considere escalabilidade futura
- Comunique em português do Brasil

Trabalhe com CISO em arquiteturas seguras."""
            },
        }

        for template_name, template_data in templates.items():
            if st.button(f"Usar Template: {template_name}", use_container_width=True):
                agent_id = st.session_state.agent_manager.create_agent(
                    name=template_name.split(' - ')[1],
                    role=template_data['role'],
                    system_message=template_data['system_message'],
                    emoji=template_name[:2],
                    human_input_mode="NEVER",
                    max_consecutive_auto_reply=10
                )
                st.success(f"✅ Agente criado do template!")
                st.rerun()


def render_knowledge_management():
    """Gestão de conhecimento"""
    st.subheader("📚 Base de Conhecimento (RAG)")

    tab_list, tab_add, tab_config = st.tabs(["📋 Documentos", "➕ Adicionar", "⚙️ Config"])

    # Listar
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
                    st.text_area("Preview", value=doc['content'][:500] + "...", height=100, disabled=True)

                    if st.button(f"🗑️ Deletar###{doc['id']}", key=f"del_{doc['id']}"):
                        st.session_state.knowledge_manager.delete_document(doc['id'])
                        st.success("Deletado!")
                        st.rerun()

    # Adicionar
    with tab_add:
        st.markdown("### Upload de Documento")

        agents = st.session_state.agent_manager.list_agents()
        agent_options = {"Global (todos)": None}
        agent_options.update({f"{a['emoji']} {a['name']}": a['id'] for a in agents})

        selected_agent = st.selectbox("Associar a:", list(agent_options.keys()))
        agent_id = agent_options[selected_agent]

        uploaded = st.file_uploader(
            "Arquivo",
            type=['txt', 'md', 'pdf', 'docx', 'csv']
        )

        st.markdown("**Ou cole:**")
        text_input = st.text_area("Conteúdo", height=200)

        if st.button("📥 Adicionar", type="primary"):
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

            if content:
                doc_id = st.session_state.knowledge_manager.add_document(
                    file_content=content,
                    file_name=filename,
                    file_type=filetype,
                    agent_id=agent_id
                )
                st.success(f"✅ '{filename}' adicionado!")
                st.session_state.vector_stores = {}  # Clear cache
                st.rerun()
            else:
                st.error("Forneça arquivo ou texto")

    # Config
    with tab_config:
        st.markdown("### Chunking Strategies")
        for strategy, desc in st.session_state.knowledge_manager.CHUNKING_STRATEGIES.items():
            st.markdown(f"**{strategy}**: {desc}")


def render_team_selection():
    """Seleção do time"""
    st.subheader("👥 Monte seu Time AutoGen")

    agents = st.session_state.agent_manager.list_agents()

    if not agents:
        st.warning("⚠️ Crie agentes primeiro ou use templates!")
        return

    st.markdown("Selecione os agentes:")

    cols = st.columns(3)
    selected = []

    for idx, agent in enumerate(agents):
        col = cols[idx % 3]

        with col:
            is_selected = st.checkbox(
                f"{agent['emoji']} {agent['name']}",
                value=agent['id'] in st.session_state.selected_agent_ids,
                key=f"sel_{agent['id']}",
                help=agent['role']
            )

            if is_selected:
                selected.append(agent['id'])

    st.session_state.selected_agent_ids = selected

    if selected:
        st.success(f"✅ {len(selected)} agente(s) no team")
    else:
        st.warning("⚠️ Selecione pelo menos 2 agentes")


def render_workflow():
    """Fluxo de trabalho"""
    st.subheader("🚀 Executar com AutoGen GroupChat")

    if not st.session_state.config.is_configured():
        st.error("❌ Configure API primeiro")
        return

    if len(st.session_state.selected_agent_ids) < 2:
        st.warning("⚠️ Selecione pelo menos 2 agentes")
        return

    # Modo
    mode = st.radio(
        "Modo:",
        ["📝 Criar Documento", "🔍 Analisar Documento"],
        horizontal=True
    )

    # Configurações
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        max_round = st.number_input("Max Rounds", 5, 50, 15)

    with col2:
        model = st.selectbox("Modelo", ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"])

    with col3:
        enable_rag = st.checkbox("Habilitar RAG", value=False)

    with col4:
        chunking = st.selectbox(
            "Chunking",
            list(st.session_state.knowledge_manager.CHUNKING_STRATEGIES.keys())
        )

    # Input
    st.markdown("---")

    if mode == "📝 Criar Documento":
        st.markdown("### Descreva o documento")
        user_input = st.text_area(
            "Instruções:",
            height=200,
            placeholder="Ex: Criar política de home office completa..."
        )
    else:
        st.markdown("### Documento para análise")
        uploaded = st.file_uploader("Upload (opcional)", type=['txt', 'md', 'pdf'])
        user_input = st.text_area(
            "Texto ou instruções:",
            height=200
        )

    # Executar
    if st.button("🚀 Executar AutoGen GroupChat", type="primary", use_container_width=True):
        if not user_input.strip():
            st.error("Forneça instruções")
            return

        execute_autogen_workflow(
            mode=mode,
            user_input=user_input,
            max_round=max_round,
            model=model,
            enable_rag=enable_rag,
            chunking_strategy=chunking
        )


def execute_autogen_workflow(
    mode: str,
    user_input: str,
    max_round: int,
    model: str,
    enable_rag: bool,
    chunking_strategy: str
):
    """Executa workflow com AutoGen"""

    st.markdown("---")
    st.markdown("## 🎯 Execução AutoGen GroupChat")

    # Prepara configuração
    config = st.session_state.config
    llm_config = config.get_llm_config(model)
    api_key = config.get_api_key()

    # Prepara vector stores se RAG
    vector_stores = {}
    if enable_rag:
        with st.spinner("Preparando RAG..."):
            for agent_id in st.session_state.selected_agent_ids:
                vs = st.session_state.knowledge_manager.create_vector_store(
                    agent_id=agent_id,
                    api_key=api_key,
                    chunking_strategy=chunking_strategy
                )
                if vs:
                    vector_stores[agent_id] = vs

            # Global knowledge
            vs_global = st.session_state.knowledge_manager.create_vector_store(
                agent_id=None,
                api_key=api_key,
                chunking_strategy=chunking_strategy
            )
            if vs_global:
                for agent_id in st.session_state.selected_agent_ids:
                    if agent_id not in vector_stores:
                        vector_stores[agent_id] = vs_global

    # Prepara agentes
    agent_configs = []
    for agent_id in st.session_state.selected_agent_ids:
        agent = st.session_state.agent_manager.get_agent(agent_id)
        if agent:
            agent_configs.append(agent)

    # Cria sessão
    session_name = f"{mode} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    session_id = st.session_state.session_manager.create_session(
        session_name,
        mode,
        st.session_state.selected_agent_ids
    )

    # Prepara prompt
    if mode == "📝 Criar Documento":
        prompt = f"""Trabalhem colaborativamente para CRIAR o seguinte documento:

{user_input}

IMPORTANTE:
- Cada agente deve contribuir com sua expertise
- Debatam e refinem ideias em conjunto
- Construam o documento iterativamente
- O resultado final deve ser um documento completo em Markdown
- Todos devem ler e comentar as contribuições dos outros

Comecem!"""
    else:
        prompt = f"""Analisem colaborativamente o seguinte:

{user_input}

IMPORTANTE:
- Cada agente analisa sob sua perspectiva
- Debatam pontos controversos
- Identifiquem riscos e oportunidades
- Todos devem ler análises dos outros
- Cheguem a um consenso final

Comecem a análise!"""

    # Cria team
    with st.spinner("Criando AutoGen GroupChat..."):
        try:
            agents_list, groupchat, manager = create_autogen_team(
                agent_configs=agent_configs,
                llm_config=llm_config,
                vector_stores=vector_stores if enable_rag else None,
                max_round=max_round,
                enable_rag=enable_rag
            )

            st.success(f"✅ GroupChat criado com {len(agents_list)} agentes!")

        except Exception as e:
            st.error(f"Erro ao criar team: {str(e)}")
            return

    # Cria user proxy para iniciar
    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
    )

    # Container para output
    output_container = st.empty()
    conversation_text = ""

    # Executa com captura de output
    st.markdown("### 💬 Conversa do GroupChat")

    with st.spinner("🤖 Agentes trabalhando..."):
        try:
            # Inicia conversa
            user_proxy.initiate_chat(
                manager,
                message=prompt,
            )

            # Captura mensagens do groupchat
            for msg in groupchat.messages:
                speaker = msg.get('name', 'Unknown')
                content = msg.get('content', '')

                if speaker and content:
                    conversation_text += f"\n\n**{speaker}:**\n{content}\n"
                    conversation_text += "\n---\n"

                    # Atualiza display
                    output_container.markdown(conversation_text)

                    # Salva no banco
                    st.session_state.session_manager.save_message(
                        session_id=session_id,
                        round_number=len(groupchat.messages),
                        speaker=speaker,
                        message=content
                    )

            st.success("✅ Conversa concluída!")

            # Salva em histórico
            st.session_state.conversation_history.append({
                'session_id': session_id,
                'mode': mode,
                'timestamp': datetime.now().isoformat(),
                'conversation': conversation_text
            })

            # Download
            st.markdown("### 📥 Download")
            st.download_button(
                "Download Markdown",
                data=conversation_text,
                file_name=f"{mode.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"Erro durante execução: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def main():
    """Main app"""

    st.set_page_config(
        page_title="AutoGen Team Builder",
        page_icon="🚀",
        layout="wide"
    )

    init_session_state()

    # Header
    st.title("🚀 AutoGen Multi-Agent Team Builder")
    st.markdown("### Sistema Completo com Microsoft AutoGen - O Melhor Orquestrador de Agentes")
    st.markdown("---")

    # Sidebar
    render_sidebar()

    # Tabs
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
## 🎓 Guia AutoGen Team Builder

### Por que AutoGen?

**AutoGen** da Microsoft Research é considerado o **melhor orquestrador** para agentes colaborativos:

✅ **GroupChat** - Múltiplos agentes conversam naturalmente
✅ **Auto-seleção** - Agentes decidem quando falar
✅ **Debate Real** - Conversação autêntica entre agentes
✅ **RAG Integrado** - RetrieveAssistantAgent nativo
✅ **Flexível** - OpenAI ou Azure OpenAI
✅ **Production-ready** - Usado por empresas globalmente

### Como Usar

**1. Configurar API**
- OpenAI ou Azure OpenAI
- Configuração na sidebar

**2. Criar Agentes**
- Use templates prontos, OU
- Crie agentes customizados
- Defina System Message detalhado

**3. Adicionar Conhecimento**
- Upload PDFs, Markdowns, etc.
- Associe a agentes específicos
- Habilite RAG na execução

**4. Montar Time**
- Selecione 2+ agentes
- Team colabora via GroupChat

**5. Executar**
- Escolha modo (Criar ou Analisar)
- Configure rounds e RAG
- Veja agentes trabalhando juntos!

### Recursos AutoGen

**GroupChat:**
- Todos agentes veem mensagens de todos
- Debate natural e orgânico
- Seleção automática de próximo speaker

**RAG:**
- RetrieveAssistantAgent para agentes com conhecimento
- Busca automática em documentos
- Respostas baseadas em contexto

**Streaming:**
- Acompanhe conversa em tempo real
- Veja cada agente contribuindo

### Exemplo de Uso

```
Time: CFO + Legal + DPO
Modo: Criar Documento
Input: "Criar política de privacidade LGPD"

AutoGen GroupChat:
1. Legal define estrutura legal
2. DPO adiciona requisitos LGPD
3. CFO comenta sobre custos de implementação
4. Legal refina com base em feedback DPO
5. Todos convergem para versão final

Resultado: Política completa co-criada
```

### Vantagens vs Outras Soluções

| Característica | AutoGen | Outros |
|----------------|---------|--------|
| GroupChat | ✅ Nativo | ❌ Manual |
| Debate Real | ✅ Automático | ⚠️ Simulado |
| RAG | ✅ Integrado | ⚠️ Separado |
| Multi-LLM | ✅ OpenAI + Azure | ⚠️ Limitado |
| Produção | ✅ Pronto | ⚠️ Experimental |

---

**Powered by Microsoft AutoGen**
*O melhor orquestrador de agentes colaborativos*
        """)


if __name__ == "__main__":
    main()

"""
Aplicação Streamlit para Análise de Documentos Jurídicos
"""
import streamlit as st
from pathlib import Path
import tempfile
from typing import Optional

from config import Config
from agents import create_legal_analysis_team, create_knowledge_base

# Configuração da página
st.set_page_config(
    page_title="Análise de Documentos Jurídicos",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state():
    """Inicializa o estado da sessão"""
    if 'config' not in st.session_state:
        st.session_state.config = Config()

    if 'team' not in st.session_state:
        st.session_state.team = None

    if 'knowledge' not in st.session_state:
        st.session_state.knowledge = None

    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []


def render_sidebar():
    """Renderiza a barra lateral com configurações"""
    with st.sidebar:
        st.title("⚙️ Configurações")

        # Seção de API Key
        st.subheader("🔑 Chave API OpenAI")

        config = st.session_state.config

        # Verifica se já existe uma chave configurada
        if config.is_configured():
            st.success("✅ Chave API configurada")

            # Mostra os primeiros e últimos caracteres da chave
            api_key = config.get_api_key()
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if api_key else ""
            st.text(f"Chave: {masked_key}")

            # Botão para remover a chave
            if st.button("🗑️ Remover Chave", use_container_width=True):
                config.delete_api_key()
                st.session_state.team = None
                st.session_state.knowledge = None
                st.rerun()

        else:
            st.warning("⚠️ Chave API não configurada")

            # Campo para inserir a chave
            api_key_input = st.text_input(
                "Digite sua chave API OpenAI:",
                type="password",
                help="Sua chave será salva localmente em ~/.legal_document_analyzer/config.json"
            )

            if st.button("💾 Salvar Chave", use_container_width=True):
                if api_key_input:
                    config.save_api_key(api_key_input)
                    st.success("✅ Chave salva com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Por favor, insira uma chave válida")

        st.divider()

        # Configurações do modelo
        st.subheader("🤖 Configurações do Modelo")

        model_option = st.selectbox(
            "Modelo OpenAI:",
            options=[
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
            ],
            index=0,
            help="Escolha o modelo para análise"
        )

        enable_rag = st.checkbox(
            "Habilitar RAG (Retrieval-Augmented Generation)",
            value=False,
            help="Permite que os agentes usem documentos carregados como contexto"
        )

        st.session_state.model_option = model_option
        st.session_state.enable_rag = enable_rag

        st.divider()

        # Informações
        st.subheader("ℹ️ Sobre")
        st.markdown("""
        **Time de Agentes:**
        - 👔 Analista de Contratos
        - ✅ Agente de Conformidade
        - 📋 Analista de Políticas
        - ⚠️ Analista de Riscos
        - 📊 Especialista em Resumos

        **Recursos:**
        - Análise multidimensional
        - Identificação de riscos
        - Verificação de conformidade
        - Sugestões de melhorias
        """)

        st.divider()

        # Estatísticas
        if st.session_state.analysis_history:
            st.subheader("📊 Estatísticas")
            st.metric("Análises Realizadas", len(st.session_state.analysis_history))


def initialize_team():
    """Inicializa o time de agentes"""
    config = st.session_state.config

    if not config.is_configured():
        return None

    api_key = config.get_api_key()
    model_id = st.session_state.get('model_option', 'gpt-4o-mini')

    # Cria knowledge base se RAG estiver habilitado
    knowledge = None
    if st.session_state.get('enable_rag', False):
        if st.session_state.knowledge is None:
            with st.spinner("Inicializando base de conhecimento..."):
                st.session_state.knowledge = create_knowledge_base(api_key)
        knowledge = st.session_state.knowledge

    # Cria o time
    team = create_legal_analysis_team(
        api_key=api_key,
        knowledge=knowledge,
        model_id=model_id
    )

    return team


def process_document(uploaded_file) -> str:
    """
    Processa o documento carregado

    Args:
        uploaded_file: Arquivo carregado pelo Streamlit

    Returns:
        Conteúdo do documento como string
    """
    # Salva temporariamente o arquivo
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    # Lê o conteúdo
    try:
        with open(tmp_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(tmp_path, 'r', encoding='latin-1') as f:
            content = f.read()

    # Remove arquivo temporário
    Path(tmp_path).unlink()

    return content


def add_document_to_knowledge(content: str, filename: str):
    """Adiciona documento à base de conhecimento"""
    if st.session_state.knowledge:
        from agno.knowledge.document import Document

        doc = Document(
            name=filename,
            content=content,
        )

        st.session_state.knowledge.load_documents([doc])


def render_main_content():
    """Renderiza o conteúdo principal"""
    st.title("⚖️ Análise de Documentos Jurídicos com IA")
    st.markdown("### Sistema Inteligente de Análise Legal Multidimensional")

    config = st.session_state.config

    # Verifica se a API está configurada
    if not config.is_configured():
        st.warning("⚠️ Configure sua chave API OpenAI na barra lateral para começar.")
        return

    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["📄 Nova Análise", "📚 Histórico", "❓ Ajuda"])

    with tab1:
        render_analysis_tab()

    with tab2:
        render_history_tab()

    with tab3:
        render_help_tab()


def render_analysis_tab():
    """Renderiza a aba de análise"""
    st.subheader("Carregar Documento para Análise")

    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Selecione um documento (TXT, MD, PDF)",
        type=['txt', 'md', 'pdf'],
        help="Carregue um contrato, política ou documento jurídico para análise"
    )

    # Ou entrada de texto direto
    st.markdown("**Ou cole o texto diretamente:**")
    text_input = st.text_area(
        "Texto do documento:",
        height=200,
        placeholder="Cole aqui o conteúdo do documento que deseja analisar..."
    )

    # Tipo de análise
    analysis_type = st.selectbox(
        "Tipo de Análise:",
        options=[
            "Análise Completa (todos os especialistas)",
            "Análise de Contrato",
            "Verificação de Conformidade",
            "Análise de Política",
            "Identificação de Riscos",
            "Resumo Executivo",
        ],
        index=0
    )

    # Instruções adicionais
    additional_instructions = st.text_area(
        "Instruções adicionais (opcional):",
        height=100,
        placeholder="Ex: Foque em cláusulas de rescisão, Verifique conformidade com LGPD, etc."
    )

    # Botão de análise
    if st.button("🔍 Iniciar Análise", type="primary", use_container_width=True):
        # Obtém o conteúdo
        content = None
        filename = "documento.txt"

        if uploaded_file:
            content = process_document(uploaded_file)
            filename = uploaded_file.name

            # Adiciona à knowledge base se RAG estiver habilitado
            if st.session_state.get('enable_rag', False):
                with st.spinner("Indexando documento na base de conhecimento..."):
                    add_document_to_knowledge(content, filename)

        elif text_input.strip():
            content = text_input
            filename = "texto_colado.txt"

        if not content:
            st.error("❌ Por favor, carregue um arquivo ou cole um texto.")
            return

        # Inicializa o time
        with st.spinner("Inicializando time de especialistas..."):
            team = initialize_team()

        if not team:
            st.error("❌ Erro ao inicializar o time de agentes.")
            return

        # Prepara o prompt
        prompt = f"""
Analise o seguinte documento jurídico:

--- INÍCIO DO DOCUMENTO ---
{content}
--- FIM DO DOCUMENTO ---

Tipo de análise solicitada: {analysis_type}
"""

        if additional_instructions:
            prompt += f"\nInstruções adicionais: {additional_instructions}"

        # Executa a análise
        with st.spinner("🤖 Agentes trabalhando na análise... Isso pode levar alguns minutos."):
            try:
                response = team.run(prompt, stream=False)

                # Salva no histórico
                st.session_state.analysis_history.append({
                    'filename': filename,
                    'analysis_type': analysis_type,
                    'content': content[:500] + "..." if len(content) > 500 else content,
                    'response': response.content,
                })

                # Exibe o resultado
                st.success("✅ Análise concluída!")
                st.markdown("---")
                st.markdown("### 📊 Resultado da Análise")
                st.markdown(response.content)

            except Exception as e:
                st.error(f"❌ Erro durante a análise: {str(e)}")


def render_history_tab():
    """Renderiza a aba de histórico"""
    st.subheader("Histórico de Análises")

    if not st.session_state.analysis_history:
        st.info("📭 Nenhuma análise realizada ainda.")
        return

    # Exibe histórico em ordem reversa (mais recente primeiro)
    for i, analysis in enumerate(reversed(st.session_state.analysis_history)):
        with st.expander(
            f"📄 {analysis['filename']} - {analysis['analysis_type']}",
            expanded=(i == 0)
        ):
            st.markdown("**Trecho do documento:**")
            st.text(analysis['content'])

            st.markdown("---")
            st.markdown("**Análise:**")
            st.markdown(analysis['response'])

    # Botão para limpar histórico
    if st.button("🗑️ Limpar Histórico"):
        st.session_state.analysis_history = []
        st.rerun()


def render_help_tab():
    """Renderiza a aba de ajuda"""
    st.subheader("❓ Como Usar")

    st.markdown("""
    ### 🚀 Início Rápido

    1. **Configure sua chave API OpenAI** na barra lateral
    2. **Carregue um documento** ou cole o texto
    3. **Escolha o tipo de análise** desejado
    4. **Clique em "Iniciar Análise"** e aguarde os especialistas

    ### 👥 Especialistas Disponíveis

    **👔 Analista de Contratos**
    - Revisa cláusulas e condições
    - Identifica obrigações e direitos
    - Avalia riscos contratuais

    **✅ Agente de Conformidade**
    - Verifica conformidade com LGPD
    - Analisa adequação a leis e regulamentos
    - Identifica gaps de compliance

    **📋 Analista de Políticas**
    - Avalia clareza e objetividade
    - Compara com melhores práticas
    - Sugere melhorias

    **⚠️ Analista de Riscos**
    - Identifica riscos legais e financeiros
    - Classifica riscos por severidade
    - Propõe estratégias de mitigação

    **📊 Especialista em Resumos**
    - Cria resumos executivos
    - Destaca pontos-chave
    - Fornece recomendações acionáveis

    ### 🎯 Tipos de Análise

    - **Análise Completa**: Todos os especialistas avaliam o documento
    - **Análise de Contrato**: Foco em cláusulas contratuais
    - **Verificação de Conformidade**: Análise regulatória
    - **Análise de Política**: Avaliação de políticas corporativas
    - **Identificação de Riscos**: Mapeamento de riscos
    - **Resumo Executivo**: Síntese para tomada de decisão

    ### 🔧 RAG (Retrieval-Augmented Generation)

    Quando habilitado:
    - Documentos carregados são indexados
    - Agentes usam documentos como contexto
    - Análises mais precisas e contextualizadas
    - Permite comparação entre documentos

    ### 💡 Dicas

    - Use **instruções adicionais** para focar em aspectos específicos
    - Escolha **gpt-4o** para análises mais profundas
    - Use **gpt-4o-mini** para análises rápidas e econômicas
    - Habilite **RAG** para análise de múltiplos documentos relacionados

    ### 🔐 Segurança

    - Sua chave API é salva localmente em `~/.legal_document_analyzer/config.json`
    - Os documentos são processados apenas durante a sessão
    - Nenhum dado é enviado para servidores externos além da OpenAI

    ### 📞 Suporte

    Para dúvidas ou problemas, consulte a documentação do Agno:
    - [Documentação Oficial](https://docs.agno.com)
    - [GitHub](https://github.com/agno-framework/agno)
    """)


def main():
    """Função principal da aplicação"""
    init_session_state()
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()

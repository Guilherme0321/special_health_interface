import json
import os
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

import streamlit as st
import requests
import uuid

# Configurações iniciais
st.set_page_config(page_title="Chat com API", layout="wide")

# Criação das abas
tab1, tab2 = st.tabs(["💬 Chatbot", "📖 Como Usar"])

with tab2:
    st.title("📖 Como Usar o Chatbot")
    
    st.header("🔧 Configuração Inicial")
    st.markdown("""    
    **1. Chave do GPT**: Sua chave de API do OpenAI
    - Formato: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx`
    - ⚠️ **Importante**: Mantenha sua chave segura e não a compartilhe
    
    **2. ID de Teste**: ID personalizado para rastrear conversas
    - Se deixado em branco, será gerado automaticamente
    """)
    
    st.header("💡 Exemplos de Perguntas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧠 Saúde Mental")
        st.code("""
            • O que é ansiedade e como controlá-la?
            • Técnicas de respiração para reduzir o estresse
            • Como melhorar o sono com hábitos saudáveis?
            • Diferença entre depressão e tristeza
            • O que é terapia cognitivo-comportamental?
        """)

        st.subheader("📘 Informações e Educação")
        st.code("""
            • Como a atividade física impacta a saúde mental?
            • Quais são os sinais de burnout?
            • Benefícios da meditação para o cérebro
            • Como lidar com pensamentos negativos?
            • Quando procurar ajuda psicológica?
        """)

    with col2:
        st.subheader("💪 Saúde Física")
        st.code("""
            • Como montar um treino para iniciantes?
            • Quais alimentos ajudam na imunidade?
            • Importância do alongamento antes do exercício
            • Dicas para manter uma boa postura no trabalho
            • Como prevenir dores nas costas?
        """)

        st.subheader("🧬 Bem-estar e Estilo de Vida")
        st.code("""
            • Estratégias para melhorar a qualidade do sono
            • Qual a melhor rotina matinal para mais energia?
            • Benefícios de beber água regularmente
            • Dicas para alimentação saudável durante o dia
            • Como manter hábitos saudáveis mesmo com rotina agitada?
        """)


with tab1:
    st.title("🤖 Chatbot via API")
    
    # Inicializa estados de sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    
    # Sidebar
    st.sidebar.header("🔧 Configurações")
    #api_url = st.sidebar.text_input("🔗 URL da API")
    api_url = 'https://web-production-6daa.up.railway.app/'
    openai_key = st.sidebar.text_input("🔑 Chave do GPT", type="password")
    thread_id = st.sidebar.text_input("ID de Teste")
    
    # Botão para testar conexão
    if st.sidebar.button("🔌 Testar Conexão"):
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                st.sidebar.success("✅ Conexão bem-sucedida!")
            else:
                st.sidebar.warning(f"⚠️ Resposta da API: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"❌ Erro na conexão: {e}")
    
    # Botão para salvar histórico        
    if st.sidebar.button("💾 Salvar Histórico (.csv)"):
        try:
            download_url = f"{api_url}/history/{thread_id}"
            response = requests.get(download_url)
            
            if response.status_code == 200:
                st.sidebar.success("✅ Histórico baixado com sucesso!")
                # Permite download no app Streamlit
                st.sidebar.download_button(
                    label="📥 Clique aqui para baixar o CSV",
                    data=response.content,
                    file_name=f"historico_{thread_id}.csv",
                    mime="text/csv"
                )
            else:
                st.sidebar.warning(f"⚠️ Erro ao baixar: {json.loads(response.content.decode('utf-8'))['message']}")
        except Exception as e:
            st.sidebar.error(f"❌ Erro no download: {e}")
    
    # Botão para encerrar sessão
    if st.sidebar.button("🛑 Encerrar Sessão"):
        json_data = {
            "openai_key": openai_key,
            "thread_id": st.session_state.thread_id,
            "content": "",
            "end_session": True
        }
        
        try:
            response = requests.post(f'{api_url}/end_conection/{thread_id}', json=json_data)
            if response.status_code == 200:
                st.sidebar.success("✅ Sessão encerrada!")
                # Limpa o histórico local também
                st.session_state.messages = []
            else:
                st.sidebar.warning(f"⚠️ Erro ao encerrar: {json.loads(response.content.decode('utf-8'))['message']}")
        except Exception as e:
            st.sidebar.error(f"❌ Erro na conexão: {e}")
    
    # Informações da sessão
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Mensagens:** {len(st.session_state.messages)}")
    
    # Campo de entrada
    user_input = st.chat_input("Digite sua mensagem...")
    
    # Envia mensagem para a API
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        json_data = {
            "openai_key": openai_key,
            "thread_id": thread_id,
            "content": user_input,
        }
        
        try:
            response = requests.post(api_url, json=json_data)
            if response.status_code == 200:
                result = response.json()
                bot_reply = result[-1]['content']
            else:
                bot_reply = f"⚠️ Erro: status {response.status_code}"
        except Exception as e:
            bot_reply = f"❌ Erro ao conectar: {e}"
        
        st.session_state.messages.append({"role": "bot", "content": bot_reply})
    
    # Exibição da conversa
    for msg in st.session_state.messages:
        col1, col2 = st.columns([1, 5]) if msg["role"] == "user" else st.columns([5, 1])
        with (col2 if msg["role"] == "user" else col1):
            with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                st.markdown(msg["content"])
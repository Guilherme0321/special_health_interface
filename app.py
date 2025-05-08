import os
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"

import streamlit as st
import requests
import uuid


# Configurações iniciais
st.set_page_config(page_title="Chat com API", layout="wide")
st.title("🤖 Chatbot via API")

# Inicializa estados de sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Sidebar
st.sidebar.header("🔧 Configurações")
api_url = st.sidebar.text_input(
    "🔗 URL da API",
    value=os.getenv("API_URL", "http://localhost:8000")
)
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
        else:
            st.sidebar.warning(f"⚠️ Erro ao encerrar: status {response.status_code}")
    except Exception as e:
        st.sidebar.error(f"❌ Erro na conexão: {e}")


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

import os
import re
import json
import streamlit as st
import openai
from openai import AssistantEventHandler
from tools import TOOL_MAP
from typing_extensions import override
from dotenv import load_dotenv
import streamlit_authenticator as stauth

load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Assistants API UI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for chat UI
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f3f4f6;
        color: black;
    }
    .chat-container {
        background: white;
        border-radius: 8px;
        max-width: 800px;
        margin: 20px auto;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #ddd;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .chat-messages {
        max-height: 400px;
        overflow-y: auto;
        margin-bottom: 20px;
    }
    .chat-input {
        display: flex;
        align-items: center;
    }
    .chat-input input {
        flex: 1;
        border: 1px solid #ddd;
        border-radius: 20px;
        padding: 10px 20px;
        margin-right: 10px;
    }
    .chat-message {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .chat-message.user {
        justify-content: flex-end;
    }
    .chat-message.user .message-content {
        background: #DCF8C6;
        color: black;
    }
    .chat-message.assistant .message-content {
        background: #ECECEC;
        color: black;
    }
    .message-content {
        max-width: 60%;
        padding: 10px 20px;
        border-radius: 20px;
        margin-left: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def str_to_bool(str_input):
    if not isinstance(str_input, str):
        return False
    return str_input.lower() == "true"

# Load environment variables
azure_openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
azure_openai_key = os.environ.get("AZURE_OPENAI_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")
authentication_required = str_to_bool(os.environ.get("AUTHENTICATION_REQUIRED", False))
assistant_id = os.environ.get("ASSISTANT_ID")
assistant_title = os.environ.get("ASSISTANT_TITLE", "Assistants API UI")

# Load authentication configuration
if authentication_required:
    if "credentials" in st.secrets:
        authenticator = stauth.Authenticate(
            st.secrets["credentials"].to_dict(),
            st.secrets["cookie"]["name"],
            st.secrets["cookie"]["key"],
            st.secrets["cookie"]["expiry_days"],
        )
    else:
        authenticator = None  # No authentication should be performed

client = None
if azure_openai_endpoint and azure_openai_key:
    client = openai.AzureOpenAI(
        api_key=azure_openai_key,
        api_version="2024-02-15-preview",
        azure_endpoint=azure_openai_endpoint,
    )
else:
    client = openai.OpenAI(api_key=openai_api_key)

class EventHandler(AssistantEventHandler):
    @override
    def on_event(self, event):
        pass

    @override
    def on_text_created(self, text):
        st.session_state.current_message = ""
        with st.chat_message("Assistant"):
            st.session_state.current_markdown = st.empty()

    @override
    def on_text_delta(self, delta, snapshot):
        if snapshot.value:
            text_value = re.sub(
                r"\[(.*?)\]\s*\(\s*(.*?)\s*\)", "Download Link", snapshot.value
            )
            st.session_state.current_message = text_value
            st.session_state.current_markdown.markdown(
                st.session_state.current_message, True
            )

    @override
    def on_text_done(self, text):
        st.session_state.current_markdown.markdown(text.value, True)
        st.session_state.chat_log.append({"name": "assistant", "msg": text.value})

    @override
    def on_tool_call_created(self, tool_call):
        if tool_call.type == "code_interpreter":
            st.session_state.current_tool_input = ""
            with st.chat_message("Assistant"):
                st.session_state.current_tool_input_markdown = st.empty()

    @override
    def on_tool_call_delta(self, delta, snapshot):
        if 'current_tool_input_markdown' not in st.session_state:
            with st.chat_message("Assistant"):
                st.session_state.current_tool_input_markdown = st.empty()

        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                st.session_state.current_tool_input += delta.code_interpreter.input
                input_code = f"### code interpreter\ninput:\n```python\n{st.session_state.current_tool_input}\n```"
                st.session_state.current_tool_input_markdo

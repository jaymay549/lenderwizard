import os
import re
import streamlit as st
import openai
from openai import AssistantEventHandler
from typing_extensions import override
from dotenv import load_dotenv

load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Chat Interface",
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

# Define the functions for handling chat messages
def create_thread(content):
    messages = [{"role": "user", "content": content}]
    thread = client.beta.threads.create()
    return thread

def create_message(thread, content):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=content, attachments=[]
    )

def run_stream(user_input):
    if "thread" not in st.session_state:
        st.session_state.thread = create_thread(user_input)
    create_message(st.session_state.thread, user_input)
    with client.beta.threads.runs.stream(
        thread_id=st.session_state.thread.id,
        assistant_id=assistant_id,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

def render_chat():
    for chat in st.session_state.chat_log:
        if chat["name"] == "user":
            st.markdown(
                f'<div class="chat-message user"><div class="message-content">{chat["msg"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-message assistant"><div class="message-content">{chat["msg"]}</div></div>',
                unsafe_allow_html=True,
            )

if "tool_call" not in st.session_state:
    st.session_state.tool_calls = []

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

if "in_progress" not in st.session_state:
    st.session_state.in_progress = False

def disable_form():
    st.session_state.in_progress = True

def main():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.markdown('<div class="chat-header"><h2>Chat</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

    render_chat()
    
    st.markdown('</div>', unsafe_allow_html=True)

    user_msg = st.text_input(
        "Type a message", key="input", on_change=disable_form, disabled=st.session_state.in_progress
    )

    if user_msg:
        with st.chat_message("user"):
            st.markdown(user_msg, True)
        st.session_state.chat_log.append({"name": "user", "msg": user_msg})
        run_stream(user_msg)
        st.session_state.in_progress = False
        st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

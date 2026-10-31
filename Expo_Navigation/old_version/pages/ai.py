import streamlit as st
from pathlib import Path
from PIL import Image
from classes.style_manager import StyleManager
from classes.chatbot import get_response


# Page configuration
st.set_page_config(
    page_title="EXORA AI",
    page_icon="💬",
    layout="centered"
)


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
IMAGE_PATH = BASE_DIR / "assets" / "exora.jpg"


# Load assistant avatar
if IMAGE_PATH.exists():
    assistant_avatar = Image.open(IMAGE_PATH)
else:
    assistant_avatar = "💬"


# Page title
st.title("EXORA AI")
st.caption("Your multilingual Expo assistant")

st.divider()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Clear conversation
col1, col2 = st.columns([4, 1])

with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# Welcome message
if not st.session_state.messages:

    with st.chat_message("assistant", avatar=assistant_avatar):

        st.markdown(
            """
            **Hello! Welcome to EXORA AI 👋**

            I'm your smart Expo assistant.

            I can help you with:
            
            - 🌍 Discovering pavilions.
            - 🧭 Finding your destination.
            - 🚶 Exploring exhibition routes.
            - 🌐 Answering questions in multiple languages.

            How can I help you today?
            """
        )


# Display conversation history
for message in st.session_state.messages:

    avatar = (
        assistant_avatar
        if message["role"] == "assistant"
        else "user"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):
        st.markdown(message["content"])


# User input
user_input = st.chat_input("Message EXORA...")


if user_input:

    # Display user message
    with st.chat_message("user", avatar="user"):
        st.markdown(user_input)

    # Get conversation history
    history = st.session_state.messages.copy()

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Generate AI response
    with st.chat_message(
        "assistant",
        avatar=assistant_avatar
    ):

        with st.spinner("EXORA is thinking... 💭"):

            try:

                answer = get_response(
                    user_input,
                    history
                )

                st.markdown(answer)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                st.error(
                    "Sorry, something went wrong. "
                    "Please try again."
                )

                st.caption(f"Error details: {e}")

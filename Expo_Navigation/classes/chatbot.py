from langchain_ollama import ChatOllama
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

# Load the LLM
llm = ChatOllama(
    model="llama3.2",
    temperature=0.7
)

# Multilingual chatbot instructions
system_message = SystemMessage(
    content=(
        "You are a helpful multilingual assistant. "
        "Reply in the same language as the user's latest message. "
        "Support Arabic, English, and other languages when possible. "
        "Keep answers simple, clear, and friendly."
    )
)


def get_response(user_input, history=None):
    """Generate a chatbot response."""

    if history is None:
        history = []

    messages = [system_message]

    for message in history:
        if message["role"] == "user":
            messages.append(
                HumanMessage(content=message["content"])
            )
        elif message["role"] == "assistant":
            messages.append(
                AIMessage(content=message["content"])
            )

    messages.append(HumanMessage(content=user_input))

    response = llm.invoke(messages)

    return response.content
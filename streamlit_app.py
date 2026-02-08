import streamlit as st
from main import agent, predict_intent  # reuse your existing logic


# PAGE CONFIG

st.set_page_config(
    page_title="Agentic AI Chatbot",
    layout="centered"
)

st.title("Agentic AI Chatbot")
st.caption("MCP + Web + ML/DL powered chatbot")


# SESSION STATE

if "messages" not in st.session_state:
    st.session_state.messages = []


# DISPLAY CHAT HISTORY

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# USER INPUT

user_input = st.chat_input("Ask me something...")

if user_input:
    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Agent response
    intent, confidence = predict_intent(user_input)
    response = agent(user_input)

    with st.chat_message("assistant"):
        st.markdown(response)

        # Optional debug info (VERY GOOD FOR DEMO)
        with st.expander("Agent reasoning"):
            st.write(f"**Detected intent:** `{intent}`")
            st.write(f"**Confidence:** `{round(confidence, 2)}`")

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

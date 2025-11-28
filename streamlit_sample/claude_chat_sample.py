import streamlit as st
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")

# Setup proxies via environment variables
if HTTP_PROXY:
    os.environ["HTTP_PROXY"] = HTTP_PROXY
if HTTPS_PROXY:
    os.environ["HTTPS_PROXY"] = HTTPS_PROXY

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Streamlit UI
st.set_page_config(page_title="Claude Chat Sample", page_icon=":robot:")
st.title("Claude Chat Sample")

# session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "こんにちは！何かお手伝いできますか？"
        }
    ]

# display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# user input
if prompt := st.chat_input("メッセージを入力してください"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Claude API call
    with st.chat_message("assistant"):
        with st.spinner("考え中..."):
            response = client.messages.create(
                model="claude-4-sonnet-20250514",
                max_tokens=1000,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )
            reply = response.content[0].text

            st.write(reply)
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

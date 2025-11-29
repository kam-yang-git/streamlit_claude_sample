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


@st.cache_data(show_spinner=False)
def get_available_models():
    """
    Anthropic から利用可能なモデル一覧を取得するヘルパー。
    取得に失敗した場合は、よく使うモデルの固定リストを返す。
    """
    try:
        models_page = client.models.list()
        # models_page.data は Model オブジェクトのリスト
        model_ids = [m.id for m in models_page.data]

        # Claude 系だけに絞る（お好みで調整）
        claude_models = [
            mid for mid in model_ids
            if mid.startswith("claude-")
        ]

        # 何も取れなかった場合はフォールバック
        if not claude_models:
            raise ValueError("No Claude models found")

        # ID には日付が含まれているので、文字列降順にすると「新しいモデルが上」になる
        return sorted(claude_models, reverse=True)
    except Exception as e:
        # API エラー時は固定の候補を返す
        return [
            "claude-3-7-sonnet-20250219",
            "claude-3-7-haiku-20250219",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]


# Streamlit UI
st.set_page_config(page_title="Claude Chat Sample", page_icon=":robot:")
st.title("Claude Chat Sample")

if "model" not in st.session_state:
    # デフォルトモデル
    st.session_state["model"] = "claude-sonnet-4-20250514"

# session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "こんにちは！何かお手伝いできますか？"
        }
    ]

# 利用可能なモデル一覧を取得
available_models = get_available_models()

# チャットが開始されたかどうか（ユーザーメッセージがあるか）
chat_started = any(m["role"] == "user" for m in st.session_state["messages"])

# 現在のモデルが一覧にない場合は先頭を選ぶ
if st.session_state["model"] not in available_models:
    st.session_state["model"] = available_models[0]

# モデル選択 UI（チャット開始後は変更不可）
selected_model = st.selectbox(
    "使用する Claude モデルを選択してください（API から取得）",
    options=available_models,
    index=available_models.index(st.session_state["model"]),
    disabled=chat_started,
    help="チャット開始前にモデルを選択してください（開始後は変更できません）。",
)

if not chat_started:
    st.session_state["model"] = selected_model

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
                model=st.session_state["model"],
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

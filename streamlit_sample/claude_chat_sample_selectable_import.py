import streamlit as st
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import json

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


def get_jst_now_str() -> str:
    """日本時間 (JST) の現在時刻を yyyy/mm/dd hh:mm:ss 形式で返す。"""
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S")


def format_chat_as_markdown(messages) -> str:
    """チャット履歴を Markdown 文字列に整形する。"""
    lines = ["# Chat Transcript", ""]
    for msg in messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        model_name = msg.get("model")

        if role == "user":
            header = f"## User ({timestamp})"
        else:
            if model_name:
                header = f"## Assistant - {model_name} ({timestamp})"
            else:
                header = f"## Assistant ({timestamp})"

        lines.append(header)
        lines.append("")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


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
            "content": "こんにちは！何かお手伝いできますか？",
            "timestamp": get_jst_now_str(),
            "model": None,
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
    timestamp = msg.get("timestamp")
    model_name = msg.get("model")

    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
            if timestamp:
                st.caption(f"投稿時刻 (JST): {timestamp}")
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])
            caption_parts = []
            if model_name:
                caption_parts.append(f"モデル: {model_name}")
            if timestamp:
                caption_parts.append(f"投稿時刻 (JST): {timestamp}")
            if caption_parts:
                st.caption(" / ".join(caption_parts))

# user input
if prompt := st.chat_input("メッセージを入力してください"):
    # ユーザー投稿を保存（JST 時刻付き）
    user_timestamp = get_jst_now_str()
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "timestamp": user_timestamp,
        }
    )

    with st.chat_message("user"):
        st.write(prompt)
        st.caption(f"投稿時刻 (JST): {user_timestamp}")

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

            # AI レスポンスのメタ情報
            assistant_timestamp = get_jst_now_str()
            assistant_model = st.session_state["model"]

            st.write(reply)
            st.caption(
                f"モデル: {assistant_model} / 投稿時刻 (JST): {assistant_timestamp}"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": reply,
                    "timestamp": assistant_timestamp,
                    "model": assistant_model,
                }
            )

# チャット復元・保存エリア（入力欄の下に固定表示）
st.markdown("---")
st.subheader("チャットの復元・保存")

# チャットの復元
st.markdown("#### チャットの復元")
uploaded_file = st.file_uploader(
    "保存したJSONファイルをアップロードしてチャットを復元",
    type=["json"],
    help="以前保存したチャット履歴のJSONファイルを選択してください。",
)

# 最後に処理したファイルIDを追跡（同じファイルの再処理を防ぐ）
if "last_processed_file_id" not in st.session_state:
    st.session_state["last_processed_file_id"] = None

if uploaded_file is not None:
    # ファイルIDを取得（Streamlitのファイルアップローダーはfile_id属性を持っている）
    current_file_id = getattr(uploaded_file, "file_id", None)
    if current_file_id is None:
        # file_idがない場合は、ファイル名とサイズの組み合わせで識別
        current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # 既に処理済みのファイルの場合はスキップ（何も表示しない）
    if st.session_state["last_processed_file_id"] != current_file_id:
        try:
            # JSONファイルを読み込む（ファイルポインタを先頭に戻す）
            uploaded_file.seek(0)
            loaded_messages = json.load(uploaded_file)
            
            # 基本的な検証
            if not isinstance(loaded_messages, list):
                st.error("❌ 無効なJSON形式です。メッセージの配列である必要があります。")
            elif len(loaded_messages) == 0:
                st.error("❌ チャット履歴が空です。")
            else:
                # 各メッセージの形式を検証
                valid = True
                for i, msg in enumerate(loaded_messages):
                    if not isinstance(msg, dict):
                        st.error(f"❌ {i+1}番目のメッセージが無効な形式です。")
                        valid = False
                        break
                    if "role" not in msg or "content" not in msg:
                        st.error(f"❌ {i+1}番目のメッセージに 'role' または 'content' がありません。")
                        valid = False
                        break
                    if msg["role"] not in ["user", "assistant"]:
                        st.error(f"❌ {i+1}番目のメッセージの 'role' が無効です。")
                        valid = False
                        break
                
                if valid:
                    # 復元実行
                    st.session_state["messages"] = loaded_messages
                    
                    # モデル情報を復元（最初のassistantメッセージから取得）
                    for msg in loaded_messages:
                        if msg.get("role") == "assistant" and msg.get("model"):
                            st.session_state["model"] = msg["model"]
                            break
                    
                    # 処理済みファイルIDを記録
                    st.session_state["last_processed_file_id"] = current_file_id
                    
                    st.success(f"✅ チャット履歴を復元しました（{len(loaded_messages)}件のメッセージ）。")
                    st.rerun()  # 画面を再描画して復元された履歴を表示
                    
        except json.JSONDecodeError as e:
            st.error(f"❌ JSONの解析に失敗しました: {e}")
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
else:
    # ファイルがクリアされたら、処理済みフラグもクリア
    if st.session_state["last_processed_file_id"] is not None:
        st.session_state["last_processed_file_id"] = None

st.markdown("---")
st.markdown("#### チャットの保存")

if st.session_state.messages:
    # JSON 文字列と Markdown 文字列を用意
    chat_json_str = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    chat_md_str = format_chat_as_markdown(st.session_state.messages)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="このチャットを JSON で保存",
            data=chat_json_str.encode("utf-8"),
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )
    with col2:
        st.download_button(
            label="このチャットを Markdown で保存",
            data=chat_md_str.encode("utf-8"),
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
        )
else:
    st.info("保存できるチャット履歴がまだありません。")

## Streamlit Claude Chat Sample

このリポジトリは、Anthropic Claude API を使ったシンプルなチャット UI のサンプルです。  
`streamlit` を利用してブラウザ上にチャット画面を表示し、Claude との対話を行います。

---

## 動作環境

- **Python**: 3.9 以上推奨
- **主要ライブラリ**:
  - `streamlit`
  - `anthropic`
  - `python-dotenv`
- **Claude のモデル**: `claude-4-sonnet-20250514`

---

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <このリポジトリのURL>
cd streamlit_claude_sample
```

### 2. 仮想環境の作成・有効化（任意）

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell の場合
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

---

## 環境変数の設定

`streamlit_sample/claude_chat_sample.py` では `python-dotenv` を用いて `.env` ファイルから環境変数を読み込んでいます。  
ルートディレクトリの `.env_sample` をコピーして `.env` にリネームし、以下のように設定してください。

```env
ANTHROPIC_API_KEY=あなたのAPIキー
HTTP_PROXY=  # 必要な場合のみ
HTTPS_PROXY= # 必要な場合のみ
```

- **ANTHROPIC_API_KEY**: Anthropic の API キー（必須）
- **HTTP_PROXY / HTTPS_PROXY**: プロキシ等を利用する場合のみ設定（不要なら空のままで構いません）

---

## アプリの起動方法

ルートディレクトリ（`streamlit_claude_sample`）で以下を実行します。

```bash
streamlit run streamlit_sample/claude_chat_sample.py
```

コマンド実行後、ブラウザが自動的に開くか、コンソールに表示される URL（通常は `http://localhost:8501`）にアクセスするとチャット画面が表示されます。

---

## アプリの概要

- 画面上部にタイトル **"Claude Chat Sample"** が表示されます。
- 画面下部の入力欄からメッセージを送信すると、セッション内の会話履歴を元に Claude が返信します。
- 会話履歴は `st.session_state["messages"]` に保存され、ページを再読み込みするまで維持されます。
- Claude のモデルを変更したい場合は、`claude_chat_sample.py` の51行目を変更してください。

---

## トラブルシューティング

- **API キーエラー（認証失敗）**:
  - `.env` の `ANTHROPIC_API_KEY` が正しく設定されているか確認してください。
- **プロキシ関連のエラー**:
  - プロキシが必要な場合は、`HTTP_PROXY` / `HTTPS_PROXY` を適切な値に設定してください。
- **ポートがすでに使用されているエラー**:
  - 他の `streamlit` アプリなどが `8501` ポートを使用している可能性があります。
  - `streamlit run streamlit_sample/claude_chat_sample.py --server.port 8502` など、別ポートを指定して起動してください。

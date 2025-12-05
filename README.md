## Streamlit Claude Chat Sample

このリポジトリは、Anthropic Claude API を使ったチャット UI のサンプル集です。  
`streamlit` を利用してブラウザ上にチャット画面を表示し、Claude との対話を行います。

---

## 動作環境

- **Python**: 3.9 以上推奨
- **主要ライブラリ**:
  - `streamlit`
  - `anthropic`
  - `python-dotenv`

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
streamlit run streamlit_sample/<ファイル名>.py
```

コマンド実行後、ブラウザが自動的に開くか、コンソールに表示される URL（通常は `http://localhost:8501`）にアクセスするとチャット画面が表示されます。

---

## アプリの終了方法

アプリを終了するには、**ターミナル/コマンドプロンプトで `Ctrl + C` を押してサーバーを停止**してください。

- ブラウザを閉じるだけでは、Streamlitサーバーは実行し続けます
- ターミナルで `Ctrl + C` を押すと、サーバーが停止し、ブラウザ側も自動的に接続できなくなります
- サーバー停止後は、ブラウザを閉じても閉じなくても構いません

---

## 各アプリの機能一覧

| ファイル名 | 機能概要 | 主な特徴 |
|-----------|---------|---------|
| `claude_simple.py` | シンプルなチャットアプリ | 基本的なチャット機能のみ。モデルは `claude-sonnet-4-20250514` 固定。会話履歴はセッション内で保持。 |
| `claude_selectable_save.py` | モデル選択・保存機能付きチャット | モデル選択機能（APIから取得）、タイムスタンプ表示、チャット履歴の保存（JSON/Markdown形式）。チャット開始後はモデル変更不可。 |
| `claude_selectable_save_import.py` | 復元機能付きチャット | 上記の機能に加えて、保存したJSONファイルからチャット履歴を復元する機能を追加。 |

### 詳細説明

#### `claude_simple.py`
最もシンプルな実装。基本的なチャット機能のみを提供します。
- 固定モデル（`claude-sonnet-4-20250514`）を使用
- セッション内で会話履歴を保持
- シンプルなUI

#### `claude_selectable_save.py`
モデル選択とチャット保存機能を追加したバージョン。
- **モデル選択**: Anthropic APIから利用可能なClaudeモデル一覧を取得し、選択可能
- **タイムスタンプ**: 各メッセージに日本時間（JST）のタイムスタンプを表示
- **チャット保存**: 
  - JSON形式で保存（メタ情報含む）
  - Markdown形式で保存（読みやすい形式）
- **モデル固定**: チャット開始後はモデル変更不可（一貫性のため）

#### `claude_selectable_save_import.py`
チャット復元機能を追加したバージョン。
- `claude_selectable_save.py` の全機能を含む
- **チャット復元**: 保存したJSONファイルをアップロードして、以前の会話を復元可能
- 復元時にはモデル情報も自動的に復元

---

## トラブルシューティング

- **API キーエラー（認証失敗）**:
  - `.env` の `ANTHROPIC_API_KEY` が正しく設定されているか確認してください。
- **プロキシ関連のエラー**:
  - プロキシが必要な場合は、`HTTP_PROXY` / `HTTPS_PROXY` を適切な値に設定してください。
- **ポートがすでに使用されているエラー**:
  - 他の `streamlit` アプリなどが `8501` ポートを使用している可能性があります。
  - `streamlit run streamlit_sample/<ファイル名>.py --server.port 8502` など、別ポートを指定して起動してください。

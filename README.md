# Web-AI-Agent

Web-AI-Agent は、自然言語による指示を受け取り、Ope3. 環境変数を設定する：

プロジェクトルートに`.env`ファイルがあります。このファイルを編集して、APIキーなどの設定を行います：

```
# .envファイルの例
OPENAI_API_KEY=your_openai_api_key_here
BROWSER_HEADLESS=false
BROWSER_SLOW_MO=50
```

`.env`ファイルは以下の設定をサポートしています：
- `OPENAI_API_KEY`: OpenAI APIキー（必須）
- `BROWSER_HEADLESS`: ブラウザをヘッドレスモードで実行するかどうか（true/false、デフォルト: false）
- `BROWSER_SLOW_MO`: ブラウザ操作のスローモーション値（ミリ秒、デフォルト: 0）

または、環境変数を直接設定することもできます：

```bash
# Linux/macOS
export OPENAI_API_KEY="your_openai_api_key_here"

# Windows
set OPENAI_API_KEY=your_openai_api_key_here
```てその指示をJSON形式の操作ステップに変換し、Playwrightを使用してブラウザで自動実行するPythonツールです。

## 概要

このプロジェクトは、以下のコンポーネントで構成されています：

```
┌────────────┐        ┌──────────────┐
│  ユーザー   │─────→│ ローカルAgent │
└────────────┘        └──────┬───────┘
                             │ REST API（OpenAI Chat API）
                   ┌────────▼──────────┐
                   │   OpenAI（ChatGPT） │
                   └────────▲──────────┘
                             │ スクリプトJSON
                ┌────────────┴────────────┐
                │ Playwright（Web操作実行） │
                └─────────────────────────┘
```

1. ユーザーは自然言語で指示を入力します。
2. OpenAI APIが自然言語指示をJSON形式の操作ステップに変換します。
3. Playwrightがそれらのステップを実際のブラウザで実行します。

## インストール

### 前提条件

- Python 3.8以上
- OpenAI APIキー

### インストール手順

1. リポジトリをクローンまたはダウンロードします。

```bash
git clone https://github.com/yourusername/Web-AI-Agent.git
cd Web-AI-Agent
```

2. 必要なパッケージをインストールします。

```bash
pip install -r requirements.txt
playwright install
```

3. OpenAI APIキーを設定します。

```bash
# Linux/macOS
export OPENAI_API_KEY="your_openai_api_key_here"

# Windows
set OPENAI_API_KEY=your_openai_api_key_here
```

または、ソースコード内でAPIキーを直接指定することもできます（推奨されません）。

## 使用方法

### コマンドライン引数による指定

```bash
python run.py "Googleで東京の天気を検索する"
```

### 対話的使用

```bash
python run.py
```

プロンプトが表示されたら、実行したい操作を自然言語で入力します。

### オプション

- `--api-key`: OpenAI APIキーを直接指定することができます。

```bash
python run.py "Twitterにログインする" --api-key "your_openai_api_key_here"
```

## サポートされる操作

現在、以下の操作がサポートされています：

- `open_url`: Webサイトを開く
- `click`: 要素をクリック
- `type`: テキストを入力
- `wait`: 特定の時間またはセレクタが現れるまで待機
- `select`: ドロップダウンから選択

## プロジェクト構造

```
Web-AI-Agent/
├── run.py                 # メインエントリーポイント
├── requirements.txt       # 依存関係
├── README.md              # このファイル
└── src/                   # ソースコード
    ├── __init__.py
    ├── agent.py           # AIエージェント（OpenAI API関連）
    ├── browser.py         # ブラウザ自動化（Playwright関連）
    └── main.py            # CLI処理とメインロジック
```

## サンプル指示

```
"Googleにアクセスして、「東京 天気」と検索し、検索結果を表示する"
```

```
"YouTubeにアクセスして、「猫 かわいい」で検索し、最初の動画を再生する"
```

## ライセンス

MITライセンス

## 注意事項

- このツールは、テスト・教育目的でのみ使用してください。
- 不正なアクセスや自動化が禁止されているサイトでの使用は避けてください。
- APIキーは安全に管理し、ソースコード内に直接記述しないでください。

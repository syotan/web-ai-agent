import os
import json
import asyncio
import chainlit as cl
from dotenv import load_dotenv
from pathlib import Path

# アプリケーション自体のモジュールをインポート
from src.agent import AIAgent
from src.browser import BrowserAutomation

# .envファイルからの環境変数読み込み
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path)

# OpenAI APIキーを環境変数から取得
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here")

# グローバル変数
agent = None


@cl.on_chat_start
async def setup():
    """
    チャットセッション開始時の初期化処理
    """
    global agent
    
    # AIエージェントの初期化
    agent = AIAgent(OPENAI_API_KEY)
    
    # ウェルカムメッセージを表示
    await cl.Message(
        content="# 🤖 Web-AI-Agent へようこそ！\n\n"
                "自然言語で指示するだけで、Webブラウザの操作を自動化します。\n\n"
                "**例えば次のような指示を入力してみてください：**\n"
                "- Googleで「東京 天気」を検索する\n"
                "- YouTubeにアクセスして、「猫 かわいい」で検索する\n"
                "- Amazonで「ノートパソコン」を検索して、価格順にソートする\n\n"
                "指示を入力してください！"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    ユーザーからのメッセージ受信時の処理
    
    Args:
        message: ユーザーから受信したメッセージ
    """
    # ユーザーからの指示
    instruction = message.content
    
    # 処理中であることを通知
    processing_msg = cl.Message(content="OpenAI APIを使用して操作ステップを生成中...")
    await processing_msg.send()
    
    try:
        # AIエージェントによるJSONステップ生成
        steps = await agent.generate_steps(instruction)
        
        if not steps:
            await cl.Message(content="操作ステップの生成に失敗しました。別の指示を試してください。").send()
            return
        
        # ステップ情報をテーブル形式で表示
        table_data = {
            "headers": ["アクション", "セレクタ", "値"],
            "rows": []
        }
        
        for step in steps:
            action = step.get("action", "")
            selector = step.get("selector", "")
            value = step.get("value", "")
            table_data["rows"].append([str(action), str(selector), str(value)])
        
        # Markdownテーブルの生成
        headers = table_data["headers"]
        rows = table_data["rows"]
        md_table = "| " + " | ".join(headers) + " |\n"
        md_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"
        for row in rows:
            md_table += "| " + " | ".join([str(cell) for cell in row]) + " |\n"
        
        # テーブルとJSONをまとめて送信
        md_content = "以下の操作ステップが生成されました。実行しますか？\n\n"
        md_content += md_table
        md_content += "\n```json\n" + json.dumps(steps, indent=2, ensure_ascii=False) + "\n```"
        await cl.Message(content=md_content).send()

        # 実行確認を待機
        res = await cl.AskActionMessage(
            content="操作を実行しますか？",
            actions=[
                cl.Action(name="execute", payload={"action": "execute"}, label="実行する"),
                cl.Action(name="cancel", payload={"action": "cancel"}, label="キャンセル")
            ]
        ).send()

        if res and res.get("payload", {}).get("action") == "execute":
            # 実行処理
            await cl.Message(content="ブラウザでステップを実行中...").send()

            # BrowserAutomationのインスタンスを作成
            browser = BrowserAutomation()

            # ステップの詳細を出力
            steps_debug = "\n".join([f"- {s.get('action', '')}: {s.get('selector', '')} {s.get('value', '')}" for s in steps])
            await cl.Message(content=f"実行するステップの詳細:\n```\n{steps_debug}\n```").send()

            # 実行結果を返すタスクを作成
            try:
                # 直接実行して例外をキャッチ
                await browser.run_steps(steps)
                await cl.Message(content="✅ 操作が完了しました！").send()
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                await cl.Message(content=f"❌ 操作実行中にエラーが発生しました: {e}\n\n```\n{error_details}\n```").send()
        else:
            await cl.Message(content="操作をキャンセルしました。").send()

    except Exception as e:
        await cl.Message(content=f"エラーが発生しました: {e}").send()


if __name__ == "__main__":
    # ローカルで実行する場合のエントリーポイント
    # chainlit run app.py -w
    pass

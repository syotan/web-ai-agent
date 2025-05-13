#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIエージェント型の画面操作自動化システム - メインエントリーポイント
"""

import sys
import json
import asyncio
import argparse
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

from src.agent import AIAgent
from src.browser import BrowserAutomation

# .envファイルからの環境変数読み込み
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path)

# OpenAI APIキーを環境変数から取得
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here")


async def process_instruction(instruction: str, api_key: Optional[str] = None) -> None:
    """
    ユーザーの指示を処理する
    
    Args:
        instruction: ユーザーからの自然言語指示
        api_key: OpenAI APIキー（指定がない場合は環境変数またはデフォルト値を使用）
    """
    # APIキーを設定
    api_key = api_key or OPENAI_API_KEY
    
    print(f"指示: {instruction}")
    print("OpenAI APIを使用して操作ステップを生成中...")
    
    # AIエージェントとブラウザ自動化のインスタンスを作成
    agent = AIAgent(api_key)
    browser = BrowserAutomation()
    
    # 自然言語からJSONステップを生成
    steps = await agent.generate_steps(instruction)
    
    if steps:
        print("生成されたステップ:")
        print(json.dumps(steps, indent=2, ensure_ascii=False))
        
        # 確認プロンプト
        confirm = input("これらのステップを実行しますか？ (y/n): ")
        if confirm.lower() == 'y':
            print("ステップを実行中...")
            await browser.run_steps(steps)
        else:
            print("実行をキャンセルしました。")
    else:
        print("有効なステップが生成されませんでした。別の指示を試してください。")


async def main_async():
    """
    非同期的にメイン処理を実行する
    """
    parser = argparse.ArgumentParser(description='AIエージェント型画面操作自動化システム')
    parser.add_argument('instruction', nargs='?', help='自然言語による指示')
    parser.add_argument('--api-key', help='OpenAI APIキー（指定がない場合は環境変数から取得）')
    args = parser.parse_args()
    
    # コマンドライン引数から指示を取得、なければ入力を促す
    instruction = args.instruction
    if not instruction:
        instruction = input("実行したい操作を自然言語で入力してください: ")
    
    await process_instruction(instruction, args.api_key)


def main():
    """
    メイン関数
    """
    # OSによってはポリシーの設定が必要
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 非同期処理を実行
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

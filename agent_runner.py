#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIエージェント型の画面操作自動化システム

インストール方法:
- pip install openai playwright
- playwright install  # Playwrightのブラウザをインストール
"""

import json
import sys
import argparse
import asyncio
from typing import List, Dict, Any

# OpenAI APIのインポート
import openai
from playwright.async_api import async_playwright

# OpenAI APIキーを設定（実際の使用時は環境変数などから安全に読み込むことを推奨）
# 以下は例として直接記述していますが、実際の使用時には環境変数などから取得してください
OPENAI_API_KEY = "your_openai_api_key_here"


async def generate_steps_from_natural_language(instruction: str) -> List[Dict[str, Any]]:
    """
    自然言語の指示からJSONステップを生成する関数
    
    Args:
        instruction: ユーザーからの自然言語指示
        
    Returns:
        UIアクションのステップリスト（JSON形式）
    """
    # OpenAI APIキーを設定
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    # プロンプトを作成
    system_prompt = """
    あなたはWebサイト操作の自動化を支援するAIです。
    ユーザーの自然言語による指示をJSONフォーマットの操作ステップに変換してください。
    
    以下のアクションタイプを使用できます：
    - open_url: Webサイトを開く（valueにURLを指定）
    - click: 要素をクリック（selectorに要素のセレクタを指定）
    - type: テキストを入力（selectorに要素のセレクタ、valueに入力テキストを指定）
    - wait: 特定の時間待機（valueにミリ秒を指定）
    - select: ドロップダウンから選択（selectorに要素のセレクタ、valueに選択肢の値を指定）
    
    レスポンスは必ず以下のJSON形式の配列で返してください：
    [
      {"action": "open_url", "value": "https://example.com"},
      {"action": "click", "selector": "text='ログイン'"},
      {"action": "type", "selector": "#username", "value": "user1"}
    ]
    
    JSONのみを返し、説明などは不要です。
    """
    
    try:
        # ChatGPT APIにリクエスト
        response = client.chat.completions.create(
            model="gpt-4o",  # 適切なモデルを指定
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction}
            ],
            temperature=0.2  # より決定論的な応答を得るため低い値を設定
        )
        
        # レスポンスからJSONステップを抽出
        steps_json = response.choices[0].message.content.strip()
        
        # JSON文字列をパース
        # 余分なテキストがある場合は、最初の[から最後の]までを抽出
        if '[' in steps_json and ']' in steps_json:
            start_idx = steps_json.find('[')
            end_idx = steps_json.rfind(']') + 1
            steps_json = steps_json[start_idx:end_idx]
            
        steps = json.loads(steps_json)
        return steps
    
    except Exception as e:
        print(f"エラー: JSONステップの生成に失敗しました: {e}")
        return []


async def run_steps(steps: List[Dict[str, Any]]) -> None:
    """
    Playwrightを使用してUIアクションを実行する関数
    
    Args:
        steps: 実行するUIアクションのステップリスト
    """
    async with async_playwright() as p:
        # ブラウザを起動（headless=Falseで可視化）
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            for step in steps:
                action = step.get("action", "")
                selector = step.get("selector", "")
                value = step.get("value", "")
                
                print(f"実行中: {action} - {selector} - {value}")
                
                if action == "open_url":
                    await page.goto(value)
                    await page.wait_for_load_state("networkidle")
                
                elif action == "click":
                    await page.click(selector)
                
                elif action == "type":
                    await page.fill(selector, value)
                
                elif action == "wait":
                    # valueが数字（ミリ秒）の場合
                    try:
                        wait_time = int(value)
                        await page.wait_for_timeout(wait_time)
                    except ValueError:
                        # valueがセレクタの場合
                        await page.wait_for_selector(value)
                
                elif action == "select":
                    await page.select_option(selector, value)
                
                # アクション実行後の短い待機（操作の安定性向上のため）
                await page.wait_for_timeout(500)
            
            # 全ステップ完了後、閲覧できるように少し待機
            print("すべてのステップが完了しました。5秒後に終了します...")
            await page.wait_for_timeout(5000)
        
        except Exception as e:
            print(f"UIアクション実行中にエラーが発生しました: {e}")
        
        finally:
            # ブラウザを閉じる
            await browser.close()


async def process_instruction(instruction: str) -> None:
    """
    ユーザーの指示を処理する関数
    
    Args:
        instruction: ユーザーからの自然言語指示
    """
    print(f"指示: {instruction}")
    print("OpenAI APIを使用して操作ステップを生成中...")
    
    # 自然言語からJSONステップを生成
    steps = await generate_steps_from_natural_language(instruction)
    
    if steps:
        print("生成されたステップ:")
        print(json.dumps(steps, indent=2, ensure_ascii=False))
        
        # 確認プロンプト
        confirm = input("これらのステップを実行しますか？ (y/n): ")
        if confirm.lower() == 'y':
            print("ステップを実行中...")
            await run_steps(steps)
        else:
            print("実行をキャンセルしました。")
    else:
        print("有効なステップが生成されませんでした。別の指示を試してください。")


async def main_async():
    """
    非同期的にメイン処理を実行する関数
    """
    parser = argparse.ArgumentParser(description='AIエージェント型画面操作自動化システム')
    parser.add_argument('instruction', nargs='?', help='自然言語による指示')
    args = parser.parse_args()
    
    # コマンドライン引数から指示を取得、なければ入力を促す
    instruction = args.instruction
    if not instruction:
        instruction = input("実行したい操作を自然言語で入力してください: ")
    
    await process_instruction(instruction)


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

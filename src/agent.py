#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIエージェントモジュール - 自然言語からJSON操作ステップへの変換を行う
"""

import json
from typing import List, Dict, Any
import openai


class AIAgent:
    """
    自然言語からPlaywright操作ステップへの変換を行うAIエージェントクラス
    """
    
    def __init__(self, api_key: str):
        """
        AIエージェントの初期化
        
        Args:
            api_key: OpenAI APIキー
        """
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    async def generate_steps(self, instruction: str) -> List[Dict[str, Any]]:
        """
        自然言語の指示からJSONステップを生成する
        
        Args:
            instruction: ユーザーからの自然言語指示
            
        Returns:
            UIアクションのステップリスト（JSON形式）
        """
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
            response = self.client.chat.completions.create(
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

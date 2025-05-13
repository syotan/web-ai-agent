#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ブラウザ操作モジュール - Playwrightを使用したブラウザ自動操作を行う
"""

import os
from typing import List, Dict, Any
from playwright.async_api import async_playwright


class BrowserAutomation:
    """
    Playwrightを使用したブラウザ自動操作クラス
    """
    
    async def run_steps(self, steps: List[Dict[str, Any]]) -> None:
        """
        JSONステップに基づいてブラウザ操作を実行する
        
        Args:
            steps: 実行するUIアクションのステップリスト
        """
        # 環境変数からブラウザ設定を取得
        headless_str = os.environ.get("BROWSER_HEADLESS", "false").lower()
        headless = headless_str == "true"
        slow_mo = int(os.environ.get("BROWSER_SLOW_MO", "0"))
        
        async with async_playwright() as p:
            # ブラウザを起動（環境変数からheadlessモードを設定）
            browser = await p.chromium.launch(headless=headless, slow_mo=slow_mo)
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

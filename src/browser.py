#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ブラウザ操作モジュール - Playwrightを使用したブラウザ自動操作を行う
"""

import os
import traceback
from typing import List, Dict, Any
import asyncio
from pathlib import Path
from playwright.async_api import Playwright, async_playwright


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
        
        # スクリーンショット保存用ディレクトリの作成
        screenshots_dir = Path("screenshots")
        if not screenshots_dir.exists():
            screenshots_dir.mkdir(exist_ok=True)
            print(f"スクリーンショットディレクトリを作成しました: {screenshots_dir}")
        
        print(f"ブラウザ設定: headless={headless}, slow_mo={slow_mo}")
        print(f"実行するステップ数: {len(steps)}")

        try:
            async with async_playwright() as p:
                # ブラウザを起動（環境変数からheadlessモードを設定）
                print("ブラウザを起動中...")
                browser = await p.chromium.launch(headless=headless, slow_mo=slow_mo)
                # より人間らしいブラウザとして認識されるための設定
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    viewport={'width': 1280, 'height': 720},
                    locale='ja-JP',
                    timezone_id='Asia/Tokyo',
                    has_touch=False,
                    ignore_https_errors=True
                )
                
                # Cookieコンセントや「お使いのPCから普段とは...」ダイアログに対応するためのイベント追加
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => false});
                """)
                
                # 自動化を検出するフラグを下げるための設定
                await context.grant_permissions(['geolocation'])
                page = await context.new_page()
                
                for i, step in enumerate(steps):
                    action = step.get("action", "")
                    selector = step.get("selector", "")
                    value = step.get("value", "")
                    
                    print(f"ステップ {i+1}/{len(steps)} 実行中: {action} - {selector} - {value}")
                    
                    if action == "open_url":
                        print(f"URLを開きます: {value}")
                        await page.goto(value)
                        print("ページ読み込み完了を待機中...")
                        await page.wait_for_load_state("networkidle")
                        print("ページ読み込み完了")
                        
                        # 現在のURLをログに出力
                        current_url = page.url
                        print(f"現在のURL: {current_url}")
                        
                        # Googleのログイン確認ダイアログの処理
                        if "google.com" in current_url:
                            print("Googleページを検出しました。ログインダイアログの確認中...")
                            
                            # セキュリティチェックメッセージの検出
                            security_messages = [
                                "お使いのPCから普段とは",
                                "不審なトラフィックが検出されました",
                                "ロボットではないことを確認",
                                "automated query",
                                "unusual traffic",
                                "security check"
                            ]
                            
                            # HTMLにセキュリティチェックのメッセージが含まれるか確認
                            content = await page.content()
                            has_security_check = any(msg in content for msg in security_messages)
                            
                            if has_security_check:
                                print("Google セキュリティチェックを検出しました。操作を中断します。")
                                print("ヒント: 別の検索エンジン（例：Bing, DuckDuckGo）を使用するか、しばらく時間をおいてから再試行してください。")
                                await page.screenshot(path=f"screenshots/google_security_check.png")
                                # 続行はせず、エラーとして表示するだけ
                                # 必要に応じてここでraiseしてもよい
                            
                            # reCAPTCHA検出と対応
                            try:
                                print("reCAPTCHAの検出を試みています...")
                                
                                # reCAPTCHAのiframeを探す
                                recaptcha_frame_selectors = [
                                    "iframe[title*='reCAPTCHA']", 
                                    "iframe[src*='recaptcha']", 
                                    "//iframe[contains(@title, 'reCAPTCHA')]"
                                ]
                                
                                for frame_selector in recaptcha_frame_selectors:
                                    frame_count = await page.locator(frame_selector).count()
                                    if frame_count > 0:
                                        print(f"reCAPTCHA iframe検出: {frame_selector}")
                                        
                                        # iframeを取得
                                        frame = await page.frame_locator(frame_selector).first
                                        if frame:
                                            # チェックボックスを探す
                                            checkbox_selectors = [
                                                ".recaptcha-checkbox-border",
                                                "//span[@role='checkbox']",
                                                "#recaptcha-anchor"
                                            ]
                                            
                                            for checkbox in checkbox_selectors:
                                                try:
                                                    if await frame.locator(checkbox).is_visible():
                                                        print(f"reCAPTCHAチェックボックス検出: {checkbox}")
                                                        await frame.locator(checkbox).click()
                                                        print("reCAPTCHAチェックボックスをクリックしました")
                                                        
                                                        # クリック後に少し待機
                                                        await page.wait_for_timeout(2000)
                                                        await page.screenshot(path="screenshots/recaptcha_clicked.png")
                                                        break
                                                except Exception as e:
                                                    print(f"reCAPTCHAクリックエラー: {e}")
                                
                                # iframe外でのreCAPTCHA検出
                                direct_checkbox_selectors = [
                                    ".recaptcha-checkbox-border", 
                                    "#recaptcha-anchor",
                                    "//div[@class='recaptcha-checkbox-border']",
                                    "//span[@role='checkbox' and contains(@aria-label, 'ロボット')]",
                                    "//span[@role='checkbox' and contains(@aria-label, 'robot')]"
                                ]
                                
                                for checkbox in direct_checkbox_selectors:
                                    try:
                                        checkbox_count = await page.locator(checkbox).count()
                                        if checkbox_count > 0 and await page.locator(checkbox).is_visible():
                                            print(f"直接reCAPTCHAチェックボックス検出: {checkbox}")
                                            await page.click(checkbox)
                                            print("reCAPTCHAチェックボックスをクリックしました")
                                            await page.wait_for_timeout(2000)
                                            await page.screenshot(path="screenshots/recaptcha_direct_clicked.png")
                                            break
                                    except Exception as e:
                                        print(f"直接reCAPTCHAクリックエラー: {e}")
                                
                            except Exception as e:
                                print(f"reCAPTCHA処理中のエラー: {e}")
                                print(traceback.format_exc())
                            
                            try:
                                # 日本語版「ログインしない」または英語版「No thanks」ボタンを探す
                                login_selectors = [
                                    "text='ログインしない'", 
                                    "text='No thanks'", 
                                    "text='今は設定しない'", 
                                    "text='Skip'",
                                    "button:has-text('ログインしない')",
                                    "button:has-text('No thanks')",
                                    "button:has-text('今は設定しない')",
                                    "button:has-text('Skip')",
                                    "text='同意する'",
                                    "text='同意して次へ'",
                                    "text='同意して続行'",
                                    "text='I agree'",
                                    "text='Accept'",
                                    "text='Accept all'",
                                    "button:has-text('同意する')",
                                    "button:has-text('同意して次へ')",
                                    "button:has-text('同意して続行')",
                                    "button:has-text('I agree')",
                                    "button:has-text('Accept')",
                                    "button:has-text('Accept all')"
                                ]
                                
                                for login_selector in login_selectors:
                                    visible = await page.locator(login_selector).is_visible()
                                    if visible:
                                        print(f"ログインダイアログを検出しました。'{login_selector}'をクリックします。")
                                        await page.click(login_selector)
                                        print("ログインダイアログをスキップしました")
                                        await page.wait_for_timeout(1000)  # 安定化のため少し待機
                                        break
                            except Exception as e:
                                print(f"ログインダイアログ処理中のエラー: {e}")
                        
                        # スクリーンショット保存
                        await page.screenshot(path=f"screenshots/step_{i+1}_open_url.png")
                    
                    elif action == "click":
                        print(f"クリック操作: {selector}")
                        # セレクタの要素が表示されるまで待機
                        try:
                            # 要素が存在するか確認
                            count = await page.locator(selector).count()
                            print(f"セレクタ '{selector}' に一致する要素数: {count}")
                            
                            if count > 0:
                                # 要素が表示されるまで待機
                                await page.wait_for_selector(selector, state="visible", timeout=5000)
                                # 要素のスクリーンショット
                                try:
                                    await page.locator(selector).screenshot(path=f"screenshots/step_{i+1}_element.png")
                                except:
                                    print("要素のスクリーンショットに失敗しました")
                                
                                # クリック実行
                                await page.click(selector)
                                print(f"クリック成功: {selector}")
                                await page.screenshot(path=f"screenshots/step_{i+1}_after_click.png")
                                
                                # クリック後にロード状態を待機
                                try:
                                    await page.wait_for_load_state("networkidle", timeout=5000)
                                except:
                                    print("ネットワークアイドル状態になりませんでした")
                            else:
                                print(f"警告: セレクタ '{selector}' に一致する要素が見つかりません")
                                # 現在のページ内容をログ
                                content = await page.content()
                                print(f"ページHTML（一部）: {content[:300]}...")
                                
                                # 代替セレクタを試す（特にGoogleの検索ボタンなど）
                                if "google" in page.url:
                                    alternative_selectors = [
                                        "input[name='btnK']",
                                        "input[value='Google 検索']", 
                                        "input[aria-label='Google 検索']",
                                        "input[value='Google Search']",
                                        "button[aria-label='Google 検索']",
                                        "button[aria-label='Google Search']"
                                    ]
                                    
                                    print("Googleページで代替セレクタを試します...")
                                    for alt_selector in alternative_selectors:
                                        try:
                                            alt_count = await page.locator(alt_selector).count()
                                            if alt_count > 0 and await page.locator(alt_selector).is_visible():
                                                print(f"代替セレクタが見つかりました: {alt_selector}")
                                                await page.click(alt_selector)
                                                print(f"代替セレクタでクリック成功: {alt_selector}")
                                                await page.screenshot(path=f"screenshots/step_{i+1}_alt_click.png")
                                                break
                                        except Exception as e:
                                            print(f"代替セレクタ試行中のエラー: {e}")
                                
                                await page.screenshot(path=f"screenshots/step_{i+1}_element_not_found.png")
                        except Exception as e:
                            print(f"クリックエラー: {e}")
                            await page.screenshot(path=f"screenshots/step_{i+1}_click_error.png")
                    
                    elif action == "type":
                        print(f"入力操作: {selector} に '{value}' を入力")
                        try:
                            # GoogleのURLの場合、検索ボックスのセレクタを確認
                            if "google.com" in page.url and selector in ["input[name='q']", "textarea[name='q']"]:
                                # 現在のページでセレクタが見つからない場合の代替処理
                                count = await page.locator(selector).count()
                                if count == 0:
                                    alt_selectors = ["textarea[name='q']", "input[name='q']", "[aria-label='検索']", "[aria-label='Search']"]
                                    for alt_selector in alt_selectors:
                                        alt_count = await page.locator(alt_selector).count()
                                        if alt_count > 0:
                                            print(f"代替検索ボックスセレクタを使用: {alt_selector}")
                                            selector = alt_selector
                                            break
                            
                            count = await page.locator(selector).count()
                            print(f"セレクタ '{selector}' に一致する要素数: {count}")
                            
                            if count > 0:
                                # 要素が表示されて入力可能になるまで待機
                                await page.wait_for_selector(selector, state="visible", timeout=5000)
                                # フォーカスを当ててから入力
                                await page.focus(selector)
                                # テキストをクリアしてから入力
                                await page.fill(selector, "")
                                await page.type(selector, value, delay=50)  # 適度な入力速度
                                print(f"入力成功: {selector}")
                                
                                # Enterキーを押す（検索実行などに対応）
                                if "google.com" in page.url and ("q" in selector or "検索" in selector or "Search" in selector):
                                    print("Googleの検索ボックスで入力後にEnterキーを押します")
                                    await page.keyboard.press('Enter')
                                    await page.wait_for_load_state("networkidle")
                                
                                await page.screenshot(path=f"screenshots/step_{i+1}_after_type.png")
                            else:
                                print(f"警告: 入力フィールド '{selector}' が見つかりません")
                                await page.screenshot(path=f"screenshots/step_{i+1}_input_not_found.png")
                        except Exception as e:
                            print(f"入力エラー: {e}")
                            await page.screenshot(path=f"screenshots/step_{i+1}_type_error.png")
                    
                    elif action == "wait":
                        # valueが数字（ミリ秒）の場合
                        try:
                            wait_time = int(value)
                            print(f"{wait_time}ミリ秒待機中...")
                            await page.wait_for_timeout(wait_time)
                            print("待機完了")
                            await page.screenshot(path=f"screenshots/step_{i+1}_after_wait.png")
                        except ValueError:
                            # valueがセレクタの場合
                            print(f"セレクタ待機中: {value}")
                            try:
                                await page.wait_for_selector(value, timeout=10000)
                                print(f"セレクタ出現確認: {value}")
                                await page.screenshot(path=f"screenshots/step_{i+1}_selector_found.png")
                            except Exception as e:
                                print(f"セレクタ待機エラー: {e}")
                                await page.screenshot(path=f"screenshots/step_{i+1}_wait_error.png")
                    
                    elif action == "select":
                        print(f"選択操作: {selector} で {value} を選択")
                        try:
                            count = await page.locator(selector).count()
                            print(f"セレクタ '{selector}' に一致する要素数: {count}")
                            
                            if count > 0:
                                await page.wait_for_selector(selector, state="visible", timeout=5000)
                                await page.select_option(selector, value)
                                print(f"選択成功: {selector}")
                                await page.screenshot(path=f"screenshots/step_{i+1}_after_select.png")
                            else:
                                print(f"警告: セレクト要素 '{selector}' が見つかりません")
                                await page.screenshot(path=f"screenshots/step_{i+1}_select_not_found.png")
                        except Exception as e:
                            print(f"選択エラー: {e}")
                            await page.screenshot(path=f"screenshots/step_{i+1}_select_error.png")
                    
                    # アクション実行後の短い待機（操作の安定性向上のため）
                    print("安定化のため500ms待機")
                    await page.wait_for_timeout(500)
                
                # 全ステップ完了後、閲覧できるように少し待機
                print("すべてのステップが完了しました。5秒後に終了します...")
                await page.screenshot(path="screenshots/completion.png")
                await page.wait_for_timeout(5000)
                
        except Exception as e:
            print(f"UIアクション実行中にエラーが発生しました: {e}")
            print(traceback.format_exc())

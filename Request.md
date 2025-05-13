あなたは熟練のPythonエンジニアであり、AIエージェント構築の専門家です。

以下の要件に基づき、PlaywrightとOpenAI APIを活用した、AIエージェント型の画面操作自動化システムを構築してください。

【目的】
ユーザーが自然言語で指示を与えると、OpenAI APIを介して操作ステップ（JSON形式）を生成し、それをPlaywrightで自動実行する一連の仕組みを作成したいです。

【構成】
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

【要件】
- Pythonで開発してください
- OpenAI API（Chat Completions）で自然言語 → JSONステップを生成
- JSONは以下のような形式：
    [
      {"action": "open_url", "value": "https://example.com"},
      {"action": "click", "selector": "text='ログイン'"},
      {"action": "type", "selector": "#username", "value": "user1"},
      {"action": "type", "selector": "#password", "value": "pass123"},
      {"action": "click", "selector": "#submit"}
    ]
- Playwrightで上記JSONに基づいてUI操作を実行するランタイム（`run_steps()`関数）を実装
- `main()`関数でCLIから自然言語指示を受け取り、上記一連を実行

【開発対象のファイル】
- agent_runner.py（すべての処理を含んだ最小構成でOK）

【補足】
- `openai` と `playwright` のインストール方法をコメントで記述してください
- セレクタは仮でよいので、自然な例を使ってください
- headless=False でUI操作が確認できるようにしてください

以上を踏まえ、agent_runner.py を生成してください。
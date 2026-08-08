import os
import json
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from tavily import TavilyClient

# APIキーの設定
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# 2026年最新仕様：文字列でモデルを指定します
gemini_model = "gemini/gemini-3.5-flash-lite"

# 【追加】今日の正確な日付を取得（AIに現在が2026年であることを認識させます）
today_str = datetime.now().strftime('%Y年%m月%d日')

# エラーの出ない安全な検索カスタムツールを定義
@tool("Web Search Tool")
def web_search_tool(query: str) -> str:
    """インターネット上の最新情報を検索するツールです。"""
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, max_results=3)
        results = response.get('results', [])
        
        summary = ""
        for r in results:
            summary += f"タイトル: {r.get('title')}\nURL: {r.get('url')}\n内容: {r.get('content')}\n\n"
        return summary if summary else "情報が見つかりませんでした。"
    except Exception as e:
        return f"検索エラーが発生しました: {str(e)}"

# 1. エージェントの定義
researcher = Agent(
    role='AI技術リサーチャー',
    goal='完全自動化・自律化AI技術に関する最新動向やツール、活用事例の正確な情報を収集する',
    backstory='最新のテクノロジー動向を見逃さない優秀な調査員です。信頼性の高い情報源から具体的な事例の情報を集めます。',
    tools=[web_search_tool],
    verbose=True,
    llm=gemini_model
)

writer = Agent(
    role='テックブログ編集長',
    goal='収集された情報を整理し、読者が読みやすいシンプルな日本語のブログ記事（HTML形式）を作成・更新する',
    backstory='難しい技術を分かりやすく解説する人気ブロガーです。最新情報をTOPに配置し、過去記事はアーカイブ化する構造を設計します。',
    verbose=True,
    llm=gemini_model
)

# 2. タスクの定義
search_task = Task(
    description='「完全自動化 自律型 AI 技術動向」「最新 AI 活用事例」について最新のニュースや記事を検索し、要点をまとめてください。',
    expected_output='最新のAI動向に関する詳細な調査レポート（日本語）',
    agent=researcher
)

write_task = Task(
    description=f'''
    調査レポートを基に、本日（{today_str}）の日付を入れた最新の【2026年】のAI技術動向記事を作成し、完全なHTMLコードとして出力してください。
    
    【必須デザインルール（インラインCSSで実装すること）】
    1. 背景色は洗練されたダークグレー（#0f172a）、文字色は読みやすいオフホワイト（#f8fafc）の「ダークモード仕様」にしてください。
    2. 全体を中央寄せ（最大幅800px）にし、スタイリッシュなフォント（sans-serif）を使用し、余白を広めにとって高級感を出してください。
    3. 見出し（H2, H3）は鮮やかなネオンブルー（#38bdf8）にし、重要な単語は太字で強調してください。
    4. 記事の各セクションは、背景を少し明るいコンテナ（#1e293b）で囲み、角を丸く（border-radius: 8px）してください。
    
    【構成ルール】
    - トップに「2026年 AI技術動向自動リサーチマガジン」といった洗練されたヘッダーを配置してください。
    - 存在しない架空の過去記事アーカイブやダミーリンクは【絶対に記述しないでください】。今回の最新記事1本だけを美しく完結させて表示してください。
    
    これがそのままindex.htmlとして保存されます。
    ''',
    expected_output='ダークモードデザインが適用された、嘘のない完全なHTMLコード',
    agent=writer,
    output_file='index.html'
)

# 3. クルーの実行
crew = Crew(
    agents=[researcher, writer],
    tasks=[search_task, write_task],
    process=Process.sequential
)

if __name__ == "__main__":
    crew.kickoff()

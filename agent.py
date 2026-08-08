import os
import json
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai_tools import TavilySearchTool

# APIキーの設定
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")
os.environ["TAVILY_API_KEY"] = os.environ.get("TAVILY_API_KEY", "")

# 検索ツールの初期化
search_tool = TavilySearchTool()

# 1. エージェントの定義
researcher = Agent(
    role='AI技術リサーチャー',
    goal='完全自動化・自律化AI技術に関する最新動向やツール、活用事例の正確な情報を収集する',
    backstory='最新のテクノロジー動向を見逃さない優秀な調査員です。信頼性の高い情報源から具体的な事例の情報を集めます。',
    tools=[search_tool],
    verbose=True
)

writer = Agent(
    role='テックブログ編集長',
    goal='収集された情報を整理し、読者が読みやすいシンプルな日本語のブログ記事（HTML形式）を作成・更新する',
    backstory='難しい技術を分かりやすく解説する人気ブロガーです。最新情報をTOPに配置し、過去記事はアーカイブ化する構造を設計します。',
    verbose=True
)

# 2. タスクの定義
search_task = Task(
    description='''
    1. 調査レポートを基に、本日の日付を入れた新しい記事を作成してください。
    2. index.html、archive.html、articles.json という名前の3つのファイルを直接作成・上書き保存してください。
    3. index.htmlはTOPページとして最新記事を一番上に表示し、archive.htmlは過去記事へのリンク一覧、articles.jsonには記事のデータを保存してください。デザインはシンプルで美しいブログ風にしてください。
    ''',


)

write_task = Task(
    description='''
    1. 調査レポートを基に、本日の日付を入れた新しい記事（HTMLの断片）を作成してください。
    2. 既存の `articles.json`（存在すれば）を読み込み、過去記事リストに今回の新しい記事を追加して保存してください。
    3. 最新記事が一番上にくる「TOPページ（index.html）」と、過去の記事一覧リンクが並ぶ「アーカイブページ（archive.html）」をシンプルで美しいデザインのHTMLとして出力・上書き保存してください。
    ''',
    expected_output='index.html, archive.html, articles.json の生成と更新',
    agent=writer
)

# 3. クルーの実行
crew = Crew(
    agents=[researcher, writer],
    tasks=[search_task, write_task],
    process=Process.sequential
)

if __name__ == "__main__":
    crew.kickoff()

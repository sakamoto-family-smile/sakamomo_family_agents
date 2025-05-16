import yfinance as yf
import pandas as pd
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import uuid
import asyncio
from dotenv import load_dotenv
import os
from typing import Optional
from datetime import datetime, timedelta


async def main():
    # .envファイルの読み込み
    load_dotenv()

    # GOOGLE_API_KEYの確認
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError(
            "GOOGLE_API_KEYが設定されていません。"
            ".envファイルにGOOGLE_API_KEYを設定してください。"
        )

    # 企業情報をお試しで表示
    try:
        display_ticker_datas()
    except Exception as e:
        print(f"企業情報の表示中にエラーが発生しました: {e}")

    # 株価分析処理
    stock_datas = get_stock_data(use_dummy_data=True)
    if stock_datas is not None and not stock_datas.empty:
        # エージェントの準備と実行
        agent = __build_agent()
        runner = __build_runner(agent)
        response = await __execute_agent(runner, stock_datas)

        print("--------------------------------")
        print("agent reponse:")
        print(response)
        print("--------------------------------")
    else:
        print("株価データの取得に失敗しました。")


def display_ticker_datas():
    # 企業を設定
    ticker_symbol = "7203.T"
    ticker_data = yf.Ticker(ticker_symbol)
    print(ticker_data.info)


def get_stock_data(use_dummy_data: bool = False) -> Optional[pd.DataFrame]:
    # ダミーデータを使用する場合
    if use_dummy_data:
        # 日付の生成（過去3ヶ月分）
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # ランダムな株価データの生成
        import numpy as np
        np.random.seed(42)  # 再現性のため

        # AAPLの初期値を150とし、日々の変動を±2%以内に設定
        aapl_base = 150
        aapl_daily_returns = np.random.uniform(-0.02, 0.02, len(dates))
        aapl_prices = aapl_base * (1 + np.cumsum(aapl_daily_returns))

        # GOOGLの初期値を2800とし、日々の変動を±2%以内に設定
        googl_base = 2800
        googl_daily_returns = np.random.uniform(-0.02, 0.02, len(dates))
        googl_prices = googl_base * (1 + np.cumsum(googl_daily_returns))

        return pd.DataFrame(
            {
                "AAPL": aapl_prices,
                "GOOGL": googl_prices
            },
            index=dates
        )

    # ターゲットとなる企業を設定
    target_company_list = ["AAPL", "GOOGL"]

    # yfinanceのデバッグモードを有効にする
    yf.enable_debug_mode()

    try:
        # 株価情報を取得
        stock_datas = yf.download(
            target_company_list,
            start="2024-03-01",
            end="2024-04-30"
        )
        if stock_datas is None:
            return None
        return None if stock_datas.empty else stock_datas
    except Exception as e:
        print(f"株価データの取得中にエラーが発生しました: {e}")
        return None


async def __execute_agent(runner: Runner, stock_data: pd.DataFrame) -> str:
    # セッション情報の取得
    sessions = runner.session_service.list_sessions(
        app_name=runner.app_name,
        user_id="sakamomo_family"
    )
    if not sessions or len(sessions.sessions) == 0:
        print("セッションが見つかりません。")
        return "セッションの取得に失敗しました。"

    session = sessions.sessions[0]

    # データフレームを文字列に変換
    data_str = stock_data.to_string()

    # 次の30日間の日付を生成
    today = datetime.now()
    future_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 31)]
    dates_str = '\n'.join(future_dates)

    # エージェントへのメッセージを作成
    message = f"""
    以下の株価データを分析し、次の30日間の株価予測を行ってください。

    株価データ:
    {data_str}

    以下の形式で予測結果を出力してください：

    1. 最初に、過去データの分析と予測の根拠を簡潔に説明してください。

    2. 次に、予測結果を以下のようなマークダウンテーブル形式で出力してください：

    | 日付 | AAPL予測価格 | AAPL変動率(%) | GOOGL予測価格 | GOOGL変動率(%) |
    |------|--------------|---------------|---------------|----------------|
    | YYYY-MM-DD | XXX.XX | +/-X.XX | XXX.XX | +/-X.XX |

    予測対象日:
    {dates_str}

    注意事項：
    - 各銘柄について、前日比の変動率も計算して表示してください
    - 市場の動向や企業のファンダメンタルズを考慮して予測を行ってください
    - 大きな価格変動が予測される場合は、その理由も説明に含めてください
    """

    # エージェントを実行
    print("\n=== 株価分析結果 ===")
    user_content = types.Content(
        role="user",
        parts=[types.Part(text=message)]
    )

    try:
        final_response_text = ""
        async for event in runner.run_async(
            user_id="sakamomo_family",
            session_id=str(session.id),
            new_message=user_content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    # 最終レスポンスのテキストを取得
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    # エラーや問題が発生した場合
                    error_msg = event.error_message or 'No specific message.'
                    final_response_text = f"Agent escalated: {error_msg}"
                break  # 最終レスポンスを取得したら処理を終了

        return final_response_text or "応答を取得できませんでした。"
    except Exception as e:
        error_message = f"エラーが発生しました: {e}"
        print(error_message)
        return error_message
    finally:
        print("==================\n")


def __build_agent() -> LlmAgent:
    # パラメーターの設定
    app_name = "analysis_finance_data"
    model_name = "gemini-2.0-flash-001"

    # LLMエージェントのビルド
    agent = LlmAgent(
        model=model_name,
        name=app_name,
        description=(
            "株価データを分析し、市場動向や傾向を分析する金融アナリストエージェントです。"
            "過去のデータから将来の株価予測を行い、その根拠とともに詳細な分析を提供します。"
        ),
        instruction=(
            "あなたは金融アナリストとして、株価データを分析し、将来の株価予測を行います。\n"
            "以下の点に注目して分析と予測を行ってください：\n"
            "1. 過去の株価トレンドと変動パターン\n"
            "2. 市場全体の動向と個別銘柄への影響\n"
            "3. 企業のファンダメンタルズと将来の成長性\n"
            "4. 予測される価格変動の根拠\n"
            "予測結果は必ず指定された表形式で出力し、\n"
            "予測の根拠となる分析も簡潔に説明してください。"
        )
    )
    return agent


def __build_runner(agent: LlmAgent) -> Runner:
    # パラメーターの設定
    app_name = agent.name
    user_id = "sakamomo_family"
    session_id = str(uuid.uuid4())

    # セッションサービスの作成
    session_service = InMemorySessionService()
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )

    # Runnerの生成
    return Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )


if __name__ == "__main__":
    asyncio.run(main())

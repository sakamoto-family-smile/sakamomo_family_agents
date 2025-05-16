from typing import Any, Dict, AsyncIterable, List, Literal
from pydantic import BaseModel
import os
import vertexai
from collections.abc import Iterable
from datetime import datetime
import json
from vertexai.generative_models import (
    GenerationConfig,
    GenerationResponse,
    GenerativeModel,
    SafetySetting,
    Part as vertexai_part
)
from google.cloud import bigquery
from proto.marshal.collections import RepeatedComposite
from logging import StreamHandler, getLogger
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph

from util.gcp_util import upload_file_into_gcs
from util.edinet_wrapper import EdinetUtil, EdinetWrapper

from common.types import (
    TaskState,
)


logger = getLogger(__name__)
# logger.addHandler(StreamHandler())
# logger.setLevel("DEBUG")


class AssetSecuritiesReportAgentConfig(BaseModel):
    agent_name: str = "AssetSecuritiesReportAgent"
    agent_description: str = "This agent generates a report on asset securities."
    agent_type: str = "reporting"
    agent_version: str = "0.0.1"
    agent_author: str = "shota.sakamoto"
    agent_author_email: str = ""
    llm_model_name: str = "gemini-1.5-flash-001"
    temperature: int = 0
    log_bucket_name: str = "sakamomo_family_service"
    log_base_folder: str = "log"
    debug_mode: bool = False
    analyze_prompt: str = """
上記の決算資料から、後述する観点についてそれぞれ分析を行なって、分析結果をまとめてください。

1. 経営戦略と事業内容:
    企業のビジョン、ミッション、経営理念を明確化し、その内容を評価してください。
    主要な事業セグメントとその内容、売上高、利益への貢献度を分析してください。
    市場における競争優位性と、その持続可能性について評価してください。
    今後の事業展開の方向性と、その実現可能性について分析してください。
    事業ポートフォリオを分析し、多角化の程度やリスク分散の状況を評価してください。

2. 財務状況:
    収益性、安全性、効率性の観点から財務状況を分析し、改善点や課題を指摘してください。
    収益性分析では、売上高総利益率、営業利益率などの指標の推移を分析し、その要因を考察してください。
    安全性分析では、流動比率、自己資本比率などの指標を分析し、財務リスクを評価してください。
    効率性分析では、総資産回転率、棚卸資産回転率などの指標を分析し、資産の運用効率を評価してください。
    キャッシュフロー計算書を分析し、資金繰りの状況を評価してください。

3. リスク:
    事業報告書に記載されているリスク要因を分析し、その重要度と影響度を評価してください。
    業界全体の動向や競合との競争環境などを考慮し、潜在的なリスクを特定してください。
    リスク管理体制の adequacy を評価し、改善点があれば指摘してください。

4. コーポレートガバナンス:
    コーポレートガバナンスの体制、取締役会の構成、独立役員の役割などを分析してください。
    株主との関係、情報開示の状況などを評価してください。
    企業倫理、コンプライアンスに関する取り組みを評価してください。

5. ESG:
    環境問題への取り組み、社会貢献活動、企業統治の状況を分析してください。
    ESGに関する情報開示の adequacy を評価してください。
    ESGの観点から、企業の持続可能性を評価してください。
    分析結果の出力形式:
    各観点ごとに章立てし、分析結果を明確に記述してください。
    図表やグラフなどを用いて、分析結果を視覚的に表現してください。
    具体的な根拠に基づいた客観的な分析を行い、結論を明確に示してください。
    必要に応じて、改善点や提言などを提示してください。
    その他:
    分析対象の有価証券報告書の発行企業、発行年を明記してください。
    最新の情報やデータを入手し、分析に活用してください。

6. 株価状況
    直近1年の株価の推移について、前述の分析結果を元に判定してください。
        """


class AgentWorkflowState(TypedDict):
    session_id: str
    message: str
    company_name: str
    report_company_name: str
    report_gcs_uri: str
    report_title: str
    response: str
    task_state: TaskState


class AgentResponse(TypedDict):
    session_id: str
    response: str
    task_state: TaskState


# TODO : 外部のデータベースにセッションを保存するように対応する
session_store: Dict[str, AgentWorkflowState] = {}
memory = MemorySaver()


# TODO : Host Agent（ReActとか）を使って、前段でよしなに解釈させてしまうのはありかも（ワークフローだとかえって面倒）
class AssetSecuritiesReportAgent:
    def __init__(self, config: AssetSecuritiesReportAgentConfig):
        self.config = config

        # LLM agentの作成
        vertexai.init(project=os.environ["GCP_PROJECT"], location=os.environ["GCP_LOCATION"])
        self.__model = GenerativeModel(model_name=config.llm_model_name)
        self.__config = config
        self.__generation_config = GenerationConfig(temperature=config.temperature, max_output_tokens=8192, top_p=0.95)
        self.__safety_settings = [
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=SafetySetting.HarmBlockThreshold.OFF,
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=SafetySetting.HarmBlockThreshold.OFF,
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=SafetySetting.HarmBlockThreshold.OFF,
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=SafetySetting.HarmBlockThreshold.OFF,
            ),
        ]
        self.__work_folder = os.path.join(os.path.dirname(__file__), "work")
        os.makedirs(self.__work_folder, exist_ok=True)

        # graphの生成
        self.__graph = self.get_workflow(memory_server=memory)

        # edinet wrapperの初期化
        self.__output_folder = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.__output_folder, exist_ok=True)
        self.__edinet_wrapper = EdinetWrapper(
            api_key=os.environ["EDINET_API_KEY"],
            output_folder=self.__output_folder
        )

    @staticmethod
    def get_supported_content_types() -> list:
        return ["text", "text/plain"]

    def invoke(self, query, sessionId) -> AgentResponse:
        message = query["message"]
        config = {
            "configurable": {"thread_id": sessionId}
        }
        try:
            self.__graph.invoke(
                {
                    "message": message,
                    "session_id": sessionId,
                },
                config
            )
            state = self.__graph.get_state(config)
        except Exception as e:
            # TODO : エラー用にstateを書き換える
            logger.error("Error invoking agent: %s", e)
            state = self.__graph.get_state(config)
            state.values["response"] = f"エラーが発生したため、処理が失敗しました"
            state.values["task_state"] = TaskState.FAILED

        # debug
        logger.info("invoke: sessionId: %s, state: %s", sessionId, state)
        res = state.values.get("response")
        logger.info("invoke: res = %s", res)

        response = AgentResponse(
            session_id=sessionId,
            response=state.values.get("response"),
            task_state=state.values.get("task_state")
        )
        return response

    async def stream(self, query, sessionId) -> AsyncIterable[Dict[str, Any]]:
        pass

    def get_workflow(self, memory_server) -> CompiledStateGraph:
        builder = StateGraph(AgentWorkflowState)
        # builder.set_entry_point(START)
        # builder.set_finish_point(END)
        builder.add_node("routing", self.__routing_node)
        builder.add_node("extract_company_name", self.__extract_company_name_node)
        builder.add_node("search_financial_report", self.__search_financial_report_node)
        builder.add_node("analyze_report", self.__analyze_report_node)
        builder.add_node("ask_human", self.__ask_human_node)
        builder.add_conditional_edges(START,
                                      self.__routing_node,
                                      {
                                          "ask_human": "ask_human",
                                          "analyze_report": "analyze_report",
                                          "extract_company_name": "extract_company_name"
                                      })
        builder.add_edge("extract_company_name", "search_financial_report")
        builder.add_edge("analyze_report", END)
        builder.add_edge("search_financial_report", END)
        builder.add_edge("ask_human", END)
        # TODO : analyze_reportの後に終了処理として、gcs_uriのリセットとかが必要かも？（要検討）
        return builder.compile(checkpointer=memory_server)

    def __routing_node(self, state: AgentWorkflowState) -> Literal["analyze_report", "extract_company_name", "ask_human"]:
        # セッションから過去のメッセージを取得
        session_id = state["session_id"]
        current_message = state["message"]
        conversation_history = []

        if session_id in session_store:
            previous_state = session_store[session_id]
            if "message" in previous_state:
                conversation_history.append(f"過去のメッセージ: {previous_state['message']}")

        conversation_history.append(f"現在のメッセージ: {current_message}")
        messages_text = "\n".join(conversation_history)

        # どの処理を行うか？をエージェントで選定
        prompt = f"""
あなたは下記の3つの手段をもっており、ユーザーからのメッセージに対して、どれを実行するか？を決定することが出来ます。
ルールに則って、メッセージから実行すべき手段を選定してください。

★手段
・有価証券報告書の分析（analyze_report）
・有価証券報告書の検索（extract_company_name）
・どの企業を分析したいかをユーザーに質問（ask_human）

★ルール
下記のどれかのみを出力するようにしてください。
※他のメッセージや内容は出力しないでください。

analyze_report
extract_company_name
ask_human

★会話履歴
{messages_text}
        """
        response = self.__model.generate_content(contents=[prompt])

        # ルールを使って、最終的なルーティングを実施
        node_name = response.text.strip()
        if session_id in session_store:
            state_of_history = session_store[session_id]
            finish_search = "report_gcs_uri" in state_of_history
        else:
            finish_search = False

        # debug
        logger.info("routing node name: %s", node_name)
        logger.info("routing finish_search: %s", finish_search)
        logger.info("routing session_store: %s", session_store)
        if "report_gcs_uri" in state:
            logger.info("gcs_uri: %s", state["report_gcs_uri"])

        if node_name == "analyze_report":
            if finish_search:
                # すでに取得済みの有価証券報告書がある場合は、分析処理を行う
                return "analyze_report"
            else:
                # まだ取得していない場合は、ユーザーに質問を行う
                return "extract_company_name"
        elif node_name == "ask_human":
            # ユーザーへの質問を実施
            return "ask_human"
        elif node_name == "extract_company_name":
            # 上記以外は、企業名の抽出を行い、レポート検索を行う
            return "extract_company_name"
        else:
            # それ以外の名前の場合は、例外として発火する
            raise ValueError(f"Invalid node name: {node_name}")

    def __extract_company_name_node(self, state: AgentWorkflowState) -> dict:
        # 企業名を抽出する処理
        company_name = self.__extract_company_name(query=state["message"])
        return {
            "company_name": company_name
        }

    def __search_financial_report_node(self, state: AgentWorkflowState) -> dict:
        # 有価証券報告書のuriをデータベースから検索する
        items = self.__search_financial_report_url_in_bq_table(state["company_name"])

        # もしドキュメントがない場合は、ドキュメントがない旨を通知
        # TODO : 現状はエラーとして通知ではなく、例外発火している（ちゃんとエラーハンドリングをする）
        if len(items) == 0:
            raise ValueError(f"no documents found for {state['company_name']}")

        # gcsにdocumentをアップロードする
        item = items[0]
        gcs_uri = self.__upload_financial_report_into_gcs(
            edinet_doc_id=item["doc_id"],
            current_time=datetime.now(),
            request_id=state["session_id"]
        )

        # TODO : LLMなどを使って、有価証券報告書を選定する
        res = {
            "report_company_name": item["filer_name"],
            "report_title": item["doc_description"],
            "report_gcs_uri": gcs_uri,
            "task_state": TaskState.INPUT_REQUIRED
        }
        res["response"] = f"この有価証券報告書のURIを分析対象として良いですか？ {item['filer_name']}"

        # sessionとして保存
        session_store[state["session_id"]] = {
            "session_id": state["session_id"],
            "message": state["message"],
            "company_name": state["company_name"],
            "report_company_name": res["report_company_name"],
            "report_title": res["report_title"],
            "report_gcs_uri": res["report_gcs_uri"],
            "task_state": TaskState.INPUT_REQUIRED
        }

        return res

    def __analyze_report_node(self, state: AgentWorkflowState) -> dict:
        # 有価証券報告書の分析を行う
        message = state["message"]
        gcs_uri = state["report_gcs_uri"]
        response = self.__analyze_financial_report(
            gcs_uri=gcs_uri,
            message=message,
            prompt=self.config.analyze_prompt,
            request_id=state["session_id"],
            timestamp=datetime.now()
        )
        return {
            "response": response,
            "task_state": TaskState.COMPLETED
        }

    def __ask_human_node(self, state: AgentWorkflowState) -> dict:
        # ユーザーへの質問を実施
        return {
            "response": "どの企業の分析をしたいかを教えてください。",
            "task_state": TaskState.INPUT_REQUIRED
        }

    def __extract_company_name(self, query: str) -> str:
        prompt = f"""
下記から企業名のみを抽出してください。ただし、ルールに沿って抽出をしてください。

★文章
{query}

★ルール
・企業名以外は出力しないでください。
・末尾に改行や空白をいれないでください。
・複数の企業名が抽出できた場合は、最初に抽出した企業名のみを出力してください。
        """
        response = self.__model.generate_content(contents=[prompt])
        company_name = response.text.rstrip().rstrip('\r\n')

        # TDDO : 企業名が正しく出力できるようにバリデーションやフォーマット指定を行いたい
        return company_name

    def __search_financial_report_url_in_bq_table(self, company_name: str) -> List[dict]:
        # 会社名から、bigqueryを検索し、有価証券報告書のリストを取得する
        client = bigquery.Client()
        items: List[dict] = []
        with open(os.path.join(os.path.dirname(__file__), "sql", "search_company.sql"), "r") as f:
            query = f.read().format(company_name=company_name)
            query_job = client.query(query)
            rows = query_job.result()
            for row in rows:
                doc_id = row["docID"]
                item = {
                    "doc_id": doc_id,
                    "filer_name": row["filerName"],
                    "doc_description": row["docDescription"],
                    "doc_url": f"{EdinetUtil.get_document_url_from_doc_id(doc_id=doc_id)}",
                }
                items.append(item)

        # 企業の件数が0件の場合は例外を発火
        if len(items) == 0:
            raise ValueError(f"no documents found for {company_name}")

        # TODO : 最新の有価証券報告書をとるように修正（LLMに判断させる？）
        return items

    def __analyze_financial_report(self,
                                   gcs_uri: str,
                                   message: str,  # TODO : messageを使うように修正が必要
                                   prompt: str,
                                   request_id: str,
                                   timestamp: datetime) -> str:
        # gcs uriからpdfデータを取得
        file_data = vertexai_part.from_uri(uri=gcs_uri, mime_type="application/pdf")

        # LLMを利用した解析処理を実施
        contents = [file_data, prompt]
        response = self.__model.generate_content(
            contents=contents,
            generation_config=self.__generation_config
        )

        # 解析結果含めて、ログとして出力
        # TODO : パラメーターにcompany_nameなども追加したい
        AgentUtil.upload_llm_log(
            work_folder=self.__work_folder,
            log_bucket_name=self.__config.log_bucket_name,
            log_base_folder=self.__config.log_base_folder,
            llm_model_name=self.__config.llm_model_name,
            temperature=self.__config.temperature,
            response=response,
            request_id=request_id,
            prompt=prompt,
            timestamp=timestamp,
            gcs_uri=gcs_uri
        )

        # 解析結果を返す
        return response.text

    def __upload_financial_report_into_gcs(self,
                                           edinet_doc_id: str,
                                           current_time: datetime,
                                           request_id: str) -> str:
        # doc_idからpdfレポートを取得。取得できない場合は例外が発火される
        file_path = self.__edinet_wrapper.download_pdf_of_financial_report(doc_id=edinet_doc_id)

        # 取得したpdfを、gcsにアップロードする
        file_name = os.path.basename(file_path)
        current_time_str = current_time.strftime("%Y%m%d%H%M%S")
        gcs_file_path = f"document/{current_time_str}/{request_id}/{file_name}"
        gcs_uri = upload_file_into_gcs(
            project_id=os.environ["GCP_PROJECT"],
            bucket_name=self.__config.log_bucket_name,
            remote_file_path=gcs_file_path,
            local_file_path=file_path,
        )

        return gcs_uri


class AgentUtil:
    # TODO : この処理はTaskManager側に実装した方が良いかも
    @staticmethod
    def upload_llm_log(
        work_folder: str,
        log_bucket_name: str,
        log_base_folder: str,
        llm_model_name: str,
        temperature: int,
        response: GenerationResponse | Iterable[GenerationResponse],
        request_id: str,
        prompt: str,
        timestamp: datetime,
        gcs_uri: str,
    ):
        # citation_metadataオブジェクトをリストに変換する
        def repeated_citations_to_list(citations: RepeatedComposite) -> list:
            citation_li = []
            for citation in citations:
                citation_dict = {}
                citation_dict["startIndex"] = citation.startIndex
                citation_dict["endIndex"] = citation.endIndex
                citation_dict["uri"] = citation.uri
                citation_dict["title"] = citation.title
                citation_dict["license"] = citation.license
                citation_dict["publicationDate"] = citation.publicationDate
                citation_li.append(citation_dict)
            return citation_li

        # safety_ratingsオブジェクトをリストに変換する
        def repeated_safety_ratings_to_list(safety_ratings: RepeatedComposite) -> list:
            safety_rating_li = []
            for safety_rating in safety_ratings:
                safety_rating_dict = {}
                safety_rating_dict["category"] = safety_rating.category.name
                safety_rating_dict["probability"] = safety_rating.probability.name
                safety_rating_li.append(safety_rating_dict)
            return safety_rating_li

        # llmのログをローカルに生成
        llm_log_data = {
            "input": {
                "input_datas": [],
                "prompt": prompt,
                "model_name": llm_model_name,
                "llm_config": {"temperature": temperature},
                "prompt_token_count": response._raw_response.usage_metadata.prompt_token_count,
                "gcs_uri": gcs_uri,
            },
            "output": {
                "text": response.candidates[0].text,
                "finish_reason": response.candidates[0].finish_reason.name,
                "finish_message": response.candidates[0].finish_message,
                "safety_ratings": repeated_safety_ratings_to_list(response.candidates[0].safety_ratings),
                "citation_metadata": repeated_citations_to_list(response.candidates[0].citation_metadata.citations),
                "candidates_token_count": response._raw_response.usage_metadata.candidates_token_count,
                "total_token_count": response._raw_response.usage_metadata.total_token_count,
            },
            "meta": {"timestamp": timestamp.strftime("%Y%m%d%H%M%S"), "request_id": request_id},
        }
        tmp_log_file = os.path.join(work_folder, "tmp_log.json")
        with open(tmp_log_file, "w") as f:
            json.dump(llm_log_data, f, ensure_ascii=False)

        # ログをGCSにアップロードする
        try:
            datetime_str = timestamp.strftime("%Y%m%d%H%M%S")
            upload_file_into_gcs(
                project_id=os.environ["GCP_PROJECT"],
                bucket_name=log_bucket_name,
                remote_file_path=f"{log_base_folder}/{datetime_str}/{request_id}/llm_log.json",
                local_file_path=tmp_log_file,
            )
        except Exception as e:
            logger.error(e)
            raise Exception(e)
        finally:
            os.remove(tmp_log_file)

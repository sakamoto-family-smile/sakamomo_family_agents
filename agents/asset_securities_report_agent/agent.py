from typing import Any, Dict, AsyncIterable
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
from proto.marshal.collections import RepeatedComposite
from logging import Logger, StreamHandler, getLogger
from common.types import (
    SendTaskRequest,
    TaskSendParams,
    Message,
    TaskStatus,
    Artifact,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    TextPart,
    Part,
    TaskState,
    Task,
    SendTaskResponse,
    InternalError,
    JSONRPCResponse,
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
)
from util.gcp_util import upload_file_into_gcs


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


class AssetSecuritiesReportAgentConfig(BaseModel):
    agent_name: str = "AssetSecuritiesReportAgent"
    agent_description: str = "This agent generates a report on asset securities."
    agent_type: str = "reporting"
    agent_version: str = "0.0.1"
    agent_author = "shota.sakamoto"
    agent_author_email: str = ""
    llm_model_name: str = "gemini-1.5-flash"
    temperature: int = 0
    log_bucket_name: str = "sakamomo_family_service"
    log_base_folder: str = "log"
    debug_mode: bool = False
    prompt: str = """
上記の決算資料から、後述する観点について分析を行い、下記の内容について回答してください。

## 回答して欲しい内容

・財務三表（損益計算書、貸借対照表、キャッシュフロー表）について、分析を行ってください。
・今後3ヵ年で企業の収益性は良くなっていくでしょうか？その理由も述べてください。
・直近1年で企業の株価は上昇していくでしょうか？その理由も述べてください。

## 分析時の観点

・貸借対照表、損益計算書、キャッシュフロー表が記載されている場合、各データについて、詳細な分析をすること
        """


class LLMAgentResponse(BaseModel):
    text: str
    metadata: dict


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

    def get_supported_content_types(self) -> list:
        return ["text", "text/plain"]

    def invoke(self, query, sessionId) -> str:
        input_data: dict = {
            "gcs_uri": query["gcs_uri"],
            "message": query["message"],
            "request_id": query["request_id"],
            "prompt": self.config.prompt
        }
        response = self.__get_llm_agent_response(input_data=input_data)
        return response.text

    async def stream(self, query, sessionId) -> AsyncIterable[Dict[str, Any]]:
        pass

    def __get_llm_agent_response(self, input_data: dict):
        # gcs uriからpdfデータを取得
        # TODO : 将来的に複数のデータタイプに対応させてもよさそう
        gcs_uri: str = input_data["gcs_uri"]
        message: str = input_data["message"]
        prompt: str = input_data["prompt"]
        request_id: str = input_data["request_id"]
        file_data = vertexai_part.from_uri(uri=gcs_uri, mime_type="application/pdf")

        # LLMを利用した解析処理を実施
        contents = [file_data, prompt]
        response = self.__model.generate_content(
            contents=contents,
            generation_config=self.__generation_config
        )

        # 解析結果含めて、ログとして出力
        AgentUtil.upload_llm_log(
            work_folder=self.__work_folder,
            log_bucket_name=self.__config.log_bucket_name,
            log_base_folder=self.__config.log_base_folder,
            llm_model_name=self.__config.llm_model_name,
            temperature=self.__config.temperature,
            response=response,
            request_id=request_id,
            prompt=prompt,
            timestamp=input_data["timestamp"],
            gcs_uri=gcs_uri
        )

        # 解析結果を返す
        return LLMAgentResponse(text=response.text, metadata={})


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

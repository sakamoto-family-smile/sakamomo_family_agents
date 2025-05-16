from typing import AsyncIterable, Union
import logging

from common.server import utils
from common.types import (
    Artifact,
    SendTaskRequest,
    SendTaskResponse,
    JSONRPCResponse,
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    TaskSendParams,
    TextPart,
    Task,
    TaskStatus,
    TaskState,
    Part
)
from common.server.task_manager import InMemoryTaskManager
from agent import AssetSecuritiesReportAgent


logger = logging.getLogger(__name__)


class AgentTaskManager(InMemoryTaskManager):
    def __init__(self, agent: AssetSecuritiesReportAgent):
        super().__init__()
        self.agent = agent
        # self.task_messages = {}

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        ## only support text output at the moment
        supported_content_types = self.agent.get_supported_content_types()
        if not utils.are_modalities_compatible(
            request.params.acceptedOutputModes,
            supported_content_types,
        ):
            logger.warning(
                "Unsupported output mode. Received %s, Support %s",
                request.params.acceptedOutputModes,
                supported_content_types,
            )
            return utils.new_incompatible_types_error(request.id)

        task_send_params: TaskSendParams = request.params
        await self.upsert_task(task_send_params)

        return await self._invoke(request)

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        pass

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        query = self.__convert_params_to_dict(task_send_params)

        # debug
        logger.info("sessionId: %s, query: %s", task_send_params.sessionId, query)

        try:
            result = self.agent.invoke(query, task_send_params.sessionId)
        except Exception as e:
            logger.error("Error invoking agent: %s", e)
            raise ValueError(f"Error invoking agent: {e}") from e

        # レスポンスは文字列で返ってくるため、TextPartとして格納する
        parts = [
            TextPart(
                text=result["response"],
            )
        ]
        logger.info(f"Final Result ===> {result}")
        task = await self.__update_store_task(
            task_send_params.id,
            TaskStatus(state=result["task_state"]),
            [Artifact(parts=parts)],
        )
        return SendTaskResponse(id=request.id, result=task)

    async def __update_store_task(
        self, task_id: str, status: TaskStatus, artifacts: list[Artifact]
    ) -> Task:
        # 内部に保存しているタスクをアップデートする
        # 処理結果を格納し直す
        async with self.lock:
            try:
                task = self.tasks[task_id]
            except KeyError as exc:
                logger.error("Task %s not found for updating the task", task_id)
                raise ValueError(f"Task {task_id} not found") from exc

        task.status = status

        # if status.message is not None:
        #     self.task_messages[task_id].append(status.message)

        if artifacts is not None:
            if task.artifacts is None:
                task.artifacts = []
                task.artifacts.extend(artifacts)

        return task

    def __convert_params_to_dict(self, task_send_params: TaskSendParams) -> dict:
        # TextPartのみ入力を許容。入力のクエリからテキスト情報を取得する。
        parts = task_send_params.message.parts
        message: str = TaskManagerUtil.get_part_text(parts[0])
        request_id: str = task_send_params.sessionId
        return {
            "message": message,
            "request_id": request_id
        }


class TaskManagerUtil:
    @staticmethod
    def get_part_text(part: Part) -> str:
        if isinstance(part, TextPart):
            return part.text
        else:
            raise ValueError("Only text parts are supported")

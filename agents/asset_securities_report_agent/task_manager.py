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
    FilePart,
    FileContent
)
from common.server.task_manager import InMemoryTaskManager
from .agent import AssetSecuritiesReportAgent


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
        query = self._get_user_query(task_send_params)
        try:
            result = self.agent.invoke(query, task_send_params.sessionId)
        except Exception as e:
            logger.error("Error invoking agent: %s", e)
            raise ValueError(f"Error invoking agent: {e}") from e

        data = self.agent.get_image_data(
            session_id=task_send_params.sessionId, image_key=result.raw
        )
        if not data.error:
            parts = [
                FilePart(
                    file=FileContent(
                        bytes=data.bytes, mimeType=data.mime_type, name=data.id
                    )
                )
            ]
        else:
            parts = [{"type": "text", "text": data.error}]

        print(f"Final Result ===> {result}")
        task = await self._update_store(
            task_send_params.id,
            TaskStatus(state=TaskState.COMPLETED),
            [Artifact(parts=parts)],
        )
        return SendTaskResponse(id=request.id, result=task)

    async def _update_store(
        self, task_id: str, status: TaskStatus, artifacts: list[Artifact]
    ) -> Task:
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

    def _get_user_query(self, task_send_params: TaskSendParams) -> str:
        part = task_send_params.message.parts[0]
        if not isinstance(part, TextPart):
            raise ValueError("Only text parts are supported")

        return part.text

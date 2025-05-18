from typing import Dict, Optional
from datetime import datetime
import uuid

class TaskManager:
    def __init__(self):
        self.tasks = {}

    def create_task(self, task_request: Dict) -> Dict:
        """新しいタスクを作成する"""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "request": task_request,
            "result": None,
            "error": None
        }
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Dict]:
        """タスクの状態を取得する"""
        return self.tasks.get(task_id)

    def update_task_status(self, task_id: str, status: str, result: Optional[Dict] = None,
                         error: Optional[str] = None) -> Dict:
        """タスクの状態を更新する"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        task["status"] = status
        task["updated_at"] = datetime.utcnow().isoformat()

        if result is not None:
            task["result"] = result
        if error is not None:
            task["error"] = error

        return task

    def list_tasks(self) -> Dict[str, Dict]:
        """全タスクのリストを返す"""
        return self.tasks

    def delete_task(self, task_id: str) -> bool:
        """タスクを削除する"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
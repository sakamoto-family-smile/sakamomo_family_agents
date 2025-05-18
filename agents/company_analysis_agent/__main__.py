import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict

from .agent import CompanyAnalysisAgent
from .task_manager import TaskManager

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
agent = CompanyAnalysisAgent()
task_manager = TaskManager()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """現在のユーザーを取得する"""
    return agent.verify_token(token)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """ユーザー認証とトークン発行"""
    return agent.authenticate_user(form_data.username, form_data.password)

@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    """新規ユーザー登録"""
    return agent.register_user(form_data.username, form_data.password)

@app.get("/agent-card")
async def get_agent_card():
    """エージェントカードを取得する"""
    return agent.get_agent_card()

@app.post("/tasks")
async def create_task(company_name: str, current_user: Dict = Depends(get_current_user)):
    """新しい企業分析タスクを作成する"""
    task_request = {
        "skill": "analyze_company",
        "parameters": {"company_name": company_name}
    }
    task = task_manager.create_task(task_request)

    try:
        # 企業分析を実行
        result = agent.analyze_company(company_name)
        task = task_manager.update_task_status(task["id"], "completed", result=result)
    except Exception as e:
        task = task_manager.update_task_status(task["id"], "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return task

@app.get("/tasks/{task_id}")
async def get_task(task_id: str, current_user: Dict = Depends(get_current_user)):
    """タスクの状態を取得する"""
    task = task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks")
async def list_tasks(current_user: Dict = Depends(get_current_user)):
    """全タスクのリストを取得する"""
    return task_manager.list_tasks()

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: Dict = Depends(get_current_user)):
    """タスクを削除する"""
    if not task_manager.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success"}

def main():
    """エージェントを起動する"""
    uvicorn.run("company_analysis_agent.__main__:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
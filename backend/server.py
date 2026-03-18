import os
import sys
from fastapi import WebSocket, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from backend.state import state

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []


class RunRequest(BaseModel):
    image_dir: str


@app.post("/run")
async def run_pipeline(req: RunRequest):
    """选择图片文件夹"""
    from backend.pipeline_runner import run_pipeline_workflow
    asyncio.create_task(run_pipeline_workflow(req.image_dir))

    return {"status": "started"}


@app.get("/dag_state")
def get_state():
    """获取节点状态"""
    return state


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    try:
        while True:
            await ws.send_json(state)
            await asyncio.sleep(0.5)
    except:
        clients.remove(ws)

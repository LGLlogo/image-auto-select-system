import json
import os
import sys

import requests
from fastapi import WebSocket, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from starlette.responses import StreamingResponse

from backend.WSManager import ws_manager
from backend.state import TaskManager

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
    task_id = TaskManager().create_task()
    loop = asyncio.get_running_loop()  # 主线程传入loop
    # 模拟请求远程
    local_image_dir = req.image_dir
    remote_image_dir = ''
    asyncio.create_task(asyncio.to_thread(run_pipeline_workflow, local_image_dir, remote_image_dir, task_id, loop))

    return {"status": "started", "task_id": task_id}


@app.get("/image")
def proxy_image(file_name: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    path = os.path.join(project_root, 'images', file_name)

    def iter_file():
        with open(path, "rb") as f:
            yield from f

    return StreamingResponse(iter_file(), media_type="image/jpg", headers={"Cache-Control": "no-store"})


@app.get("/thumb")
def proxy_thumb(file_name: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    path = os.path.join(project_root, 'thumb', file_name)

    def iter_file():
        with open(path, "rb") as f:
            yield from f

    return StreamingResponse(iter_file(), media_type="image/jpg", headers={"Cache-Control": "no-store"})


@app.get("/dag_state")
def get_state(task_id):
    """获取节点状态"""
    return TaskManager.get_state(task_id)


@app.websocket("/ws/{task_id}")
async def websocket_endpoint(ws: WebSocket, task_id: str):
    await ws_manager.connect(task_id, ws)

    try:
        while True:
            # 接收客户端发送的消息
            # await ws.receive_text()  # 保持连接
            await ws.receive_text()  # 保持连接
            if task_id is not None:
                print(f"📥 收到消息: {task_id}")
            await asyncio.sleep(1.5)
            # print("after send")
    except Exception as e:
        ws_manager.disconnect(task_id, ws)
        raise e

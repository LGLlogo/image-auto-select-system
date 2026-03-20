import asyncio
import os.path

import uvicorn

from backend.logger import TaskLogger
from backend.pipeline_runner import build_dag
from backend.state import TaskManager
from pipeline.core.dag import DAG
from pipeline.core.executor import DAGExecutor
from pipeline.core.context import WorkflowContext
from pipeline.nodes.file_storge import FileStorgeNode


# def main():
#     task_id = TaskManager().create_task()
#     ctx = WorkflowContext()
#     dag = DAG()
#     # 设置日志系统
#     # def emit(data):
#     #     asyncio.run_coroutine_threadsafe(
#     #         ws_manager.broadcast(task_id, data),
#     #         loop
#     #     )
#     logger = TaskLogger(task_id, None)
#     ctx.set("task_id", task_id)
#     ctx.set("logger", logger)
#     dag.add_node(FileStorgeNode(), task_id)
#     path = "C:\\Users\\looge\\Desktop\\images\\1030_final"
#     ctx.set("selected_images", [os.path.join(path, "IMG_8588.JPG"), os.path.join(path, "IMG_8590.JPG")])
#     executor = DAGExecutor(dag, max_workers=4)
#     executor.run(ctx)


# if __name__ == "__main__":
#     main()


if __name__ == "__main__":
    uvicorn.run("backend.server:app", host="localhost", port=8000, reload=True)

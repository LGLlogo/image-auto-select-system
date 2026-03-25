import argparse
import asyncio
import os.path

import requests
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

def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='商业图库智能选取系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py                    # 正常运行
  python main.py --symbol GLD       # 指定分析图片目录
        ''')

    parser.add_argument(
        '--folder',
        type=str,
        help='指定分析图片目录'
    )

    return parser.parse_args()


# if __name__ == "__main__":
#     # 直接调用
#     from backend.pipeline_runner import run_pipeline_workflow
#
#     args = parse_arguments()
#     task_id = TaskManager().create_task()
#     if args.folder:
#         # 远程
#         run_pipeline_workflow("", args.folder, task_id, None)
#     else:
#         # 本地
#         run_pipeline_workflow("C:\\Users\\looge\\Desktop\\images\\1031", "", task_id, None)

if __name__ == "__main__":
    # fastapi 服务
    uvicorn.run("backend.server:app", host="localhost", port=8000, reload=True)

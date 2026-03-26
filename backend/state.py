import time
import uuid
from typing import Dict, Optional, Any

from pipeline.core.context import WorkflowContext


class TaskManager:
    """任务调度器 单例模式"""
    _instance = None
    _states: Dict[str, 'TaskManager.State'] = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def create_task(cls) -> str:
        """创建新任务并返回任务ID"""
        task_id = str(uuid.uuid4())
        cls._states[task_id] = cls.State(task_id)
        return task_id

    @classmethod
    def remove_task(cls, task_id: str) -> bool:
        """移除任务"""
        if task_id in cls._states:
            del cls._states[task_id]
            return True
        return False

    @staticmethod
    def get_state(task_id: str) -> Optional['TaskManager.State']:
        """根据任务ID获取状态对象"""
        return TaskManager._states.get(task_id)

    #  State 状态类
    class State:
        def __init__(self, task_id):
            self.task_id = task_id
            self.nodes = {}
            self.results = []
            self.dag = {
                "nodes": [],
                "edges": []
            }

        def add_node(self, node_id: str, data: Dict[str, Any]) -> None:
            """添加节点"""
            self.nodes[node_id] = data

        def add_result(self, results: Dict[str, Any]) -> None:
            """添加结果"""
            self.results = results

        def add_dag(self, dag_type: str, dag_json: Dict[str, Any]) -> None:
            """添加结果"""
            self.dag[dag_type].append(dag_json)

        def __str__(self) -> str:
            return f"State(task_id={self.task_id}, nodes={len(self.nodes)})"


def update_node(node_id: str, status: str, ctx: WorkflowContext):
    """节点状态更新"""
    task_id = ctx.get("task_id")
    _state = TaskManager.get_state(task_id)
    data = {
        "status": status,
        "image_count": len(ctx.get("files", [])),
        # 返回前 dict转list
        "scores": [{"path": f, **v} for f, v in ctx.get("scores", {}).items()],
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    }
    _state.add_node(node_id, data)
    return _state


def add_dag(dag_type, dag_json, task_id):
    """添加dag"""
    _state = TaskManager.get_state(task_id)
    _state.add_dag(dag_type, dag_json)


def update_results(results, task_id):
    """日志记录"""
    _state = TaskManager.get_state(task_id)
    """更新最终选片"""
    _state.add_result(results)

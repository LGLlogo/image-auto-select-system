import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.state import TaskManager, update_node, add_log


class DAGExecutor:

    def __init__(self, dag, max_workers=4, on_update=None):
        """
        dag: {
            "nodes": {id: node},
            "edges": [(u, v)]
        }
        """
        self.nodes = dag.nodes
        self.graph = dag.edges
        self.in_degree = dag.in_degree
        self.max_workers = max_workers
        self.on_update = on_update
        self.lock = threading.Lock()

    def run(self, ctx):

        # 初始可执行节点
        ready = deque([n for n in self.nodes if self.in_degree[n] == 0])

        executor = ThreadPoolExecutor(max_workers=self.max_workers)

        futures = {}
        running = set()

        while ready or futures:

            # 🚀 提交任务
            while ready and len(running) < self.max_workers:
                node_id = ready.popleft()

                future = executor.submit(self._run_node, node_id, ctx)

                futures[future] = node_id
                running.add(node_id)

            # ⏳ 等待完成
            done, _ = as_completed(futures), None

            for future in list(futures):

                if future.done():

                    node_id, success = future.result()

                    running.remove(node_id)
                    futures.pop(future)

                    if not success:
                        executor.shutdown(wait=False)
                        raise RuntimeError(f"Node {node_id} failed")

                    # 🔓 解锁下游
                    for nxt in self.graph[node_id]:
                        self.in_degree[nxt] -= 1
                        if self.in_degree[nxt] == 0:
                            ready.append(nxt)

                    break  # ⚠️ 每轮只处理一个完成任务（避免锁复杂）

        executor.shutdown()

    def _run_node(self, node_id, ctx):
        """执行单节点"""
        node = self.nodes[node_id]
        start = time.time()
        try:
            update_node(node_id, "running", ctx)
            add_log(f"{node_id} started", ctx.get("task_id"))
            _state = TaskManager.get_state(ctx.get("task_id"))

            self._emit({
                "type": "node_update",
                **_state.__dict__
            })

            result = node.execute(ctx)  # ✅ 同步执行

            cost = round(time.time() - start, 2)
            update_node(node_id, "done", ctx)
            add_log(f"{node_id} done in ({cost}s)", ctx.get("task_id"))
            _state = TaskManager.get_state(ctx.get("task_id"))

            self._emit({
                "type": "node_done",
                **_state.__dict__
            })

            return node_id, True

        except Exception as e:
            cost = round(time.time() - start, 2)
            update_node(node_id, "fail", ctx)
            add_log(f"{node_id} failed {e}", ctx.get("task_id"))
            _state = TaskManager.get_state(ctx.get("task_id"))
            self._emit({
                "type": "node_error",
                **_state.__dict__
            })

            return node_id, False

    def _emit(self, data):
        """发送事件(线程安全)"""
        if self.on_update:
            self.on_update(data)

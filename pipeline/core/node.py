# Node 抽象类
import time
from backend.state import update_node, add_log


class Node:
    name = 'node'

    def run(self, ctx):
        raise NotImplementedError

    def execute(self, ctx):
        """
        统一执行入口
        """
        start = time.time()
        try:
            print(f"[NODE START] {self.name}")
            update_node(self.name, "running", ctx)
            add_log(f"{self.name} started")
            result = self.run(ctx)
            cost = round(time.time() - start, 2)
            update_node(self.name, "done", ctx)
            add_log(f"{self.name} done in ({cost}s)")
            print(f"[NODE SUCCESS] {self.name} ({cost}s)")
            return result

        except Exception as e:
            cost = round(time.time() - start, 2)
            update_node(self.name, "fail", ctx)
            add_log(f"{self.name} failed {e}")
            print(f"[NODE ERROR] {self.name} ({cost}s): {e}")
            raise Exception(f"Node {self.name} failed") from e

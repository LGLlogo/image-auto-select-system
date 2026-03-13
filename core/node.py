# Node 抽象类
import time


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
            result = self.run(ctx)
            cost = round(time.time() - start, 2)
            print(f"[NODE SUCCESS] {self.name} ({cost}s)")
            return result

        except Exception as e:
            cost = round(time.time() - start, 2)
            print(f"[NODE ERROR] {self.name} ({cost}s): {e}")
            raise Exception(f"Node {self.name} failed") from e

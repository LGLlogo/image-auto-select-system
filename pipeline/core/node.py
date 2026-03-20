# Node 抽象类
import logging
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
            self.log(ctx, f"[NODE START] {self.name}")
            result = self.run(ctx)
            cost = round(time.time() - start, 2)
            self.log(ctx, f"[NODE SUCCESS] {self.name}  in ({cost}s)")
            return result

        except Exception as e:
            cost = round(time.time() - start, 2)
            self.log(ctx, f"[NODE ERROR] : {e}", logging.ERROR)
            raise Exception(f"Node {self.name} failed") from e

    def log(self, ctx, msg, level=logging.INFO):
        """node日志打印封装"""
        logger = ctx.get("logger")
        logger.log(node=self.name, message=msg, level=level)

    def info(self, ctx, msg):
        self.log(ctx, msg, level=logging.INFO)

    def error(self, ctx, msg):
        self.log(ctx, msg, level=logging.ERROR)

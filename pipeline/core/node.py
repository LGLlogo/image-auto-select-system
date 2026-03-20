# Node 抽象类

class Node:
    name = 'node'

    def run(self, ctx):
        raise NotImplementedError

    def execute(self, ctx):
        """
        统一执行入口
        """
        try:
            print(f"[NODE START] {self.name}")
            result = self.run(ctx)
            print(f"[NODE SUCCESS] {self.name}")
            return result

        except Exception as e:
            print(f"[NODE ERROR] {self.name} : {e}")
            raise Exception(f"Node {self.name} failed") from e

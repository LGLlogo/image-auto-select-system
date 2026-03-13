# Workflow 执行器
class Workflow:

    def __init__(self):
        self.nodes = []

    def add(self, node):
        self.nodes.append(node)

    def run(self, ctx):
        for node in self.nodes:
            print(f"Running node: {node.__class__.__name__}")
            node.run(ctx)

        return ctx

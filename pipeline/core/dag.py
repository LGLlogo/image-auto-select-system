from collections import defaultdict
from backend.state import add_dag


class DAG:

    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(list)
        self.in_degree = defaultdict(int)

    def add_node(self, node, task_id):
        self.nodes[node.name] = node
        add_dag("nodes", {"id": node.name, "label": node.name}, task_id)

    def add_edge(self, upstream, downstream, task_id):
        self.edges[upstream].append(downstream)
        self.in_degree[downstream] += 1
        add_dag("edges", {"source": upstream, "target": downstream}, task_id)

    def get_roots(self):
        roots = []
        for name in self.nodes:
            if self.in_degree[name] == 0:
                roots.append(name)

        return roots

from collections import defaultdict


class DAG:

    def __init__(self):
        self.nodes = {}
        self.edges = defaultdict(list)
        self.in_degree = defaultdict(int)

    def add_node(self, node):
        self.nodes[node.name] = node

    def add_edge(self, upstream, downstream):
        self.edges[upstream].append(downstream)
        self.in_degree[downstream] += 1

    def get_roots(self):
        roots = []
        for name in self.nodes:
            if self.in_degree[name] == 0:
                roots.append(name)

        return roots

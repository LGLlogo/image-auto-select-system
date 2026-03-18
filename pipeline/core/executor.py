from concurrent.futures import ThreadPoolExecutor, as_completed


class DAGExecutor:

    def __init__(self, dag, max_workers=4):
        self.dag = dag
        self.max_workers = max_workers

    def run(self, ctx):
        completed = set()
        submitted = set()
        executor = ThreadPoolExecutor(max_workers=self.max_workers)
        futures = {}

        while len(completed) < len(self.dag.nodes):
            ready_nodes = []
            for name, node in self.dag.nodes.items():
                if name in completed or name in submitted:
                    continue

                if all(dep in completed for dep in self.get_upstreams(name)):
                    ready_nodes.append(name)

            for node_name in ready_nodes:
                node = self.dag.nodes[node_name]
                futures[executor.submit(node.execute, ctx)] = node_name
                submitted.add(node_name)

            for future in as_completed(futures):
                node_name = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"[DAG FAILED] node={node_name}")
                    executor.shutdown(wait=False)
                    raise e
                print(f"[DAG FINISHED] {node_name}")
                completed.add(node_name)
                del futures[future]
                break

    def get_upstreams(self, node):
        upstreams = []
        for u, downs in self.dag.edges.items():
            if node in downs:
                upstreams.append(u)
        return upstreams

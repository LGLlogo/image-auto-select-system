import time

state = {
    "nodes": {},
    "logs": [],
    "results": [],
    "dag": {
        "nodes": [],
        "edges": []
    }
}


def update_node(node, status, ctx):
    """节点状态更新"""
    state["nodes"][node] = {
        "status": status,
        "image_count": len(ctx.get("files", [])),
        "scores": ctx.get("scores", {}),
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    }


def add_log(msg):
    """日志记录"""
    state["logs"].append({
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
        "msg": msg
    })


def add_dag(dag_type, dag_json):
    """添加dag"""
    state["dag"][dag_type].append(dag_json)


def update_results(results):
    """更新最终选片"""
    state["results"] = results

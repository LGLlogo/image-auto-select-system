from core.dag import DAG
from core.executor import DAGExecutor
from core.workflow import Workflow
from core.context import WorkflowContext
from nodes.aesthetic_score import AestheticScoreNode
from nodes.deduplicate import DeduplicateNode

from nodes.load_images import LoadImagesNode
from nodes.quality_filter import QualityFilterNode
from nodes.clip import CLIPEmbeddingNode
from nodes.gpt_scoring import GPTScoringNode
from nodes.portfolio_optimizer import SelectTopNode


def build_dag():

    dag = DAG()
    dag.add_node(LoadImagesNode("images"))
    dag.add_node(QualityFilterNode())
    dag.add_node(CLIPEmbeddingNode())
    dag.add_node(DeduplicateNode())
    dag.add_node(AestheticScoreNode())
    dag.add_node(GPTScoringNode(batch_size=3, max_workers=3))
    dag.add_node(SelectTopNode())

    dag.add_edge("load_images", "quality_filter")
    dag.add_edge("quality_filter", "clip_embedding")
    dag.add_edge("clip_embedding", "deduplicate")
    dag.add_edge("deduplicate", "aesthetic_score")
    dag.add_edge("aesthetic_score", "gpt_score")
    dag.add_edge("gpt_score", "select_top")

    return dag


def main():
    ctx = WorkflowContext()
    dag = build_dag()
    executor = DAGExecutor(dag, max_workers=4)
    executor.run(ctx)


if __name__ == "__main__":
    main()

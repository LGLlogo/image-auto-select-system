import torch
from core.dag import DAG
from core.executor import DAGExecutor
from core.context import WorkflowContext
from nodes.aesthetic_score import AestheticScoreNode
from nodes.deduplicate import DeduplicateNode

from nodes.load_images import LoadImagesNode
from nodes.quality_filter import QualityFilterNode
from nodes.clip_embedding import CLIPEmbeddingNode
from nodes.gpt_scoring import GPTScoringNode
from nodes.portfolio_optimizer import PortfolioOptimizerNode
from nodes.score_fusion import ScoreFusionNode
from nodes.select_top import SelectTopNode
from nodes.vision_score_node import VisionScoreNode

device = "cuda" if torch.cuda.is_available() else "cpu"


def build_dag():
    dag = DAG()
    dag.add_node(LoadImagesNode("images"))
    dag.add_node(QualityFilterNode())
    dag.add_node(CLIPEmbeddingNode())
    dag.add_node(DeduplicateNode())
    dag.add_node(AestheticScoreNode())
    # dag.add_node(GPTScoringNode(batch_size=3, max_workers=3))
    dag.add_node(VisionScoreNode())
    dag.add_node(ScoreFusionNode())
    dag.add_node(
        PortfolioOptimizerNode(
            top_k=10,
            cluster_k=12,
            cluster_top_n=3,
            lambda_penalty=0.7,
            device=device
        )
    )
    # dag.add_node(SelectTopNode())

    dag.add_edge("load_images", "quality_filter")
    dag.add_edge("quality_filter", "clip_embedding")
    dag.add_edge("clip_embedding", "deduplicate")
    dag.add_edge("deduplicate", "aesthetic_score")
    dag.add_edge("aesthetic_score", "vision_scoring")
    dag.add_edge("vision_scoring", "score_fusion")
    dag.add_edge("score_fusion", "portfolio_optimizer")
    # dag.add_edge("portfolio_optimizer", "select_top")

    return dag


def main():
    ctx = WorkflowContext()
    dag = build_dag()
    executor = DAGExecutor(dag, max_workers=4)
    executor.run(ctx)


if __name__ == "__main__":
    main()

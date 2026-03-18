import os
import torch
from pipeline.core.dag import DAG
from pipeline.core.context import WorkflowContext
from pipeline.core.executor import DAGExecutor
from pipeline.nodes.aesthetic_score import AestheticScoreNode
from pipeline.nodes.content_safety_filter import ContentSafetyFilterNode
from pipeline.nodes.deduplicate import DeduplicateNode

from pipeline.nodes.load_images import LoadImagesNode
from pipeline.nodes.quality_filter import QualityFilterNode
from pipeline.nodes.clip_embedding import CLIPEmbeddingNode
from pipeline.nodes.portfolio_optimizer import PortfolioOptimizerNode
from pipeline.nodes.score_fusion import ScoreFusionNode
from pipeline.nodes.vision_score_node_v3 import VisionScoreNodeV3

device = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_num_threads(os.cpu_count())


def build_dag(image_dir):
    dag = DAG()
    num_workers = os.cpu_count()
    dag.add_node(LoadImagesNode(image_dir=image_dir))
    dag.add_node(ContentSafetyFilterNode(num_workers=num_workers,
                                         device=device))
    dag.add_node(QualityFilterNode(num_workers=num_workers))
    dag.add_node(CLIPEmbeddingNode(num_workers=num_workers,
                                   device=device))
    dag.add_node(DeduplicateNode())
    dag.add_node(AestheticScoreNode())
    # dag.add_node(GPTScoringNode(batch_size=3, max_workers=3))
    dag.add_node(VisionScoreNodeV3(num_workers=num_workers))
    dag.add_node(ScoreFusionNode())
    dag.add_node(
        PortfolioOptimizerNode(
            top_k=20,
            cluster_k=12,
            cluster_top_n=3,
            lambda_penalty=0.7,
            device=device
        )
    )
    # dag.add_node(SelectTopNode())

    dag.add_edge("load_images", "content_safety_filter")
    dag.add_edge("content_safety_filter", "quality_filter")
    dag.add_edge("quality_filter", "clip_embedding")
    dag.add_edge("clip_embedding", "deduplicate")
    dag.add_edge("deduplicate", "aesthetic_score")
    dag.add_edge("aesthetic_score", "vision_score")
    dag.add_edge("vision_score", "score_fusion")
    dag.add_edge("score_fusion", "portfolio_optimizer")
    # dag.add_edge("portfolio_optimizer", "select_top")

    return dag


async def run_pipeline_workflow(image_dir: str):
    ctx = WorkflowContext()
    dag = build_dag(image_dir)
    executor = DAGExecutor(dag, max_workers=2)
    executor.run(ctx)

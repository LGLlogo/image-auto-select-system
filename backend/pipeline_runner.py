import asyncio
import os
import torch

from backend.WSManager import ws_manager
from backend.logger import TaskLogger
from backend.state import TaskManager
from pipeline.core.dag import DAG
from pipeline.core.context import WorkflowContext
from pipeline.core.executor import DAGExecutor
from pipeline.nodes.aesthetic_score import AestheticScoreNode
from pipeline.nodes.content_safety_filter import ContentSafetyFilterNode
from pipeline.nodes.deduplicate import DeduplicateNode
from pipeline.nodes.download_images import DownloadImagesNode
from pipeline.nodes.file_storge import FileStorgeNode

from pipeline.nodes.load_images import LoadImagesNode
from pipeline.nodes.load_images_zip import LoadImagesZipNode
from pipeline.nodes.quality_filter import QualityFilterNode
from pipeline.nodes.clip_embedding import CLIPEmbeddingNode
from pipeline.nodes.portfolio_optimizer import PortfolioOptimizerNode
from pipeline.nodes.score_fusion import ScoreFusionNode
from pipeline.nodes.vision_score_node_v3 import VisionScoreNodeV3

device = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_num_threads(os.cpu_count())


def build_dag(image_dir, remote_image_dir, task_id):
    dag = DAG()
    num_workers = os.cpu_count()
    if remote_image_dir:
        dag.add_node(DownloadImagesNode(folder_name=remote_image_dir,
                                        input_image_dir='input_images'), task_id)

    dag.add_node(LoadImagesZipNode(image_zip_path=image_dir), task_id)
    # dag.add_node(LoadImagesNode(image_dir=image_dir), task_id)

    dag.add_node(ContentSafetyFilterNode(num_workers=num_workers,
                                         device=device), task_id)
    dag.add_node(QualityFilterNode(num_workers=num_workers), task_id)
    dag.add_node(CLIPEmbeddingNode(num_workers=num_workers,
                                   device=device), task_id)
    dag.add_node(DeduplicateNode(), task_id)
    dag.add_node(AestheticScoreNode(), task_id)
    # dag.add_node(GPTScoringNode(batch_size=3, max_workers=3))
    dag.add_node(VisionScoreNodeV3(num_workers=num_workers), task_id)
    dag.add_node(ScoreFusionNode(), task_id)
    dag.add_node(
        PortfolioOptimizerNode(
            top_k=20,
            cluster_k=12,
            cluster_top_n=3,
            lambda_penalty=0.7,
            device=device
        ), task_id)
    dag.add_node(FileStorgeNode(), task_id)

    if remote_image_dir:
        dag.add_edge("download_images", "load_images", task_id)

    dag.add_edge("load_images", "content_safety_filter", task_id)
    dag.add_edge("content_safety_filter", "quality_filter", task_id)
    dag.add_edge("quality_filter", "clip_embedding", task_id)
    dag.add_edge("clip_embedding", "deduplicate", task_id)
    dag.add_edge("deduplicate", "aesthetic_score", task_id)
    dag.add_edge("deduplicate", "vision_score", task_id)
    dag.add_edge("aesthetic_score", "score_fusion", task_id)
    dag.add_edge("vision_score", "score_fusion", task_id)
    dag.add_edge("score_fusion", "portfolio_optimizer", task_id)
    dag.add_edge("portfolio_optimizer", "file_storge", task_id)

    return dag


def run_pipeline_workflow(local_image_dir: str, remote_image_dir: str, task_id: str, loop):
    ctx = WorkflowContext()
    ctx.set("task_id", task_id)

    def on_update(data):
        if loop:
            asyncio.run_coroutine_threadsafe(
                ws_manager.broadcast(task_id, data),
                loop
            )

    # 设置日志系统
    logger = TaskLogger(task_id, emitter=on_update)
    ctx.set("logger", logger)

    dag = build_dag(local_image_dir, remote_image_dir, task_id)
    executor = DAGExecutor(dag,
                           max_workers=2,
                           on_update=on_update)
    # await asyncio.to_thread(executor.run, ctx)
    executor.run(ctx)
    return task_id

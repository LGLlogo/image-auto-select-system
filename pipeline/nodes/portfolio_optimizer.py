import os.path

import torch
import numpy as np
from sklearn.cluster import KMeans

from backend.state import update_results
from pipeline.core.node import Node


class PortfolioOptimizerNode(Node):
    name = "portfolio_optimizer"

    def __init__(
            self,
            top_k=10,  # MMR 从 cluster_k × cluster_top_n 张选 top_k 张
            cluster_k=12,  # 聚类 cluster_k 类
            cluster_top_n=3,  # 每类选 cluster_top_n 张 候选池:cluster_k × cluster_top_n 张
            lambda_penalty=0.7,
            device="cpu",
    ):

        self.top_k = top_k
        self.cluster_k = cluster_k
        self.cluster_top_n = cluster_top_n
        self.lambda_penalty = lambda_penalty
        self.device = device

    def run(self, ctx):

        files = ctx.get("files")
        embeddings = ctx.get("embeddings")
        scores = ctx.get("scores")

        emb_matrix = np.asarray(embeddings)
        N = emb_matrix.shape[0]

        if len(files) != N:
            raise ValueError("images 与 embeddings 数量不一致")

        # ---------- score vector ----------
        score_vec = np.array([
            scores[f]["total_score"] for f in files
        ])

        # ---------- CLIP clustering ----------
        cluster_k = min(self.cluster_k, N)

        kmeans = KMeans(
            n_clusters=cluster_k,
            random_state=42,
            n_init=10
        )

        labels = kmeans.fit_predict(emb_matrix)

        clusters = {}

        for idx, label in enumerate(labels):
            clusters.setdefault(label, []).append(idx)

        # ---------- 每个 cluster 选 topN ----------
        candidate_idx = []
        for cluster_indices in clusters.values():
            cluster_scores = [
                (i, score_vec[i]) for i in cluster_indices
            ]
            cluster_scores.sort(key=lambda x: x[1], reverse=True)
            top_items = [
                i for i, _ in cluster_scores[: self.cluster_top_n]
            ]

            candidate_idx.extend(top_items)

        candidate_idx = list(set(candidate_idx))

        # ---------- candidate embeddings ----------
        cand_emb = emb_matrix[candidate_idx]
        cand_scores = score_vec[candidate_idx]

        # ---------- normalize ----------
        cand_emb = torch.tensor(cand_emb, dtype=torch.float32).to(self.device)
        cand_emb = torch.nn.functional.normalize(cand_emb, dim=1)
        cand_scores = torch.tensor(
            cand_scores,
            dtype=torch.float32
        ).to(self.device)

        # similarity matrix
        sim_matrix = cand_emb @ cand_emb.T
        # ---------- MMR ----------
        selected = []

        first = torch.argmax(cand_scores).item()
        selected.append(first)

        candidates = set(range(len(candidate_idx)))
        candidates.remove(first)

        while len(selected) < self.top_k and candidates:

            best_idx = None
            best_score = -1e9

            for c in candidates:

                relevance = cand_scores[c]

                sim_to_selected = sim_matrix[c, selected]

                max_sim = torch.max(sim_to_selected)

                mmr = (
                    self.lambda_penalty * relevance
                    - (1 - self.lambda_penalty) * max_sim
                )

                if mmr > best_score:
                    best_score = mmr
                    best_idx = c

            selected.append(best_idx)
            candidates.remove(best_idx)

        # ---------- map back ----------
        final_idx = [candidate_idx[i] for i in selected]

        selected_files = [files[i] for i in final_idx]

        ctx.set("selected_images", selected_files)
        # state更新选片结果
        update_results([{"file": os.path.basename(f), **scores[f]} for f in selected_files], ctx.get("task_id"))

        for f in selected_files:
            super().log(ctx, f"{scores[f]['total_score']}, {f}")

        super().log(ctx,f"PortfolioOptimizer finished: {len(selected_files)} images")

import torch
from core.node import Node


# 相似度惩罚
class DiversitySelectionNode(Node):
    name = "diversity_selection"

    def __init__(self, top_k=10, lambda_penalty=0.7, device="cpu"):

        self.top_k = top_k
        self.lambda_penalty = lambda_penalty
        self.device = device

    def run(self, ctx):

        scores = ctx.get("scores")
        embeddings = ctx.get("embeddings")

        files = list(scores.keys())

        # score vector
        score_vec = torch.tensor(
            [scores[f]["total_score"] for f in files],
            dtype=torch.float32
        ).to(self.device)

        # embedding matrix
        emb_matrix = torch.tensor(
            [embeddings[f] for f in files],
            dtype=torch.float32
        ).to(self.device)

        # normalize embedding
        emb_matrix = torch.nn.functional.normalize(
            emb_matrix, dim=1
        )

        # cosine similarity matrix
        sim_matrix = emb_matrix @ emb_matrix.T

        selected = []

        # first image: highest score
        first = torch.argmax(score_vec).item()
        selected.append(first)

        candidates = set(range(len(files)))
        candidates.remove(first)

        while len(selected) < self.top_k and candidates:

            best_idx = None
            best_score = -1e9

            for c in candidates:
                relevance = score_vec[c]
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

        selected_files = [files[i] for i in selected]

        ctx.set("selected_images", selected_files)

        print(f"DiversitySelection v2 finished: {len(selected_files)} images")

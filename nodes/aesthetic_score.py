import numpy as np
from core.node import Node
import torch
from models.aesthetic_model import load_aesthetic_model


class AestheticScoreNode(Node):
    name = "aesthetic_score"

    def __init__(self):
        self.model = load_aesthetic_model()

    def aesthetic_score_batch(self, embeddings):
        emb = torch.tensor(embeddings).float()

        with torch.no_grad():
            scores = self.model(emb).squeeze()

        return scores.numpy()

    def run(self, ctx):
        embeddings = ctx.get("embeddings")
        aesthetic_scores = self.aesthetic_score_batch(embeddings)
        scores = ctx.get("scores").copy()
        files = ctx.get("files")
        aesthetic_scores_json = {}
        for path, score in zip(files, aesthetic_scores):
            scores[path] = {
                **scores[path],
                'aesthetic_score': score
            }
            aesthetic_scores_json[path] = score

        ctx.set("aesthetic_scores", aesthetic_scores_json)
        ctx.set("scores", scores)

        print("Aesthetic scoring finished")

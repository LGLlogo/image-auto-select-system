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
        scores = {}
        images = ctx.get("images")
        for path, score in zip(images, aesthetic_scores):
            scores[path] = score

        ctx.set("aesthetic_scores", scores)
        print("Aesthetic scoring finished")

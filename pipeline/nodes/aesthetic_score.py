from pipeline.core.node import Node
import torch
from pipeline.models.aesthetic_model import load_aesthetic_model


class AestheticScoreNode(Node):

    def __init__(self, batch_size=32):
        super().__init__(name="aesthetic_score")
        self.model = load_aesthetic_model()
        self.batch_size = batch_size

    def aesthetic_score_batch(self, embeddings):
        total = len(embeddings)
        results = []
        processed = 0
        for i in range(0, total, self.batch_size):
            batch = embeddings[i:i + self.batch_size]
            mid = i + len(batch) * 0.5
            end = i + len(batch)
            self._emit(
                self.progress.callback(mid, total)
            )
            emb = torch.tensor(batch).float()
            with torch.no_grad():
                scores = self.model(emb).squeeze()

            scores = scores.cpu().numpy()
            results.extend(scores)
            self._emit(
                self.progress.callback(end, total)
            )

        return results

    def run(self, ctx):
        records = ctx.get("records")
        embeddings = [record.clip for record in records]
        aesthetic_scores = self.aesthetic_score_batch(embeddings)
        files = [record.name for record in records]
        super().log(ctx, f"Aesthetic scoring start: {len(files)} | {len(aesthetic_scores)}")
        aesthetic_scores_json = ctx.setdefault("aesthetic_scores", {})
        for name, score in zip(files, aesthetic_scores):
            # scores[path] = {
            #     **scores[path],
            #     'aesthetic_score': float(score)
            # }
            aesthetic_scores_json[name] = float(score)

        ctx.set("aesthetic_scores", aesthetic_scores_json)
        # ctx.set("scores", scores)

        super().log(ctx, "Aesthetic scoring finished")

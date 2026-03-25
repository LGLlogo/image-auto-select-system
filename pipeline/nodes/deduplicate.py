import numpy as np
from pipeline.core.node import Node


class DeduplicateNode(Node):

    def __init__(self):
        super().__init__(name="deduplicate")

    def run(self, ctx):
        files = ctx.get("files")
        embeddings = ctx.get("embeddings")
        images = ctx.get("images")

        selected = []
        selected_idx = []
        threshold = 0.95  # 精度 越小越严格 0.85-0.95
        embeddings = np.array(embeddings)
        total = len(embeddings)
        for i in range(total):

            if not selected_idx:
                selected.append(files[i])
                selected_idx.append(i)
                continue

            sims = np.dot(embeddings[i], embeddings[selected_idx].T)

            if sims.max() < threshold:
                selected.append(files[i])
                selected_idx.append(i)

            self._emit(
               self.process.callback(i + 1, total)
            )

        # 同步更新embeddings和images
        embeddings = embeddings[selected_idx]
        images = [images[i] for i in selected_idx]

        ctx.set("files", selected)
        ctx.set("embeddings", embeddings)
        ctx.set("images", images)
        super().log(ctx, f"After deduplicate: {len(selected)}")

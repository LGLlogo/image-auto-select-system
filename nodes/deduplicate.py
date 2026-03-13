import numpy as np
from core.node import Node


class DeduplicateNode(Node):
    name = "deduplicate"

    def run(self, ctx):
        images = ctx.get("images")
        embeddings = ctx.get("embeddings")

        selected = []
        selected_idx = []
        threshold = 0.9
        embeddings = np.array(embeddings)

        for i in range(len(embeddings)):

            if not selected_idx:
                selected.append(images[i])
                selected_idx.append(i)
                continue

            sims = np.dot(embeddings[i], embeddings[selected_idx].T)

            if sims.max() < threshold:
                selected.append(images[i])
                selected_idx.append(i)

        # 同步更新embeddings
        embeddings = embeddings[selected_idx]
        ctx.set("images", selected[:30])
        ctx.set("embeddings", embeddings[:30])
        print("After deduplicate:", selected)

from operator import itemgetter

import numpy as np
from pipeline.core.node import Node


class DeduplicateNode(Node):

    def __init__(self):
        super().__init__(name="deduplicate")

    def run(self, ctx):
        records = ctx.get("records")
        embeddings = [record.clip for record in records]

        # selected = []
        selected_idx = []
        threshold = 0.95  # 精度 越小越严格 0.85-0.95
        embeddings = np.array(embeddings)
        total = len(embeddings)
        for i in range(total):

            if not selected_idx:
                # selected.append(files[i])
                selected_idx.append(i)
                continue

            sims = np.dot(embeddings[i], embeddings[selected_idx].T)

            if sims.max() < threshold:
                # selected.append(files[i])
                selected_idx.append(i)

            self._emit(
               self.progress.callback(i + 1, total)
            )

        getter = itemgetter(*selected_idx)
        result = getter(records)
        ctx.set("records", result)
        super().log(ctx, f"After deduplicate: {len(selected_idx)}")

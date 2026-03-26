from concurrent.futures import ThreadPoolExecutor

import torch
import clip
import numpy as np
from PIL import Image
from pipeline.core.node import Node
from tqdm import tqdm


def read_image(file):
    try:
        img = Image.open(file).convert("RGB")
        return img
    except:
        return None


# GPU批量
class CLIPEmbeddingNode(Node):

    def __init__(self,
                 device="cpu",
                 batch_size=32,
                 num_workers=8):
        super().__init__(name="clip_embedding")
        self.device = device
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.model, self.preprocess = clip.load(
            "ViT-L/14",
            device=device
        )

    def compute_embeddings(self, valid_images):
        embeddings = []
        total = len(valid_images)
        processed = 0

        for i in tqdm(range(0, len(valid_images), self.batch_size)):
            batch_imgs = valid_images[i:i + self.batch_size]
            mid = i + len(batch_imgs) * 0.5
            end = i + len(batch_imgs)

            inputs = torch.stack(
                [self.preprocess(img) for img in batch_imgs]
            ).to(self.device)

            self._emit(
                self.progress.callback(mid, total)
            )

            with torch.no_grad():
                emb = self.model.encode_image(inputs)

            emb = emb / emb.norm(dim=-1, keepdim=True)
            embeddings.append(emb.cpu().numpy())

            self._emit(
                self.progress.callback(end, total)
            )

        # 垂直拼接
        embeddings = np.vstack(embeddings)
        # 垂直拼接
        # embeddings = np.concatenate(embeddings, axis=0)
        return embeddings

    def run(self, ctx):
        files = ctx.get("files")
        # ---------- 多线程读取图片 ----------
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            images = list(executor.map(read_image, files))

        valid_files = []
        valid_images = []

        for f, img in zip(files, images):
            if img is not None:
                valid_files.append(f)
                valid_images.append(img)

        embeddings = self.compute_embeddings(valid_images)
        ctx.set("files", valid_files)
        ctx.set("embeddings", embeddings)
        super().log(ctx, f"CLIP embeddings computed: {len(valid_files)}")


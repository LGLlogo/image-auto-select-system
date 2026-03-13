import torch
import clip
import numpy as np
from PIL import Image
from core.node import Node
from tqdm import tqdm

device = "cuda" if torch.cuda.is_available() else "cpu"

model, preprocess = clip.load("ViT-L/14", device=device)


def compute_embeddings(image_paths, batch_size=32):
    embeddings = []

    for i in tqdm(range(0, len(image_paths), batch_size)):
        batch_paths = image_paths[i:i + batch_size]
        images = []
        for p in batch_paths:
            try:
                img = preprocess(Image.open(p).convert("RGB"))
                images.append(img)
            except:
                continue

        if len(images) == 0:
            continue

        images = torch.stack(images).to(device)
        with torch.no_grad():
            feats = model.encode_image(images)
            feats = feats / feats.norm(dim=-1, keepdim=True)
        embeddings.append(feats.cpu())

    embeddings = torch.cat(embeddings)

    return embeddings.numpy()


# GPU批量
class CLIPEmbeddingNode(Node):
    name = "clip_embedding"

    def run(self, ctx):
        images = ctx.get("images")
        embeddings = compute_embeddings(images)
        ctx.set("embeddings", embeddings)


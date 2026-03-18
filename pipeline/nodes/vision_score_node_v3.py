from concurrent.futures import ThreadPoolExecutor

import numpy as np
import cv2
import torch
import clip
from pipeline.core.node import Node


# ---------- 技术质量 ----------
def compute_metrics(img):
    # ---------- sharpness 锐度 ----------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    # ---------- exposure 曝光 ----------
    exposure = np.mean(gray)
    # ---------- colorfulness 色彩丰富度 ----------
    (B, G, R) = cv2.split(img)
    rg = np.abs(R - G)
    yb = np.abs(0.5 * (R + G) - B)
    colorfulness = np.sqrt(np.mean(rg ** 2) + np.mean(yb ** 2))
    return sharpness, exposure, colorfulness


class VisionScoreNodeV3(Node):
    name = "vision_score"

    def __init__(self, num_workers=8, device="cpu"):

        self.device = device
        self.num_workers = num_workers
        self.model, self.preprocess = clip.load(
            "ViT-L/14",
            device=device
        )

        self.prompts = {
            "technical_quality": [
                "a high resolution photograph",
                "a sharp professional photo",
                "a studio quality photograph",
                "a high detail photography",
                "a professionally shot photograph",
                "a high clarity image"
            ],
            "commercial_value": [
                "a professional stock photo",
                "a commercial advertising photograph",
                "a high quality stock photograph",
                "a premium commercial photograph",
                "a premium stock photography image",
                "a high quality marketing photo",
                "a professional product marketing photo",
                "a clean commercial photography image",
                "a stock photo suitable for advertising",
                "a professional lifestyle stock photo",
                "a corporate marketing image",
                "a professional brand marketing photograph"
            ],
            "composition_quality": [
                "a well composed photograph",
                "a balanced composition photograph",
                "a professional photography composition",
                "a rule of thirds photography",
                "a visually balanced image",
                "a clean minimal composition",
                "a professional framing photography",
                "a well structured image composition"
            ],
            "content_uniqueness": [
                "a creative photography concept",
                "a unique artistic photograph",
                "an original visual concept image",
                "a creative conceptual photography",
                "a unique storytelling photograph",
                "a fresh modern photography idea"
            ],
            "negative_content": [
                "a blurry photo",
                "a low quality photograph",
                "a poorly composed image",
                "an amateur snapshot",
                "a noisy low resolution image",
                "a badly lit photograph"
            ]
        }

        self.prompt_embeddings = self.encode_prompts()

    def encode_prompts(self):

        prompt_embeddings = {}

        for key, texts in self.prompts.items():
            tokens = clip.tokenize(texts).to(self.device)

            with torch.no_grad():
                emb = self.model.encode_text(tokens)

            emb = emb / emb.norm(dim=-1, keepdim=True)

            prompt_embeddings[key] = emb.cpu().numpy()

        return prompt_embeddings

    def run(self, ctx):
        # ---------- 主流程 ----------
        files = ctx.get("files")
        embeddings = ctx.get("embeddings")
        images = ctx.get("images")

        scores = ctx.get("scores").copy()

        # ---------- CLIP semantic scores ----------
        semantic_scores = {}
        for key, prompt_emb in self.prompt_embeddings.items():
            sim = embeddings @ prompt_emb.T
            score = sim.mean(axis=1)
            semantic_scores[key] = score

        # ---------- 图像技术指标 ----------

        sharpness_scores = []
        exposure_scores = []
        color_scores = []

        # ---------- 多线程读取图片 ----------
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            results = list(executor.map(compute_metrics, images))

            for s, e, c in results:
                sharpness_scores.append(s)
                exposure_scores.append(e)
                color_scores.append(c)

        sharpness_scores = np.array(sharpness_scores)
        exposure_scores = np.array(exposure_scores)
        color_scores = np.array(color_scores)

        commercial = semantic_scores.get("commercial_value", np.zeros(len(files)))
        composition = semantic_scores.get("composition_quality", np.zeros(len(files)))
        uniqueness = semantic_scores.get("content_uniqueness", np.zeros(len(files)))
        technical = semantic_scores.get("technical_quality", np.zeros(len(files)))
        negative = semantic_scores.get("negative_content", np.zeros(len(files)))
        # technical = normalize(sharpness_scores)
        post = color_scores + exposure_scores

        # ---------- 保存结果 ----------

        for i, f in enumerate(files):
            scores[f] = {
                **scores[f],
                "commercial_value": float(commercial[i]),
                "technical_quality": float(technical[i]),
                "composition_quality": float(composition[i]),
                "post_processing": float(post[i]),
                "content_uniqueness": float(uniqueness[i]),
                "negative_quality": float(negative[i])
            }

        ctx.set("scores", scores)

        print("VisionScoreNode v3 finished")

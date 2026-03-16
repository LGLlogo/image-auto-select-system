import cv2
import numpy as np
import torch
import clip
from PIL import Image

from core.node import Node


def laplacian_sharpness(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def color_score(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    saturation = hsv[:, :, 1].mean()
    value = hsv[:, :, 2].mean()

    return (saturation + value) / 2


def composition_score(img):
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)

    thirds_x = [w // 3, w * 2 // 3]
    thirds_y = [h // 3, h * 2 // 3]

    score = 0

    for x in thirds_x:
        score += edges[:, x].sum()

    for y in thirds_y:
        score += edges[y, :].sum()

    return score


class VisionScoreNode(Node):
    name = "vision_score"

    def __init__(self, device="cpu"):
        self.device = device
        self.model, self.preprocess = clip.load("ViT-L/14", device=device)
        self.prompts = [
            "high quality stock photo",
            "commercial advertising photo",
            "professional photography",
            "beautiful composition",
        ]

        text = clip.tokenize(self.prompts).to(device)

        with torch.no_grad():
            self.text_features = self.model.encode_text(text)
            self.text_features /= self.text_features.norm(dim=-1, keepdim=True)

    def run(self, ctx):

        files = ctx.get("images")
        embeddings = ctx.get("embeddings")

        scores = {}

        for f in files:
            img = cv2.imread(f)

            # ---------- technical quality ----------
            sharpness = laplacian_sharpness(img)
            tech_score = np.clip(sharpness / 100, 0, 10)

            # ---------- post processing ----------
            color = color_score(img)
            post_score = np.clip(color / 25, 0, 10)

            # ---------- composition ----------
            comp = composition_score(img)
            comp_score = np.clip(comp / 5000, 0, 10)

            # ---------- commercial value ----------
            image = self.preprocess(Image.open(f)).unsqueeze(0).to(self.device)

            with torch.no_grad():
                img_feature = self.model.encode_image(image)
                img_feature /= img_feature.norm(dim=-1, keepdim=True)

                similarity = (
                        img_feature @ self.text_features.T
                ).mean().item()

            commercial_score = np.clip(similarity * 10, 0, 10)

            scores[f] = {
                "commercial_value": commercial_score,
                "technical_quality": tech_score,
                "composition_quality": comp_score,
                "post_processing": post_score,
                "content_uniqueness": 0,  # 后面算
            }

        # ---------- uniqueness ----------
        # emb_list = np.array(list(embeddings.values()))

        dist = np.linalg.norm(
            embeddings[:, None, :] - embeddings[None, :, :], axis=2
        )

        uniqueness = dist.mean(axis=1)

        uniq_norm = (uniqueness - uniqueness.min()) / (
                uniqueness.max() - uniqueness.min() + 1e-6
        )

        uniq_norm *= 10.0

        for i, f in enumerate(files):
            scores[f]["content_uniqueness"] = uniq_norm[i]

        ctx.set("scores", scores)

        print("Vision scoring finished")

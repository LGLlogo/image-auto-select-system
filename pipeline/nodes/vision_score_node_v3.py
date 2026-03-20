import numpy as np
import torch
import clip
from pipeline.core.node import Node


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
            "post_processing": [
                "professionally color graded photo",
                "natural color correction, realistic tones",
                "well balanced exposure and contrast",
                "subtle and high quality post processing",
                "clean and natural photo editing",
                "soft and realistic lighting, no over processing",
                "true to life colors, professional photography",
            ],
            "content_uniqueness": [
                "a creative photography concept",
                "a unique artistic photograph",
                "an original visual concept image",
                "a creative conceptual photography",
                "a unique storytelling photograph",
                "a fresh modern photography idea"
            ],
            "negative_quality": [
                # ---------- 技术质量 ----------
                "a blurry photo",
                "a low quality photograph",
                "a poorly composed image",
                "an amateur snapshot",
                "a noisy low resolution image",

                # ---------- 技术质量 ----------
                "blurry image, out of focus, low resolution",
                "motion blur, camera shake, noisy image",
                "overexposed or underexposed photo",
                "poor lighting, low contrast, dull image",

                # ---------- 构图问题 ----------
                "bad composition, subject cut off, awkward framing",
                "no clear subject, cluttered background",
                "unbalanced composition, distracting elements",

                # ---------- 后期问题 ----------
                "overprocessed photo, excessive editing",
                "oversaturated colors, unnatural tones",
                "strong HDR effect, unrealistic lighting",
                "heavy filters, artificial look",
                "halo artifacts, sharpening artifacts",
                "plastic skin, beauty filter",

                # ---------- 商业价值 ----------
                "snapshot, casual photo, not professional",
                "random subject, no clear concept",
                "non commercial image, lacks usability",

                # ---------- 内容质量 ----------
                "boring image, generic content, not unique",
                "common scene, no visual interest",
                "repetitive subject, lack of creativity",

                # ---------- 美学问题 ----------
                "ugly image, poor aesthetics",
                "harsh lighting, unpleasant colors",
                "visually unappealing composition",

                # ---------- AI/伪影 ----------
                "AI generated artifacts, unnatural texture",
                "distorted objects, unrealistic details",
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

        commercial = semantic_scores.get("commercial_value", np.zeros(len(files)))
        composition = semantic_scores.get("composition_quality", np.zeros(len(files)))
        uniqueness = semantic_scores.get("content_uniqueness", np.zeros(len(files)))
        technical = semantic_scores.get("technical_quality", np.zeros(len(files)))
        negative = semantic_scores.get("negative_quality", np.zeros(len(files)))
        post = semantic_scores.get("post_processing", np.zeros(len(files)))

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

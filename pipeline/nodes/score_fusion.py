import numpy as np

from pipeline.core.node import Node


def normalize(scores):
    """数据分布归一化"""
    arr = np.array(scores)

    min_v = arr.min()
    max_v = arr.max()

    if max_v == min_v:
        return [0.5] * len(scores)

    norm = (arr - min_v) / (max_v - min_v)
    # 归一化到 0.1-1 避免最差图片评分全为0
    return 0.1 + 0.9 * norm


# 总评分计算
class ScoreFusionNode(Node):
    name = 'score_fusion'

    def __init__(self, top_k=10):
        self.weights = {
            "aesthetic_score": 0.30,  # 美学评分
            "commercial_value": 0.25,  # 商业价值
            "technical_quality": 0.15,  # 技术质量
            "composition_quality": 0.15,  # 构图质量
            "post_processing": 0.10,  # 后期质量
            "content_uniqueness": 0.05,  # 内容独特性
        }
        self.quality_score_weight = 0.25  # quality_filter 质量评分
        self.negative_penalty = 0.15
        # self.top_k = top_k

    def run(self, ctx):
        scores = ctx.get('scores').copy()
        files = list(scores.keys())
        normalized = {}
        for factor in self.weights:
            values = [scores[f].get(factor, 0) for f in files]
            # 统一标准化
            normalized[factor] = normalize(values)

        matrix = []

        for factor in self.weights:
            matrix.append(normalized[factor])

        # 负向质量
        negative_scores = [scores[f].get("negative_quality", 0) for f in files]
        negative_scores = normalize(negative_scores)

        # quality_filter 质量评分
        quality_scores = [scores[f].get("quality_score", 0) for f in files]

        # 向量化计算加权
        matrix = np.array(matrix)
        weight_vec = np.array(list(self.weights.values())).reshape(-1, 1)
        total_scores = (matrix * weight_vec).sum(axis=0)

        for i, f in enumerate(files):
            # 总评分 = 正向加权 - 负向加权
            base_score = float(
                (1 - self.quality_score_weight) * total_scores[i] + self.quality_score_weight * quality_scores[i])

            penalty_score = self.negative_penalty * negative_scores[i]
            scores[f]["total_score"] = float(np.clip(base_score - penalty_score, 0, 1))

        ctx.set("scores", scores)
        # 排序
        # sorted_items = sorted(
        #     scores.items(),
        #     key=lambda x: x[1]["total_score"],
        #     reverse=True
        # )

        # top_images = [x[0] for x in sorted_items[:self.top_k]]
        #
        # ctx.set("scores", scores)
        # ctx.set("top_images", top_images)
        #
        # print("Top selected:")
        #
        # for img, scores in top_images:
        #     print(img, scores)

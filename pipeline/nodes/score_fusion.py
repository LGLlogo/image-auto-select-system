import numpy as np

from pipeline.core.node import Node


def auto_weights(score_dict):
    """
    方差越大 → 区分度越强 → 权重越高
    """
    weights = {}
    total_var = 0

    for k, v in score_dict.items():
        var = np.var(v)
        weights[k] = var
        total_var += var

    for k in weights:
        weights[k] /= (total_var + 1e-6)

    return weights


def generate_explanation(features):
    exp = []

    if features["aesthetic_score"] > 0.7:
        exp.append("美学质量高")

    if features["composition_quality"] > 0.7:
        exp.append("构图优秀")

    if features["commercial_value"] > 0.7:
        exp.append("商业价值高")

    if features["post_processing"] > 0.7:
        exp.append("后期处理干净")

    if features["negative_quality"] > 0.5:
        exp.append("存在负面质量问题")

    return exp


def top_k_explanation(features, k=3):
    sorted_items = sorted(features.items(), key=lambda x: x[1], reverse=True)
    return [f"{k} 高 ({v:.2f})" for k, v in sorted_items[:k]]


def compute_confidence(features):
    vals = np.array(list(features.values()))
    return np.std(vals)  # 分数越分散 → 越有信心


def normalize(scores, method="minmax"):
    """数据分布归一化"""
    arr = np.array(scores)
    if method == "minmax":
        min_v = arr.min()
        max_v = arr.max()
        if max_v == min_v:
            return [0.5] * len(scores)

        return (arr - min_v) / (max_v - min_v + 1e-6)

    elif method == "zscore":
        x = (arr - arr.mean()) / (arr.std() + 1e-6)
        return 1 / (1 + np.exp(-x))

    elif method == "rank":
        order = arr.argsort().argsort()
        return order / len(arr)


# 总评分计算
class ScoreFusionNode(Node):

    def __init__(self, top_k=10):
        super().__init__(name='score_fusion')
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
        # scores = ctx.get('scores').copy()
        records = ctx.get("records")
        files = [record.name for record in records]
        quality_scores = ctx.get("quality_scores")
        aesthetic_scores = ctx.get("aesthetic_scores")
        vision_scores = ctx.get("vision_scores")
        scores = {}
        for file in files:
            scores[file] = {
                'quality_score': quality_scores.get(file),
                **vision_scores.get(file),
                'aesthetic_score': aesthetic_scores.get(file),
            }
        # files = list(scores.keys())
        normalized = {}
        for factor in self.weights:
            values = [scores[f].get(factor, 0) for f in files]
            # 统一标准化 clip分数使用rank
            normalized[factor] = normalize(values, method="rank")
            for i, f in enumerate(files):
                scores[f][factor] = normalized[factor][i]

        matrix = []

        score_dict = {}

        for factor in self.weights:
            score_dict[factor] = normalized[factor]
            matrix.append(normalized[factor])

        _weights = auto_weights(score_dict)

        # 负向质量
        negative_scores = [scores[f].get("negative_quality", 0) for f in files]
        negative_scores = normalize(negative_scores)

        # quality_filter 质量评分 quality_score已经normalize
        quality_scores = [scores[f].get("quality_score", 0) for f in files]

        # 向量化计算加权
        matrix = np.array(matrix)
        weight_vec = np.array(list(_weights.values())).reshape(-1, 1)
        total_scores = (matrix * weight_vec).sum(axis=0)

        for i, f in enumerate(files):
            # 总评分 = 正向加权 - 负向加权
            base_score = float(
                (1 - self.quality_score_weight) * total_scores[i] + self.quality_score_weight * quality_scores[i])

            penalty_score = self.negative_penalty * negative_scores[i]
            scores[f]["total_score"] = float(np.clip(base_score - penalty_score, 0, 1))
            self._emit(
                self.progress.callback(i + 1, len(files))
            )

        results = {}
        for file, features in scores.items():

            explanation = generate_explanation(features)
            confidence = compute_confidence(features)

            results[file] = {
                "total_score": float(features["total_score"]),
                "sub_scores": {k: float(v) for k, v in features.items() if k != 'total_score'},
                "weights": _weights,
                "explanation": explanation,
                "confidence": float(confidence)
            }

        ctx.set("scores", scores)
        ctx.set("output_scores", results)

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

from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

from core.node import Node


def normalize(scores):
    """数据分布归一化"""
    arr = np.array(scores)

    min_v = arr.min()
    max_v = arr.max()

    if max_v - min_v < 1e-6:
        return np.ones_like(scores) * 0.5

    return (arr - min_v) / (max_v - min_v)


def compute_metrics(img):
    """图片质量指标"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1 sharpness 锐度
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 2 brightness 曝光
    exposure = gray.mean()

    # 3 contrast 对比度
    contrast = gray.std()

    # 4 noise estimation 噪声
    noise = np.std(gray - cv2.GaussianBlur(gray, (3, 3), 0))

    # 5 dynamic range 动态范围
    dyn_range = np.percentile(gray, 95) - np.percentile(gray, 5)

    # 6 motion blur (gradient energy) 运动模糊
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    motion_energy = np.mean(np.sqrt(gx ** 2 + gy ** 2))

    # 7 jpeg artifact (blockiness) JPEG压缩伪影
    diff = np.abs(gray[:, 8:] - gray[:, :-8])
    blockiness = np.mean(diff)
    # 8 resolution 分辨率
    h, w = img.shape[:2]
    resolution = min(h, w)

    return (
        sharpness,
        exposure,
        contrast,
        noise,
        dyn_range,
        motion_energy,
        blockiness,
        resolution
    )


class QualityFilterNode(Node):
    name = 'quality_filter'

    def __init__(self, num_workers=16):
        self.num_workers = num_workers
        # 清晰度
        self.min_sharpness = 60
        # 曝光
        self.min_brightness = 40
        self.max_brightness = 210
        # 对比度
        self.min_contrast = 18
        # 噪声
        self.max_noise = 25
        # 分辨率
        self.min_resolution = 1200

    def run(self, ctx):
        files = ctx.get("files")
        images = ctx.get("images")
        keep_indices = []

        tasks = []
        for idx, img in enumerate(images):
            tasks.append(img)
        # ---------- 多线程读取图片 ----------
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            metrics = list(executor.map(compute_metrics, tasks))

        metrics = np.array(metrics)
        sharpness = metrics[:, 0]
        exposure = metrics[:, 1]
        contrast = metrics[:, 2]
        noise = metrics[:, 3]
        dyn_range = metrics[:, 4]
        motion = metrics[:, 5]
        blockiness = metrics[:, 6]
        resolution = metrics[:, 7]

        sharpness_n = normalize(sharpness)
        exposure_n = normalize(exposure)
        contrast_n = normalize(contrast)
        dyn_range_n = normalize(dyn_range)
        noise_n = 1 - normalize(noise)
        motion_n = normalize(motion)
        blockiness_n = 1 - normalize(blockiness)
        resolution_n = np.array(normalize(resolution))

        quality_score = (
                0.30 * sharpness_n +
                0.15 * contrast_n +
                0.15 * dyn_range_n +
                0.10 * exposure_n +
                0.10 * motion_n +
                0.10 * noise_n +
                0.05 * resolution_n +
                0.05 * blockiness_n
        )
        for idx, score in enumerate(quality_score):
            if score < 0.25:
                continue
            keep_indices.append((idx, score))

        # 保留 top 80%
        keep_indices.sort(key=lambda x: x[1], reverse=True)
        top_k = int(len(keep_indices) * 0.8)
        keep_files = [files[x[0]] for x in keep_indices[:top_k]]
        images = [images[x[0]] for x in keep_indices[:top_k]]

        scores = ctx.setdefault("scores", {})
        # 质量评分 总评分计算要进行加权
        for i, f in enumerate(keep_files):
            scores.setdefault(f, {})
            scores[f]["quality_score"] = float(quality_score[i])

        ctx.set("files", keep_files)
        ctx.set("images", images)
        ctx.set("scores", scores)

        print("After quality filter:", len(keep_files))

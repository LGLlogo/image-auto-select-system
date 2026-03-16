import os
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
import easyocr
from ultralytics import YOLO
from core.node import Node


class ContentSafetyFilterNode(Node):
    name = "content_safety_filter"

    def __init__(self,
                 num_workers=None,
                 batch_size=16,
                 device="cpu"):

        self.device = device

        self.batch_size = batch_size
        # self.num_workers = num_workers / 2 or os.cpu_count() / 2
        self.num_workers = 4

        # 人脸检测
        self.face_model = YOLO("models/yolov8n-face.pt")
        # self.face_model.prepare(ctx_id=0 if device == "cuda" else -1)

        # logo / object detection
        self.detector = YOLO("models/yolov8n.pt")

        # OCR
        self.ocr = easyocr.Reader(["en"], gpu=(device == "cuda"))

        # QR detection
        self.qr_detector = cv2.QRCodeDetector()

        # 常见品牌词
        self.brand_words = [
            "nike", "apple", "coca", "cola", "adidas",
            "sony", "canon", "tesla", "bmw", "toyota"
        ]

    def process_extra_checks(self, idx_img):
        """多线程任务调用"""
        idx, img = idx_img

        if self.detect_qrcode(img):
            return idx, False

        if self.detect_text_brand(img):
            return idx, False

        return idx, True

    def detect_text_brand(self, img):
        """ocr识别"""
        # TODO
        return img is None
        # ocr_results = self.ocr.readtext(img)
        #
        # for (_, text, conf) in ocr_results:
        #
        #     t = text.lower()
        #
        #     for brand in self.brand_words:
        #         if brand in t:
        #             return True
        #
        # return False

    def detect_qrcode(self, img):
        """qrcode识别"""
        # return img is None
        data, bbox, _ = self.qr_detector.detectAndDecode(img)
        return bbox is not None

    def detect_yolo_batch(self, yolo_model, images, valid_indices):
        """yolo batch"""
        results = yolo_model(images,
                             batch=self.batch_size,
                             verbose=False)
        pass_indices = []
        for i, r in enumerate(results):
            if r.boxes is None or len(r.boxes) == 0:
                pass_indices.append(valid_indices[i])

        return pass_indices

    def run(self, ctx):

        files = ctx.get("files")
        # embeddings = ctx.get("embeddings")

        removed = {
            "face": 0,
            "logo": 0,
            "brand_text": 0,
            "qr": 0
        }

        images = ctx.get("images")
        valid_indices = []
        for i, img in enumerate(images):
            valid_indices.append(i)

        # ---------- YOLO batch face detection ----------
        face_pass_indices = self.detect_yolo_batch(self.face_model, images, valid_indices)
        removed["face"] = len(valid_indices) - len(face_pass_indices)

        # ---------- YOLO batch logo detection ----------
        logo_pass_indices = self.detect_yolo_batch(self.detector, images, valid_indices)
        removed["logo"] = len(valid_indices) - len(logo_pass_indices)

        # ---------- extra checks (OCR / QR) ----------
        all_pass_indices = list(set(face_pass_indices).union(set(logo_pass_indices)))
        tasks = []
        for idx in all_pass_indices:
            tasks.append((idx, images[idx]))

        keep_indices = []
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            results = executor.map(self.process_extra_checks, tasks)

            for idx, keep in results:
                if keep:
                    keep_indices.append(idx)

        keep_indices.sort()
        keep_files = [files[i] for i in keep_indices]
        # embeddings = embeddings[keep_indices]
        images = [images[i] for i in keep_indices]

        print("ContentSafetyFilter v3 result:")
        print("kept:", len(keep_files))
        print("removed:", removed)

        ctx.set("files", keep_files)
        # ctx.set("embeddings", embeddings)
        ctx.set("images", images)

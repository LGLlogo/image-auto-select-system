import os
import zipfile
from collections import namedtuple

import cv2
import numpy as np

from pipeline.core.node import Node


def read_cv_image(path):
    img = cv2.imread(path)
    if img is None:
        raise
    return img


# 图片读取层
class LoadImagesZipNode(Node):

    def __init__(self, image_zip_path):
        super().__init__(name="load_images")
        self.image_zip_path = image_zip_path

    def run(self, ctx):

        files = []
        cv2_images = []
        with zipfile.ZipFile(self.image_zip_path, 'r') as z:
            total = len(z.namelist())
            for i, name in enumerate(z.namelist()):
                if name.lower().endswith((".jpg", ".jpeg", ".png")):
                    # 1. 读取二进制数据
                    img_bytes = z.read(name)
                    # 2. 将二进制数据转换为内存文件对象
                    img_array = np.frombuffer(img_bytes, np.uint8)
                    # 3. 使用 OpenCV 解码 (IMREAD_COLOR 表示读取为彩色图)
                    # 此时 img 就是一个标准的 numpy 数组，可以直接送入模型
                    # print(img.shape)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if img is not None:
                        # file_path = os.path.join(os.path.dirname(self.image_zip_path), name)
                        files.append(name.lower())
                        cv2_images.append(img)

                        self._emit(
                            self.progress.callback(i + 1, total)
                        )

        ImageRecord = namedtuple('image_record', ['name', 'image'])
        records = [ImageRecord(n, i) for n, i in zip(files, cv2_images)]
        ctx.set("records", records)

        super().log(ctx, f"Loaded images: {len(files)}")

import os

import cv2

from pipeline.core.node import Node


def read_cv_image(path):
    img = cv2.imread(path)
    if img is None:
        raise
    return img


# 图片读取层
class LoadImagesNode(Node):
    name = "load_images"

    def __init__(self, image_dir, num_workers=16):
        self.num_workers = num_workers
        self.image_dir = image_dir

    def run(self, ctx):

        files = []
        images = []
        for f in os.listdir(self.image_dir):
            if f.lower().endswith(("jpg", "jpeg", "png")):
                file_path = os.path.join(self.image_dir, f)
                # files.append(file_path)
                img = cv2.imread(file_path)
                if img is not None:
                    files.append(file_path)
                    images.append(img)

        # ---------- 多线程读取图片 ----------
        # with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
        #     images = list(executor.map(read_cv_image, files))

        ctx.set("files", files)
        ctx.set("images", images)
        super().log(ctx, f"Loaded images: {len(files)}")

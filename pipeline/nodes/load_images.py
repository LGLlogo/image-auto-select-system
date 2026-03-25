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

    def __init__(self, image_dir, num_workers=16):
        super().__init__(name="load_images")
        self.num_workers = num_workers
        self.image_dir = image_dir

    def run(self, ctx):

        files = []
        images = []
        input_image_dir = self.image_dir if self.image_dir else ctx.get("input_image_dir")
        image_paths = os.listdir(input_image_dir)
        total = len(image_paths)
        for i, f in enumerate(image_paths):
            if f.lower().endswith(("jpg", "jpeg", "png")):
                file_path = os.path.join(input_image_dir, f)
                # files.append(file_path)
                img = cv2.imread(file_path)
                if img is not None:
                    files.append(file_path)
                    images.append(img)
                    self._emit(
                        self.process.callback(i + 1, total)
                    )

        # ---------- 多线程读取图片 ----------
        # with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
        #     images = list(executor.map(read_cv_image, files))

        ctx.set("files", files)
        ctx.set("images", images)
        super().log(ctx, f"Loaded images: {len(files)}")

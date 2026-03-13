import os
from core.node import Node


# 图片读取层
class LoadImagesNode(Node):
    name = "load_images"

    def __init__(self, image_dir):
        self.image_dir = image_dir

    def run(self, ctx):

        images = []

        for f in os.listdir(self.image_dir):
            if f.lower().endswith(("jpg", "jpeg", "png")):
                images.append(os.path.join(self.image_dir, f))

        ctx.set("images", images)

        print("Loaded images:", len(images))

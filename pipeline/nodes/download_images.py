from pathlib import Path

from pipeline.core.node import Node
from quark.quark import download_images_from_quark


class DownloadImagesNode(Node):
    name = "download_images"

    def __init__(self, folder_name, input_image_dir):
        self.folder_name = folder_name
        self.input_image_dir = input_image_dir

    def run(self, ctx):
        logger = ctx.get("logger")
        l = download_images_from_quark(folder_name=self.folder_name, desc_save_dir=self.input_image_dir, logger=logger)
        super().log(ctx, f"Download images: {l}")
        path = Path(self.input_image_dir)
        # 保存绝对路径
        ctx.set("input_image_dir", path.absolute())

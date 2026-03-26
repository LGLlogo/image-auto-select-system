import os
from pathlib import Path

from pipeline.core.node import Node
from quark_client import QuarkClient


class DownloadImagesNode(Node):

    def __init__(self, folder_name, input_image_dir):
        super().__init__(name="download_images")
        self.folder_name = folder_name
        self.input_image_dir = input_image_dir

    def download_images_from_quark(self):
        with QuarkClient() as client:
            # 搜索文件
            results = client.search_files(self.folder_name, size=1)
            print(f"找到 {len(results['data']['list'])} 个文件")
            # print(results['data']['list'])
            folder_id = results['data']['list'][0]['fid']
            files = client.list_files(folder_id, size=20)
            files = files['data']['list']
            # print(len(files))
            Path(self.input_image_dir).mkdir(exist_ok=True)
            input_images = os.listdir(self.input_image_dir)
            file_ids = [file['fid'] for file in files if file['file_name'] not in input_images]
            print(file_ids)

            def progress_callback(current, total, downloaded_bytes, total_bytes):
                self._emit(
                    self.progress.callback(current, total, downloaded_bytes, total_bytes)
                )
                # bar_length = int((abs(downloaded_bytes) / total_bytes) * 10)
                # bar_str = "█" * bar_length + "-" * (10 - bar_length)
                # print('download_images', f"image[{current}/{total}] download Progress: | {bar_str} | "
                #                          f"{downloaded_bytes / total_bytes * 100:.2f} % Complete")

            client.download.download_files(file_ids=file_ids, save_dir=self.input_image_dir,
                                           progress_callback=progress_callback)
            return len(file_ids)

    def run(self, ctx):
        count = self.download_images_from_quark()
        super().log(ctx, f"Download images: {count}")
        path = Path(self.input_image_dir)
        # 保存绝对路径
        ctx.set("input_image_dir", path.absolute())
        self._emit(
            self.progress.callback(1, 1)
        )

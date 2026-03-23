import logging
import os
from pathlib import Path

from quark_client import QuarkClient


def download_images_from_quark(folder_name: str, desc_save_dir: str):
    with QuarkClient() as client:
        # 搜索文件
        results = client.search_files(folder_name, size=1)
        print(f"找到 {len(results['data']['list'])} 个文件")
        # print(results['data']['list'])
        folder_id = results['data']['list'][0]['fid']
        files = client.list_files(folder_id, size=10)
        files = files['data']['list']
        # print(len(files))
        input_images = os.listdir(desc_save_dir)
        file_ids = [file['fid'] for file in files if file['file_name'] not in input_images]
        print(file_ids)

        def progress_callback(current, total, downloaded_bytes, total_bytes):
            pass
            # bar_length = int((abs(downloaded_bytes) / total_bytes) * 10)
            # bar_str = "█" * bar_length + "-" * (10 - bar_length)
            # logger.info('download_images', f"image[{current}/{total}] download Progress: | {bar_str} | "
            #                                f"{downloaded_bytes / total_bytes * 100:.2f} % Complete")

        client.download.download_files(file_ids=file_ids, save_dir=desc_save_dir, progress_callback=progress_callback)
        return len(file_ids)


if __name__ == "__main__":
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(levelname)s - %(message)s',
    #     handlers=[
    #         logging.StreamHandler()
    #     ]
    # )
    # logger = logging.getLogger(__name__)
    download_images_from_quark(folder_name='0104相机', desc_save_dir='input_images')

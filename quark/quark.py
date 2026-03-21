from pathlib import Path

from quark_client import QuarkClient


def progress_callback(current, total, downloaded_bytes, total_bytes):
    pass
    # print(f"文件: [{current}/{total}] 进度: [{downloaded_bytes}/{total_bytes}]")


def download_images_from_quark(folder_name: str, desc_save_dir: str):
    with QuarkClient() as client:
        # 搜索文件
        results = client.search_files(folder_name, size=1)
        print(f"找到 {len(results['data']['list'])} 个文件")
        print(results['data']['list'])
        folder_id = results['data']['list'][0]['fid']
        files = client.list_files(folder_id, size=50)
        files = files['data']['list']
        print(len(files))
        file_ids = [file['fid'] for file in files]
        print(file_ids)
        # 获取下载链接
        # download_url = client.download.get_download_url("ca7a320357d44f379f1dc07cde2c791f")
        # print(download_url)
        client.download.download_files(file_ids=file_ids, save_dir=desc_save_dir, progress_callback=progress_callback)
        return len(file_ids)


if __name__ == "__main__":
    # download_images_from_quark(folder_name='0104相机', desc_save_dir='input_images')
    path = Path('input_images')
    print(path.absolute())
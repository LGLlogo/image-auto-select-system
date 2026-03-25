

class DownloadProgress:

    def __init__(self, node_id):
        self.node_id = node_id

    def callback(self, current, total, downloaded_bytes=0, total_bytes=0):
        """
        按“图片数量 + 当前图片进度”计算总进度
        :param current:
        :param total:
        :param downloaded_bytes:
        :param total_bytes:
        :return:
        """
        finished = current

        current_progress = (
            downloaded_bytes / total_bytes
            if total_bytes > 0 else 0
        )

        percent = (finished + current_progress) / total * 100

        # bar_length = int(percent)
        # bar_str = "█" * bar_length + "-" * (100 - bar_length)
        # print(
        #     f"图片 {current}/{total} "
        #     f"Progress: | {bar_str} | "
        #     f"{downloaded_bytes}/{total_bytes} | "
        #     f"总进度: {percent:.2f}%"
        # )

        return {
            "type": "process",
            "node_id": self.node_id,
            "current": current,
            "total": total,
            "percent": percent
        }

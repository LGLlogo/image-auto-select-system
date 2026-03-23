import json
import logging
import os
import shutil
import zipfile
from pathlib import Path

from PIL import Image

from backend.state import TaskManager
from pipeline.core.node import Node


def make_thumb(src, dst):
    """缩略图"""
    img = Image.open(src)
    img.thumbnail((400, 400))
    img.save(dst, quality=85)


class FileStorgeNode(Node):
    """
    文件保存
    """

    name = "file_storge"

    def __init__(self):
        """初始化目录管理器"""
        self.images_dir = "images"
        self.logs_dir = "logs"
        self.thumb_dir = "thumb"
        self.data_dir = "data"

    def _create_directories(self, ctx):
        """创建必要的目录"""
        directories = [self.images_dir, self.logs_dir, self.thumb_dir, self.data_dir]
        for directory in directories:
            try:
                Path(directory).mkdir(exist_ok=True)
                super().info(ctx, f"目录 '{directory}' 创建成功或已存在")
            except Exception as e:
                super().info(ctx, f"创建目录 '{directory}' 时出错: {e}")

    def run(self, ctx):
        self._create_directories(ctx)
        self.zip_images(ctx)
        self.zip_logs(ctx)
        self.data_storge(ctx)

    def zip_images(self, ctx):
        """压缩图片"""
        task_id = ctx.get("task_id")
        _state = TaskManager.get_state(task_id)
        images = ctx.get('selected_images')
        scores = ctx.get("scores")
        # 移动图片到目标目录
        moved_files = []
        for src_path in images:
            if os.path.exists(src_path):
                # 评分_文件名
                filename = f"{round(scores[src_path]['total_score'], 3):.3f}_{os.path.basename(src_path)}"
                dest_path = os.path.join(self.images_dir, filename)
                dest_thumb_path = os.path.join(self.thumb_dir, filename)
                try:
                    shutil.copy(src_path, dest_path)
                    # 缩略图
                    make_thumb(src_path, dest_thumb_path)
                    moved_files.append(dest_path)
                    super().info(ctx, f"已复制: {src_path} -> {dest_path}")
                except Exception as e:
                    super().error(ctx, f"移动文件 {src_path} 时出错: {e}")
            else:
                super().error(ctx, f"警告: 文件不存在 {src_path}")

        # 创建ZIP文件
        zip_filepath = f"images_{task_id}.zip"
        try:
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_STORED, compresslevel=1) as zipf:
                for file_path in moved_files:
                    # 将文件添加到ZIP中，只保留文件名（不包含目录结构）
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
            super().info(ctx, f"最终选图压缩文件已创建: {zip_filepath}")
            return zip_filepath
        except Exception as e:
            super().error(ctx, f"创建ZIP文件时出错: {e}")
            raise

    def zip_logs(self, ctx):
        """打包日志"""
        task_id = ctx.get("task_id")
        _state = TaskManager.get_state(task_id)
        zip_filename = f"logs_backup_{task_id}.zip"

        # 确保日志目录存在
        logs_path = Path(self.logs_dir)
        if not logs_path.exists():
            super().error(ctx, f"日志目录不存在: {self.logs_dir}")
            raise FileNotFoundError(f"日志目录不存在: {self.logs_dir}")

        # 获取所有日志文件
        log_files = list(logs_path.glob("*.*"))
        if not log_files:
            super().error(ctx, "日志目录中没有找到.log文件")
            return

        # 创建ZIP文件并添加日志文件
        try:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_STORED, compresslevel=1) as zipf:
                for log_file in log_files:
                    # 添加文件到ZIP，保持目录结构
                    zipf.write(log_file, log_file.name)
                    super().info(ctx, f"已添加日志文件: {log_file.name}")

            super().info(ctx, f"日志文件已成功压缩到: {zip_filename}")
            return zip_filename
        except Exception as e:
            super().error(ctx, f"创建ZIP文件时出错: {e}")
            raise

    def data_storge(self, ctx):
        task_id = ctx.get("task_id")
        state = TaskManager.get_state(task_id)
        state_data = {
            "task_id": state.task_id,
            "nodes": state.nodes,
            "results": state.results,
            "dag": state.dag
        }
        # 保存到JSON文件
        try:
            filepath = os.path.join(self.data_dir, f"state_{task_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            super().info(ctx, f"分析数据已保存: {filepath} ")
        except Exception as e:
            super().error(ctx, f"保存状态失败: {e}")
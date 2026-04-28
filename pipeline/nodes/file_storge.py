import io
import json
import logging
import os
import shutil
import zipfile
from pathlib import Path

import cv2
from PIL import Image

from backend.state import TaskManager
from pipeline.config.Config import get_config
from pipeline.core.node import Node

cfg = get_config()


def make_thumb(dst, cv2_image):
    """缩略图"""
    h, w = cv2_image.shape[:2]
    # --- 按比例缩放 ---
    # 2. 计算缩放比例 (新宽度 / 原宽度) 宽度缩小到 30%
    scale_factor = float(w * 0.3) / w

    medium_img = cv2.resize(cv2_image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    cv2.imwrite(dst, medium_img)


class FileStorgeNode(Node):
    """
    文件保存
    """

    def __init__(self):
        """初始化目录管理器"""
        super().__init__(name="file_storge")
        self.node_progress = {
            cfg.images_dir: 0,
            cfg.logs_dir: 0,
            cfg.thumb_dir: 0,
            cfg.data_dir: 0
        }
        self.file_storge_weight = {
            cfg.images_dir: 0,
            cfg.logs_dir: 0,
            cfg.thumb_dir: 0,
            cfg.data_dir: 0
        }
        self.total = 0

    def _create_directories(self, ctx):
        """创建必要的目录"""
        directories = self.file_storge_weight.keys()
        for directory in directories:
            try:
                Path(directory).mkdir(exist_ok=True)
                super().info(ctx, f"目录 '{directory}' 创建成功或已存在")
            except Exception as e:
                super().info(ctx, f"创建目录 '{directory}' 时出错: {e}")

    def _count_files(self, ctx):
        records = ctx.get("records")
        self.file_storge_weight[cfg.images_dir] = len(records)
        self.file_storge_weight[cfg.thumb_dir] = len(records)

        # 确保日志目录存在
        logs_path = Path(cfg.logs_dir)
        if not logs_path.exists():
            super().error(ctx, f"日志目录不存在: {cfg.logs_dir}")
            raise FileNotFoundError(f"日志目录不存在: {cfg.logs_dir}")

        # 获取所有日志文件
        self.log_files = list(logs_path.glob("*.*"))
        if not self.log_files:
            super().error(ctx, "日志目录中没有找到.log文件")
            return

        # 创建ZIP文件并添加日志文件
        self.file_storge_weight[cfg.logs_dir] = len(self.log_files)
        self.file_storge_weight[cfg.data_dir] = 1

        self.total = sum(v for v in self.file_storge_weight.values())

    def run(self, ctx):
        self._create_directories(ctx)
        self._count_files(ctx)
        self.zip_images(ctx)
        self.zip_logs(ctx)
        self.data_storge(ctx)

    def emit_total_progress(self):
        sub_total = sum(percent * 1.0 for percent in self.node_progress.values())

        self._emit(
            # 权重 * percent
            self.progress.callback(sub_total, self.total)
        )

    def zip_images(self, ctx):
        """压缩图片"""
        task_id = ctx.get("task_id")
        _state = TaskManager.get_state(task_id)
        records = ctx.get("records")
        files = [record.name for record in records]
        cv2_images = [record.image for record in records]
        scores = ctx.get("scores")
        # 移动图片到目标目录
        moved_files = []
        if not cfg.is_clear_temp_file:
            for file_name, cv2_image in zip(files, cv2_images):
                # 评分_文件名
                filename = f"{round(scores[file_name]['total_score'], 3):.3f}_{file_name}"
                dest_path = os.path.join(cfg.images_dir, filename)
                try:
                    cv2.imwrite(dest_path, cv2_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                    # shutil.copy(src_path, dest_path)
                    # 缩略图
                    if cfg.is_create_thumb:
                        dest_thumb_path = os.path.join(cfg.thumb_dir, filename)
                        make_thumb(dest_thumb_path, cv2_image)
                    moved_files.append(dest_path)
                    self.node_progress[cfg.thumb_dir] += 1
                    self.emit_total_progress()
                    super().info(ctx, f" {dest_path} 图片已生成")
                except Exception as e:
                    super().error(ctx, f"图片 {dest_path} 生成时出错: {e}")

            # 创建ZIP文件
            zip_filepath = f"images_{task_id}.zip"
            try:
                with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_STORED) as zipf:
                    for file_path in moved_files:
                        # 将文件添加到ZIP中，只保留文件名（不包含目录结构）
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
                        self.node_progress[cfg.images_dir] += 1
                        self.emit_total_progress()
                super().info(ctx, f"最终选图压缩文件已创建: {zip_filepath}")
                return zip_filepath
            except Exception as e:
                super().error(ctx, f"创建ZIP文件时出错: {e}")
                raise

        else:
            zip_buffer = io.BytesIO()
            # 使用这个内存对象初始化ZipFile
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, cv2_image in zip(files, cv2_images):
                    # cv2.IMWRITE_JPEG_QUALITY 用于设置JPEG质量 (0-100)，100为最高质量
                    is_success, img_bytes = cv2.imencode(cv2_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

                    if is_success:
                        # 将编码后的字节数据写入ZIP包
                        # arcname 是压缩包内的文件名
                        # 评分_文件名
                        filename = f"{round(scores[file_name]['total_score'], 3):.3f}_{file_name}"
                        zip_file.writestr(filename, img_bytes)
                        super().info(ctx, f" {filename} 图片已添加到压缩包")
                    else:
                        super().info(ctx, f"{filename} 图片图片编码失败")

            # 将内存中完整的ZIP数据写入到物理磁盘
            zip_filepath = f"images_{task_id}.zip"
            with open(zip_filepath, 'wb') as f:
                f.write(zip_buffer.getvalue())

            super().info(ctx, f"ZIP压缩包已生成: {zip_filepath}")

    def zip_logs(self, ctx):
        """打包日志"""
        task_id = ctx.get("task_id")
        _state = TaskManager.get_state(task_id)
        zip_filename = f"logs_backup_{task_id}.zip"

        try:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_STORED) as zipf:
                for log_file in self.log_files:
                    # 添加文件到ZIP，保持目录结构
                    zipf.write(log_file, log_file.name)
                    self.node_progress[cfg.logs_dir] += 1
                    self.emit_total_progress()
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
            filepath = os.path.join(cfg.data_dir, f"state_{task_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
                self.node_progress[cfg.data_dir] += 1
                self.emit_total_progress()
            super().info(ctx, f"分析数据已保存: {filepath} ")
        except Exception as e:
            super().error(ctx, f"保存状态失败: {e}")

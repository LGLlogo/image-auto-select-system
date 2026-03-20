import json
import logging
import time
from pathlib import Path


def setup_logging(task_id):
    """根据task_id配置日志系统"""
    # 创建logs目录
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # 配置日志格式
    log_filename = logs_dir / f"app-{task_id}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='gb2312'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


class LogStore:
    logs = {}

    @classmethod
    def add(cls, log):
        cls.logs.setdefault(log["task_id"], []).append(log)

    @classmethod
    def get(cls, task_id):
        return cls.logs.get(task_id, [])

    @classmethod
    def save_log(cls, log):
        cls.logs.setdefault(log["task_id"], []).append(log)
        with open(f"logs/app-{log['task_id']}.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(log) + "\n")


class TaskLogger:

    def __init__(self, task_id, emitter=None):
        self.task_id = task_id
        self.emitter = emitter  # WebSocket 推送
        self.logger = setup_logging(task_id)

    def info(self, node, message):
        """INFO日志"""
        self.log(node, message, logging.INFO)

    def error(self, node, message):
        """ERROR日志"""
        self.log(node, message, logging.ERROR)

    def log(self, node, message, level=logging.INFO):
        data = {
            "type": "log",
            "task_id": self.task_id,
            "node": node,
            "level": level,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
        }

        # 全局日志写入
        self.logger.log(level=level, msg=message)

        # 推送到前端
        if self.emitter:
            self.emitter({
                **data,
                "logs": LogStore.logs,

            })

        # 本地存储
        LogStore.save_log(data)

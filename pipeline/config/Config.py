import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import yaml


@dataclass
class Config:
    """
    系统配置类 - 单例模式

    设计说明：
    - 使用 dataclass 简化配置属性定义
    - 所有配置项从配置文件读取，支持默认值
    - 类方法 get_instance() 实现单例访问
    """
    # 邮件配置（只需邮箱和授权码，SMTP 自动识别）
    # email_sender: Optional[str] = None  # 发件人邮箱
    # email_password: Optional[str] = None  # 邮箱密码/授权码
    # email_receivers: List[str] = field(default_factory=list)  # 收件人列表（留空则发给自己）

    # 目录配置
    images_dir: str = None
    logs_dir: str = None
    thumb_dir: str = None
    data_dir: str = None

    # 文件操作
    is_create_thumb: bool = False
    is_clear_temp_file: bool = False

    # === 系统配置 ===
    max_workers: int = 3  # 低并发防封禁
    debug: bool = False

    # === 定时任务配置 ===
    schedule_enabled: bool = False  # 是否启用定时任务
    schedule_time: str = "18:00"  # 每日推送时间（HH:MM 格式）

    # 单例实例存储
    _instance: Optional['Config'] = None

    @classmethod
    def get_instance(cls) -> 'Config':
        """
        获取配置单例实例

        单例模式确保：
        1. 全局只有一个配置实例
        2. 配置只从环境变量加载一次
        3. 所有模块共享相同配置
        """
        if cls._instance is None:
            cls._instance = cls._load_from_yaml()
        return cls._instance

    @classmethod
    def _load_from_yaml(cls) -> 'Config':
        current_file_path = Path(__file__).resolve()
        project_root = current_file_path.parent.parent.parent
        print(project_root)
        with open(os.path.join(project_root, 'config.yaml'), 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)

        # 2. 获取配置值
        images_dir = cfg['dir']['images']
        logs_dir = cfg['dir']['logs']
        thumb_dir = cfg['dir']['thumbs']
        data_dir = cfg['dir']['data']
        is_create_thumb = cfg['dir']['is_create_thumb']
        is_clear_temp_file = cfg['is_clear_temp_file']
        return cls(

            # email_sender=os.getenv('EMAIL_SENDER', ''),
            # email_password=os.getenv('EMAIL_PASSWORD', ''),
            # email_receivers=[r.strip() for r in os.getenv('EMAIL_RECEIVERS', '').split(',') if
            #                  r.strip()],

            images_dir=images_dir,
            logs_dir=logs_dir,
            thumb_dir=thumb_dir,
            data_dir=data_dir,
            is_create_thumb=is_create_thumb,
            is_clear_temp_file=is_clear_temp_file

            # max_workers=int(os.getenv('MAX_WORKERS', '3')),
            # debug=os.getenv('DEBUG', 'false').lower() == 'true',
            # schedule_enabled=os.getenv('SCHEDULE_ENABLED', 'false').lower() == 'true',
            # schedule_time=os.getenv('SCHEDULE_TIME', '18:00'),
        )

    def validate(self) -> List[str]:
        """
        验证配置完整性

        Returns:
            缺失或无效配置项的警告列表
        """
        warnings = []
        return warnings


# === 便捷的配置访问函数 ===
def get_config() -> Config:
    """获取全局配置实例的快捷方式"""
    return Config.get_instance()


def is_linux() -> bool:
    return os.name == 'posix'


if __name__ == "__main__":
    # 测试配置加载
    config = get_config()
    print("=== 配置加载测试 ===")
    print(f"最大并发数: {config.is_create_thumb}")
    print(f"调试模式: {config.data_dir}")

    # 验证配置
    warnings = config.validate()
    if warnings:
        print("\n配置验证结果:")
        for w in warnings:
            print(f"  - {w}")

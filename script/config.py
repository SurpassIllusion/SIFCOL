import os
import shutil
import winreg
from typing import Dict, List, Optional

import yaml
from cmd_line import get_config_path
from constant import root_path, wait_exit
from pydantic import BaseModel, Field


class Config(BaseModel):
    # 脚本基础配置
    ModelName: Optional[str] = Field("yolo", title="模型的名称,默认是yolo.onnx")
    project_root: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LogFilePath: Optional[str] = Field(None, title="日志文件路径")

    # 游戏崩溃捕获及处理
    RebootCount: int = Field(0, title="截取窗口失败次数")

    # 赞助商
    IsVIP : bool = Field(True,title="是否VIP")
    TargetTC : int = Field(90,title="目标TC")
    TargetSC: int = Field(120, title="目标SC")

    # 经理人
    OcrInterval: float = Field(0.5, title="OCR间隔时间经理人", ge=0)
    

    def __init__(self, **data):
        super().__init__(**data)
        if not self.LogFilePath:
            self.LogFilePath = os.path.join(self.project_root, "si_log.txt")

config_path = get_config_path()
# 判断是否存在配置文件
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = Config(**yaml.safe_load(f))
else:
    config = Config()
    # with open(config_path, "w", encoding="utf-8") as f:
    #     yaml.safe_dump(config.dict(), f)
    """
    若初始化时config文件不存在将复制example自动生成config文件
    替代之版本yaml函数读取无注释字符串流版本的无格式config文件
    并提醒用户配置文件
    """
    config_example = os.path.join(config.project_root, "config.example.yaml")
    config_auto = os.path.join(config.project_root, "config.yaml")
    with open(config_example, "rb") as source_file:
        with open(config_auto, "wb") as dest_file:
            shutil.copyfileobj(source_file, dest_file)
    print("\n未找到配置文件，已按example为模板自动生成，请进行配置")

from datetime import datetime, timedelta
from enum import Enum

from colorama import Fore, Style, init
from config import config
from pydantic import BaseModel, Field


class StatusInfo(BaseModel):
    fightTime: datetime = Field(datetime.now(), title="战斗开始时间")
    adaptsType: int = Field(None, title="适配类型")
    adaptsResolution: str = Field(None, title="适配分辨率")
    currentPageName: str = Field("", title="当前页面名称")
    def resetTime(self):
        self.fightTime = datetime.now()
        self.idleTime = datetime.now()
        self.lastFightTime = datetime.now()


info = StatusInfo()

lastMsg = ""


def logger(msg: str, level: str = "INFO", display: bool = True):
    global lastMsg
    content = (
        f"SIFCOL "+
        f"【{level}】".ljust(7,' ') +
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
    )
    # ljust函数对齐log输出
    content += f"{msg}"

    start = "\n" if lastMsg != msg else "\r"
    content = start + content

    # 设置日志级别颜色
    if level == "INFO":
        color = Fore.WHITE
    elif level == "WARN":
        color = Fore.YELLOW
    elif level == "ERROR":
        color = Fore.RED
    elif level == "DEBUG":
        color = Fore.GREEN
    else:
        color = Fore.WHITE
    colored_content = color + content

    if display:
        print(colored_content, end="")
        lastMsg = msg

    with open(config.LogFilePath, 'a', encoding='utf-8') as log_file:
        log_file.write(content)

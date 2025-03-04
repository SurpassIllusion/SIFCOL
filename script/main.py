import ctypes
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from multiprocessing import Event, Process

import init
import pyautogui
import version
from cmd_line import get_cmd_task_opts
from config import config
from constant import class_name, window_title
from mouse_reset import mouse_reset
from pynput.keyboard import Key, Listener
from schema import Task
from status import logger
from task import sponser_task
from utils import *


def set_console_title(title: str):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


set_console_title(
    f"FC自动工具ver {version.__version__}   ---SurpassIllusions"
)

def run(task: Task, e: Event):
    """
    运行
    :return:
    """
    logger("任务进程开始运行")
    logger("请将鼠标移出游戏窗口，避免干扰脚本运行")
    if e.is_set():
        logger("任务进程已经在运行，不需要再次启动")
        return
    e.set()

    while e.is_set():
        img = screenshot()
        result = ocr(img)
        task(img, result)
    logger("进程停止运行")


def on_press(key):
    """
    F5 启动赞助商脚本
    F12 停止脚本
    :param key:
    :return:
    """
    if key == Key.f5:
        logger("启动赞助商脚本")
        thread = Process(target=run, args=(sponser_task, taskEvent), name="task")
        thread.start()
    if key == Key.f12:
        logger("请等待程序退出后再关闭窗口...")
        taskEvent.clear()
        mouseResetEvent.set()
        return False
    return None


# 执行命令行启动任务，
# TODO: 多个将异步顺序执行
def run_cmd_tasks_async():
    cmd_task_dict = get_cmd_task_opts()
    if cmd_task_dict is None:
        return
    cmd_keys = ""
    for key_str, keyboard in cmd_task_dict.items():
        cmd_keys += key_str if len(cmd_keys) == 0 else ", " + key_str
    logger("依次执行命令: " + cmd_keys)
    if len(cmd_task_dict) == 1:
        for key_str, keyboard in cmd_task_dict.items():
            on_press(keyboard)
        return
    # 异步 todo F12中断线程
    cmd_task_thread = threading.Thread(target=cmd_task_func, args=(cmd_task_dict,))
    cmd_task_thread.daemon = True
    cmd_task_thread.start()


def cmd_task_func(cmd_task_dict: OrderedDict[str, Key]):
    # print(str(cmd_task_dict))
    for key_str, keyboard in cmd_task_dict.items():
        on_press(keyboard)
        break


# TODO: UI
if __name__ == "__main__":
    taskEvent = Event()  # 用于停止任务线程
    mouseResetEvent = Event()  # 用于停止鼠标重置线程
    mouse_reset_thread = Process(
        target=mouse_reset, args=(mouseResetEvent,), name="mouse_reset"
    )
    mouse_reset_thread.start()

    logger(f"version: {version.__version__}")
    logger("鼠标重置进程启动")
    print("请确认已经配置好了config.yaml文件\n")
    print(
        "使用说明：\n   F5  启动脚本\n   F12  停止运行"
    )
    logger("开始运行")
    run_cmd_tasks_async()
    with Listener(on_press=on_press) as listener:
        listener.join()
    print("结束运行")

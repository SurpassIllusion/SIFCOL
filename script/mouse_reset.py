
import math
import time
from threading import Event

from pynput.mouse import Controller
from status import logger


def mouse_reset(e: Event):
    logger("鼠标重置进程启动成功")
    mouse = Controller()
    last_position = mouse.position
    while True:
        time.sleep(0.01)  # 0.01秒检测一次
        if e.is_set():
            break
        current_position = mouse.position
        distance = math.sqrt(
            (current_position[0] - last_position[0]) ** 2
            + (current_position[1] - last_position[1]) ** 2
        )
        if distance > 200:
            mouse.position = last_position
        else:
            last_position = current_position

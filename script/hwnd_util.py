import re

import psutil
import win32gui
import win32process

# 纯粹的窗口工具脚本，只可被其他脚本引用，不要在此引入其他自己写的包，
# 会带入各种全局变量和逻辑造成影响，也不要在这写逻辑（去utils.py写） by wakening
# from status import logger

# 窗口相关属性
fc_hwnd_class_name = "FIFAKC"
fc_hwnd_title = "FC ONLINE"


def get_pid_by_exe_name(exe_name: str):
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] == exe_name:
            pro_pid = proc.info['pid']
            # print(f"pid: {pro_pid}")
            return pro_pid
    return None


# 获取当前系统所有窗口句柄
def get_all_hwnd() -> list:
    def get_hwnd_callback(cb_hwnd, cb_window_list):
        # _, found_pid = win32process.GetWindowThreadProcessId(cb_hwnd)
        # print(f"found_pid: {found_pid}")
        cb_window_list.append(cb_hwnd)

    window_list: list = []
    win32gui.EnumWindows(get_hwnd_callback, window_list)
    return window_list


def get_hwnd_by_exe_name(exe_name: str) -> list | None:
    ge_pid = get_pid_by_exe_name(exe_name)
    if ge_pid is None:
        return None
    ge_hwnd_list: list = get_all_hwnd()
    rt_hwnd_list: list = []
    for ge_hwnd in ge_hwnd_list:
        _, found_pid = win32process.GetWindowThreadProcessId(ge_hwnd)
        if found_pid == ge_pid:
            rt_hwnd_list.append(ge_hwnd)
    return rt_hwnd_list


def get_hwnd_by_class_and_title(class_name: str, title: str):
    return win32gui.FindWindow(class_name, title)


# 获取fc游戏窗口句柄
def get_fc_hwnd():
    return get_hwnd_by_class_and_title(fc_hwnd_class_name, fc_hwnd_title)

import itertools
import os
import re
import time
from ctypes import windll
from datetime import datetime
from typing import List, Tuple, Union

import cv2
import hwnd_util
import mss
import numpy as np
import win32con
import win32gui
import win32ui
from config import config
from constant import height_ratio, hwnd, real_h, real_w, root_path, width_ratio
from control import control
from ocr import ocr
from PIL import Image, ImageGrab
from schema import OcrResult, Position, match_template
from status import info, logger


def screenshot():
    """
    截取当前窗口的屏幕图像。

    通过调用Windows图形设备接口（GDI）和Python的win32gui、win32ui模块，
    本函数截取指定窗口的图像，并将其存储为numpy数组。

    返回值:
        - np.ndarray: 截图的numpy数组，格式为RGB（不包含alpha通道）。
        - None: 如果截取屏幕失败，则返回None。
    """
    hwndDC = win32gui.GetDC(hwnd)  # 获取窗口设备上下文（DC）
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 创建MFC DC从hwndDC
    saveDC = mfcDC.CreateCompatibleDC()  # 创建与mfcDC兼容的DC
    saveBitMap = win32ui.CreateBitmap()  # 创建一个位图对象
    saveBitMap.CreateCompatibleBitmap(mfcDC, real_w, real_h)  # 创建与mfcDC兼容的位图
    saveDC.SelectObject(saveBitMap)  # 选择saveDC的位图对象，准备绘图

    # 尝试使用PrintWindow函数截取窗口图像
    saveDC.BitBlt((0, 0), (real_w, real_h), mfcDC, (0, 0), win32con.SRCCOPY)
    #TODO: 最小化
    """
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    if result != 1:
        config.RebootCount += 1
        logger(
            "截取游戏窗口失败，请勿最小化窗口，已重试："
            + str(config.RebootCount)
            + "次",
            "ERROR",
        )
        # 释放所有资源
        try:
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            del hwndDC, mfcDC, saveDC, saveBitMap
        except Exception as e:
            logger(f"清理截图资源失败: {e}", "ERROR")
        # 重试，若失败多次重新启动游戏以唤醒至前台
        if config.RebootCount < 3:
            time.sleep(1)
            return screenshot()  # 截取失败，重试
        else:
            config.RebootCount = 0
            logger("正在重新启动游戏及脚本...", "INFO")
            from main import close_window

            close_window()
            raise Exception(
                "截取游戏窗口失败且重试次数超过上限，正在重启游戏"
            ) from None
    """
    # 从位图中获取图像数据
    bmp_info = saveBitMap.GetInfo()  # 获取位图信息
    bmp_str = saveBitMap.GetBitmapBits(True)  # 获取位图数据
    im = np.frombuffer(bmp_str, dtype="uint8")  # 将位图数据转换为numpy数组
    im.shape = (bmp_info["bmHeight"], bmp_info["bmWidth"], 4)  # 设置数组形状
    # 调整通道顺序 并 去除alpha通道
    im = im[:, :, [2, 1, 0, 3]][:, :, :3]

    # 清理资源
    try:
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
    except Exception as e:
        logger(f"清理截图资源失败: {e}", "ERROR")
    return im  # 返回截取到的图像


def save_screenshot(image_array, file_path="screenshot.png"):
    """
    保存截图到文件
    :param image_array: np.ndarray, 截取的图像
    :param file_path: str, 图片保存路径，默认保存为 "screenshot.png"
    """
    if image_array is not None:
        # 使用 OpenCV 保存（默认 BGR 需要转换为 RGB）
        cv2.imwrite(file_path, cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
        print(f"截图已保存: {file_path}")
    else:
        print("截图失败，未能保存")


def random_click(
    x: int = None,
    y: int = None,
    range_x: int = 3,
    range_y: int = 3,
    ratio: bool = True,
    need_print: bool = False,
):
    """
    在以 (x, y) 为中心的区域内随机选择一个点并模拟点击。

    :param x: 中心点的 x 坐标
    :param y: 中心点的 y 坐标
    :param range_x: 水平方向随机偏移的范围
    :param range_y: 垂直方向随机偏移的范围
    :param ratio: 是否将坐标进行缩放
    :param need_print: 是否输出log，debug用
    """
    if x is None or y is None:
        logger("没有传入坐标，无法点击", "WARN")
    else:
        random_x = x + np.random.uniform(-range_x, range_x)
        random_y = y + np.random.uniform(-range_y, range_y)

        # 将浮点数坐标转换为整数像素坐标
        if ratio:
            # 需要缩放
            random_x = int(random_x) * width_ratio
            random_y = int(random_y) * height_ratio
        else:
            # 不需要缩放
            random_x = int(random_x)
            random_y = int(random_y)

        # 点击
        time.sleep(np.random.uniform(0, 0.1))  # 随机等待后点击
        control.click(random_x, random_y)

        if need_print:
            logger(f"点击了坐标{random_x},{random_y}", "DEBUG")
        # logger(f"点击了坐标{random_x},{random_y}")


def click_position(position: Position):
    """
    点击位置
    :param position: 需要点击的位置
    """
    # 分析position的中点
    x = (position.x1 + position.x2) // 2
    y = (position.y1 + position.y2) // 2
    # control.click(x, y)
    random_click(x, y, ratio=False)  # 找图所得坐标不需要缩放！


def find_pic(
    x_upper_left: int = None,
    y_upper_left: int = None,
    x_lower_right: int = None,
    y_lower_right: int = None,
    template_name: str = None,
    threshold: float = 0.8,
    img: np.ndarray = None,
    need_resize: bool = True,
):
    if img is None:
        img = screenshot()
    region = None
    if None not in (x_upper_left, y_upper_left, x_lower_right, y_lower_right):
        region = set_region(x_upper_left, y_upper_left, x_lower_right, y_lower_right)
    template = Image.open(os.path.join(root_path, "template", template_name))
    template = np.array(template)
    result = match_template(img, template, region, threshold, need_resize)
    return result


def adapts():
    adapts_type = info.adaptsType

    def calculate_distance(w1, h1, w2, h2):
        return ((w1 - w2) ** 2 + (h1 - h2) ** 2) ** 0.5

    if adapts_type is None:
        if 1910 <= real_w <= 1930 and 1070 <= real_h <= 1090:  # 判断适配1920*1080
            logger("分辨率正确，使用原生坐标")
            info.adaptsType = 1
            info.adaptsResolution = "_1920_1080"
        elif 1590 <= real_w <= 1610 and 890 <= real_h <= 910:  # 判断适配1600*900
            logger("分辨率正确，使用适配坐标")
            info.adaptsType = 2
            info.adaptsResolution = "_1600_900"
        # elif 1430 <= real_w <= 1450 and 890 <= real_h <= 910: # template比例实际与1600*900相同但region需要重设(ArcS17)
        #     logger("分辨率正确，使用通用坐标")
        #     info.adaptsType = 2
        #     info.adaptsResolution = "_1600_900"
        elif 1360 <= real_w <= 1380 and 750 <= real_h <= 790:  # 判断适配1366*768
            logger("分辨率正确，使用适配坐标")
            info.adaptsType = 3
            info.adaptsResolution = "_1366_768"
        elif 1270 <= real_w <= 1290 and 710 <= real_h <= 730:  # 判断适配1280*720
            logger("分辨率正确，使用适配坐标")
            info.adaptsType = 4
            info.adaptsResolution = "_1280_720"
        else:
            logger(
                "尝试使用相近分辨率，如有问题，请切换分辨率到 1920*1080*1.0 或者 1280*720*1.0",
                "WARN",
            )
            info.adaptsType = 5
        if info.adaptsType == 5:
            distance_1920_1080 = calculate_distance(real_w, real_h, 1920, 1080)
            distance_1600_900 = calculate_distance(real_w, real_h, 1600, 900)
            distance_1366_768 = calculate_distance(real_w, real_h, 1366, 768)
            distance_1280_720 = calculate_distance(real_w, real_h, 1280, 720)
            if distance_1920_1080 < distance_1600_900:
                info.adaptsType = 1
                info.adaptsResolution = "_1920_1080"
            elif distance_1600_900 < distance_1366_768:
                info.adaptsType = 2
                info.adaptsResolution = "_1600_900"
            elif distance_1366_768 < distance_1280_720:
                info.adaptsType = 3
                info.adaptsResolution = "_1366_768"
            else:
                info.adaptsType = 4
                info.adaptsResolution = "_1280_720"

cnt = 0
def find_sponsor():
    box_locs = [
        [[416, 261], [937, 464]],
        [[1103, 261], [1625, 464]],
        [[416, 475], [937, 677]],
        [[1103, 475], [1625, 677]],
        [[416, 687], [937, 889]],
        [[1103, 687], [1625, 889]],
    ]
    if not config.IsVIP:
        box_locs = box_locs[0:5]
    img = screenshot()
    global cnt
    cnt += 1
    oks = 0
    i = 0
    for box_loc in box_locs:
        i += 1
        accept = None
        x1 = int(box_loc[0][0] * width_ratio)
        y1 = int(box_loc[0][1] * height_ratio)
        x2 = int(box_loc[1][0] * width_ratio)
        y2 = int(box_loc[1][1] * height_ratio)
        box = img[
            y1:y2,
            x1:x2,
        ]
        # save_screenshot(box, f"test_pic/{cnt}_{i}.png")
        result = ocr(box)
        ok = True
        finished = False
        enough = False
        for item in result:
            if "接受" in item.text:
                ok = False
                accept = item
                continue
            if "/" in item.text:
                if item.text.split("/")[0] == item.text.split("/")[1]:
                    finished = True
        # 35 108 107 180 111 108 183 180
        img_sc = box[
            int(80 * width_ratio) : int(200 * width_ratio),
            int(0 * height_ratio) : int(130 * height_ratio),
        ]
        # save_screenshot(img_sc, f"test_pic/{cnt}_{i}_sc.png")
        img_tc = box[
            int(80 * width_ratio) : int(200 * width_ratio),
            int(107 * height_ratio) : int(237 * height_ratio),
        ]
        # save_screenshot(img_tc, f"test_pic/{cnt}_{i}_tc.png")
        sc = 0
        tc = 0
        result = ocr(img_sc)
        for item in result:
            try:
                sc = int(item.text)
            except:
                continue
        result = ocr(img_tc)
        for item in result:
            try:
                tc = int(item.text)
            except:
                continue
        if sc >= config.TargetSC and tc >= config.TargetSC:
            enough = True
        if ok:
            oks += 1
        elif finished and enough:
            logger(f"找到sc = {sc} tc = {tc} 的 第{i}个赞助商")
            # 分析position的中点
            x = x1 + (accept.position.x1 + accept.position.x2) // 2
            y = y1 + (accept.position.y1 + accept.position.y2) // 2
            # control.click(x, y)
            random_click(x, y, ratio=False)  # 找图所得坐标不需要缩放！
    return oks!=6


import logging
import os
import time
from multiprocessing import current_process

import numpy as np
import paddle
from config import config
from paddleocr import PaddleOCR
from schema import OcrResult, Position
from status import logger

ocrIns: PaddleOCR = None

if paddle.is_compiled_with_cuda() and paddle.get_device().startswith(
    "gpu"
):  # 判断是否调用GPU
    use_gpu = True
else:
    use_gpu = False
    os.environ['FLAGS_use_mkldnn'] = '1'  # CPU启用mkldnn加速

if current_process().name == "task":
    if use_gpu:
        logger("正在使用GPU加速，OCR初始化中...","DEBUG")
    else:
        logger("正在使用CPU，OCR初始化中...","DEBUG")
    logging.disable(logging.WARNING)  # 关闭WARNING日志的打印
    ocrIns = PaddleOCR(
        use_angle_cls=False,
        use_gpu=use_gpu,
        lang="ch",
        show_log=False,
        precision="int8",
    )

last_time = time.time()


def ocr(img: np.ndarray) -> list[OcrResult]:
    global last_time
    if (
        config.OcrInterval > 0 and time.time() - last_time < config.OcrInterval
    ):  # 限制OCR调用频率
        if wait_time := config.OcrInterval - (time.time() - last_time) > 0:
            time.sleep(wait_time)
    last_time = time.time()
    results = ocrIns.ocr(img)[0]
    # print(f"ocr当前扫描结果{results}") # ocr debug使用
    if not results:
        return []
    res = []
    for result in results:
        text = result[1][0]
        position = result[0]
        x1, y1, x2, y2 = position[0][0], position[0][1], position[2][0], position[2][1]
        position = Position(x1=x1, y1=y1, x2=x2, y2=y2)
        confidence = result[1][1]
        res.append(OcrResult(text=text, position=position, confidence=confidence))
    return res

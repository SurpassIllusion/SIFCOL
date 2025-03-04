# 赞助商脚本
from utils import find_sponsor

from . import *

pages = []


# 刷新
def find_finished_action(positions):
    """
    新增委托
    :param positions: 位置信息
    :return:
    """
    position = positions.get("新增委托")
    click_position(position)
    time.sleep(0.3)
    return find_sponsor()


find_finished_page = Page(
    name="赞助商",
    targetTexts=[
        TextMatch(
            name="新增委托",
            text="新增委托",
        ),
    ],
    action=find_finished_action,
)
pages.append(find_finished_page)

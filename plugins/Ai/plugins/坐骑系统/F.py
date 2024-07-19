import base64
import datetime

from plugins.Ai.llm import LLM
from plugins.Ai.module import User
from plugins.Ai.api import ComfyUI
from plugins.Ai.plugins.坐骑系统.坐骑 import Mount
import random

__PROMPT__ = """坐骑名字可以借鉴:火麒麟、朱雀、炎魔、精灵龙、奇美拉、草泥马、羊驼、猪猪侠
设计一个坐骑并遵循以下格式回复，请不要回复格式以外的任何信息：
name:{name}
prompt:(英文外观描述，尽可能详细描述包括形态、动作、背景)"""


def __random__(
        rule: tuple[
            tuple[
                int,  # 概率(0-10000)
                int,  # 最小值
                int,  # 最大值
            ], ...
        ]
):
    """
    随机数生成
    :param rule: 概率规则
    :return: 随机数
    """
    r = random.randint(0, 10000)
    for i in rule:
        if r < i[0]:
            return random.randint(i[1], i[2])
        r -= i[0]
    return random.randint(0, 10000)


async def get_new_mount(user: User):
    # 获取坐骑对象
    mount = Mount()
    # 生成坐骑信息
    data = await LLM.ainvoke(__PROMPT__.format(name='(中文名)'))
    # 解析坐骑信息
    data = data.split('\n')
    try:
        name = data[0].split(':')[1].strip()
        prompt = data[1].split(':')[1].strip()
    except IndexError:
        return await get_new_mount(user)
    mount.name = name
    mount.prompt = prompt
    mount.owner = user.nickname
    mount.owner_id = user.qq
    attr = {
        'hp': [
            __random__(
                (
                    (1, 2000, __random__(
                        (
                            (1, 10000, 50000),  # 0.01%
                            (9, 6000, 10000),  # 0.09%
                            (90, 4000, 6000),  # 0.9%
                            (900, 3000, 4000),  # 9%
                            (3000, 2500, 3000),  # 30%
                            (6000, 2000, 2500),  # 60%
                        )
                    )),
                    (9, 1000, 2000),  # 0.09%
                    (90, 500, 1000),  # 0.9%
                    (900, 200, 500),  # 9%
                    (3000, 100, 200),  # 30%
                    (6000, 20, 100),  # 60%
                )
            ),  # 生命值
            __random__(
                (
                    (1, 200, __random__(
                        (
                            (1, 1000, 5000),  # 0.01%
                            (9, 600, 1000),  # 0.09%
                            (90, 400, 600),  # 0.9%
                            (900, 300, 400),  # 9%
                            (3000, 250, 300),  # 30%
                            (6000, 200, 250),  # 60%
                        )
                    )),
                    (9, 100, 200),  # 0.09%
                    (90, 50, 100),  # 0.9%
                    (900, 20, 50),  # 9%
                    (3000, 10, 20),  # 30%
                    (6000, 2, 10),  # 60%
                )
            ),  # 生命增长
        ],
        'atk': [
            __random__(
                (
                    (1, 200, __random__(
                        (
                            (1, 1000, 5000),  # 0.01%
                            (9, 600, 1000),  # 0.09%
                            (90, 400, 600),  # 0.9%
                            (900, 300, 400),  # 9%
                            (3000, 250, 300),  # 30%
                            (6000, 200, 250),  # 60%
                        )
                    )),
                    (9, 100, 200),  # 0.09%
                    (90, 50, 100),  # 0.9%
                    (900, 20, 50),  # 9%
                    (3000, 10, 20),  # 30%
                    (6000, 2, 10),  # 60%
                )
            ),  # 攻击力
            __random__(
                (
                    (1, 20, __random__(
                        (
                            (1, 100, 500),  # 0.01%
                            (9, 60, 100),  # 0.09%
                            (90, 40, 60),  # 0.9%
                            (900, 30, 40),  # 9%
                            (3000, 25, 30),  # 30%
                            (6000, 20, 25),  # 60%
                        )
                    )),
                    (9, 10, 20),  # 0.09%
                    (90, 5, 10),  # 0.9%
                    (900, 2, 5),  # 9%
                    (3000, 1, 2),  # 30%
                    (6000, 1, 1),  # 60%
                )
            ),  # 攻击力增长
        ],
        'def': [
            __random__(
                (
                    (1, 100, __random__(
                        (
                            (1, 750, 1000),  # 0.01%
                            (9, 500, 750),  # 0.09%
                            (90, 300, 500),  # 0.9%
                            (900, 200, 300),  # 9%
                            (3000, 150, 200),  # 30%
                            (6000, 100, 150),  # 60%
                        )
                    )),
                    (9, 50, 100),  # 0.1%
                    (90, 25, 50),  # 0.9%
                    (900, 10, 25),  # 9%
                    (3000, 5, 10),  # 30%
                    (6000, 1, 5),  # 60%
                )
            ),  # 防御力
            __random__(
                (
                    (1, 10, __random__(
                        (
                            (1, 75, 100),  # 0.01%
                            (9, 50, 75),  # 0.09%
                            (90, 30, 50),  # 0.9%
                            (900, 20, 30),  # 9%
                            (3000, 15, 20),  # 30%
                            (6000, 10, 15),  # 60%
                        )
                    )),
                    (9, 5, 10),  # 0.09%
                    (90, 3, 5),  # 0.9%
                    (900, 2, 3),  # 9%
                    (3000, 1, 2),  # 30%
                    (6000, 1, 1),  # 60%
                )
            ),  # 防御力增长
        ],
        'sign_in_c': [
            __random__(
                (
                    (1, 1000, __random__(
                        (
                            (1, 7500, 10000),  # 0.01%
                            (9, 5000, 7500),  # 0.09%
                            (90, 3000, 5000),  # 0.9%
                            (900, 2000, 3000),  # 9%
                            (3000, 1500, 2000),  # 30%
                            (6000, 1000, 1500),  # 60%
                        )
                    )),
                    (9, 500, 1000),  # 0.09%
                    (90, 100, 500),  # 0.9%
                    (900, 50, 100),  # 9%
                    (3000, 20, 50),  # 30%
                    (6000, 1, 20),  # 60%
                )
            ),  # 角色签到积分加成
        ]
    }
    attr['hp'].append(attr['hp'][0])
    mount.attributes = str(attr)
    mount.level = 1
    mount.exp = 0
    # 生成坐骑图片
    mount.img = None
    while not mount.img:
        api = ComfyUI()
        mount.img = base64.b64encode((await api.auto_draw(prompt=mount.prompt, size=(512, 512)))).decode()
    mount.created_at = datetime.datetime.now()
    mount.update()
    user.mount_id = Mount().find(owner_id=user.qq).id
    user.update()
    return mount

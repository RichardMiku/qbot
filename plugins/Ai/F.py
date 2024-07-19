from nonebot.adapters.satori.event import *
from plugins.Ai.module import Object as OBD
from plugins.Ai.object.道具商店物品 import *
from plugins.Ai.object.精灵商店物品 import *
from plugins.Ai.object.坐骑商店物品 import *
from plugins.Ai.object.农贸市场物品 import *

import time


def is_group_message(event: Event):
    return event.__dict__.get('guild') is not None


def get_group_id(event: Event):
    guild = event.__dict__.get('guild')
    if guild:
        return guild.id
    return None


def is_private_message(event: Event):
    return event.__dict__.get('guild') is None


def get_object(name: str):
    obj = OBD().find(name=name)
    if not obj:
        return None
    obj = globals()[obj.name]
    return obj()


def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher
from plugins.Ai.module import *
from plugins.Ai.F import is_group_message


def info(ch: Matcher, bot: Bot, event: Event):
    user = User(event)
    return ((MessageSegment.at(user.qq) + '\n') if is_group_message(event) else '') + user.info()


async def main(ch: Matcher, bot: Bot, event: Event):
    msg = event.get_plaintext()
    if msg == '个人信息':
        await ch.finish(info(ch, bot, event))

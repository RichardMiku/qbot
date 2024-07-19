from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher
from plugins.Ai.module import *
from plugins.Ai.F import is_group_message


def menu(ch: Matcher, bot: Bot, event: Event, menu: str):
    if menu == '娱乐菜单':
        pass
    elif menu == '游戏菜单':
        pass
    return ""


async def main(ch: Matcher, bot: Bot, event: Event):
    msg = event.get_plaintext()
    if msg == '娱乐菜单':
        await ch.finish(menu(ch, bot, event, '娱乐菜单'))
    elif msg == '游戏菜单':
        await ch.finish(menu(ch, bot, event, '游戏菜单'))

import asyncio
import os.path

from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *

from plugins.Ai.F import get_group_id, is_group_message
from plugins.Ai.llm.tools import agent
from plugins.Ai.module import *
from plugins.Ai.plugins import 个人信息, 智慧山商, 每日签到, 背包管理, 道具商店, 煤炭社互动, 游戏娱乐, 功能尝新, 塔罗牌, \
    坐骑系统, 农场系统, 实用工具
from plugins.Ai.llm.tools import main as llm_main

ch = on_message()

__ALL_PLUGINS__ = [x for x in os.listdir(os.path.join(os.path.dirname(__file__), 'plugins')) if not x.startswith('_')]
dev_mode = os.getenv('ENVIRONMENT') == 'dev'
dev_group = str(os.getenv('DEV_GROUP', ''))


async def menu(ch, bot: Bot, event: Event):
    if event.get_plaintext() != '菜单':
        return
    msg = '-⭐- 🚀 - 菜单 - 🚀 -⭐-\n\n'
    msg += " 🚀每日签到 🏆个人信息\n\n"
    msg += " 🏫智慧山商 🏭道具商店\n\n"
    msg += " 🦄坐骑系统 🥕农场系统\n\n"
    msg += " 🖥️机房助手 🔧实用工具\n\n"
    msg += " 🚧正在施工 🎊功能尝新\n\n"
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    await ch.finish(msg)


@ch.handle()
async def _(bot: Bot, event: Event):
    if dev_mode and get_group_id(event) != dev_group:
        return
    if not is_group_message(event) or event.get_user_id() == bot.self_id:
        return
    task = [eval(x).main(ch, bot, event) for x in __ALL_PLUGINS__]
    task.append(menu(ch, bot, event))
    await asyncio.gather(*task)
    await llm_main(ch, bot, event)

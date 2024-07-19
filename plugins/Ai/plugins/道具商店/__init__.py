from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher
from plugins.Ai.module import Object as OBD
from plugins.Ai.F import get_object
from plugins.Ai.object import Object


async def menu(ch, bot, event):
    db = OBD().find_all(owner='道具商店')
    msg = MessageSegment.text('-⭐-🚀 道具商店 🚀-⭐-\n\n')
    for i in db:
        i: Object = get_object(i.name)
        msg += MessageSegment.text(f'{i.logo} 【 {i.name} 】')
        if i.data['price']['c']:
            msg += MessageSegment.text(f'🎖️{i.data["price"]["c"]} ')
        if i.data['price']['b']:
            msg += MessageSegment.text(f'💰{i.data["price"]["b"]} ')
        if i.data['price']['r']:
            msg += MessageSegment.text(f'💎{i.data["price"]["r"]} ')
        msg += MessageSegment.text(f'\n{i.description}\n\n')
    msg += MessageSegment.text('-⭐- 🚀 山商AI 🚀 -⭐-')
    await ch.finish(msg)


async def main(ch, bot: Bot, event: Event):
    msg = event.get_plaintext()
    if msg == '道具商店':
        await ch.finish(await menu(ch, bot, event))

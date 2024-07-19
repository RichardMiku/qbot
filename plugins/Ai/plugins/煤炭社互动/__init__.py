from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *

from plugins.Ai.F import get_group_id, is_group_message
from plugins.Ai.llm import LLM
from plugins.Ai.module import User


async def main(ch, bot: Bot, event: Event):
    if not is_group_message(event):
        return
    group_id = get_group_id(event)
    if group_id != '739607411':
        return
    user = User(event)
    if user.qq != '1038722541':
        return
    msg: str = event.get_plaintext().strip()
    if not msg.startswith('今日人品'):
        return
    to_user = User(event.get_message()[0])
    scores = int(msg[5:].split('，')[0])
    msg: MessageSegment = MessageSegment.at(to_user.qq)
    if scores < 80:
        msg += MessageSegment.text(LLM('写一句富有激情逆天改命的话，例如:骚年！你想逆天改命吗？'))
    else:
        msg += MessageSegment.text(LLM('写一句十分羡慕的话，例如:你这人品简直不要太逆天！'))
    await ch.finish(msg)
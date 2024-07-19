import base64

from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher

from plugins.Ai.llm import LLM
from plugins.Ai.module import Object as OBD
from plugins.Ai.F import get_object
from plugins.Ai.object import Object
from plugins.Ai.plugins.坐骑系统.F import get_new_mount
from plugins.Ai.module import User
from plugins.Ai.plugins.坐骑系统.坐骑 import Mount


async def 我的坐骑(ch, bot, event):
    # 检查用户是否已存在坐骑
    user = User(event)
    if user.mount_id < 0:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你还没有坐骑哦！可以通过【 领养坐骑 】领取坐骑')
        return msg
    # 获取坐骑信息
    mount = Mount().find(id=user.mount_id)
    msg = MessageSegment.at(user.qq)
    msg += MessageSegment.text(' -> 你的坐骑信息如下：\n')
    msg += await mount.info()
    return msg


async def 领养坐骑(ch, bot, event):
    # 检查用户是否已存在坐骑
    user = User(event)
    if user.mount_id > 0:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 贪得无厌的家伙，你已经有坐骑了！')
        return msg
    elif user.mount_id == 0:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 正在处理您的坐骑手续，请稍后...')
        return msg
    # 标记为正在领养
    user.mount_id = 0
    user.update()
    # 提示
    msg = MessageSegment.at(user.qq)
    msg += MessageSegment.text(' -> 正在为您匹配新坐骑！请稍后...')
    await ch.send(msg)
    # 获取新坐骑
    mount = await get_new_mount(user)
    # 返回信息
    msg = MessageSegment.at(user.qq)
    msg += MessageSegment.text(' 恭喜您，成功领养到新坐骑！')
    msg += await mount.info()
    return msg


async def 坐骑大图(ch, bot, event):
    # 检查用户是否已存在坐骑
    user = User(event)
    if user.mount_id < 0:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你还没有坐骑哦！可以通过【 领养坐骑 】领取坐骑')
        return msg
    # 获取坐骑信息
    mount = Mount().find(id=user.mount_id)
    return MessageSegment.image(raw=base64.b64decode(mount.img.encode()), mime='image/png')


async def menu(ch, bot, event):
    msg = MessageSegment.text('-⭐-🚀 坐骑商店 🚀-⭐-\n\n')
    msg += MessageSegment.text('-⭐- 🚀 山商AI 🚀 -⭐-')
    await ch.finish(msg)


async def 坐骑系统(ch, bot, event):
    msg = MessageSegment.text('-⭐-🚀 坐骑系统 🚀-⭐-\n\n')
    msg += MessageSegment.text('🍄【 领养坐骑 】\n')
    msg += MessageSegment.text('领养坐骑可获得坐骑信息\n\n')

    msg += MessageSegment.text('🐲【 我的坐骑 】\n')
    msg += MessageSegment.text('查看自己的坐骑信息\n\n')

    msg += MessageSegment.text('🗺️【 坐骑大图 】\n')
    msg += MessageSegment.text('查看自己的坐骑高清图\n\n')

    msg += MessageSegment.text('💔【 坐骑放生 】 🎖️50\n')
    msg += MessageSegment.text('放生你的坐骑！（ 请谨慎操作 ）\n\n')

    msg += MessageSegment.text('⚠️注意：坐骑系统各种功能正在逐步开发中，敬请期待！\n\n')

    msg += MessageSegment.text('-⭐- 🚀 山商AI 🚀 -⭐-')
    await ch.finish(msg)


async def 坐骑放生(ch, bot, event):
    # 获取用户对象
    user = User(event)
    # 检查用户是否已存在坐骑
    if user.mount_id < 0:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你还没有坐骑哦！可以通过【 领养坐骑 】领取坐骑')
        return msg
    # 检查是否有足够的积分
    if user.c < 50:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你的🎖️积分不足50，无法放生坐骑！')
        return msg
    # 扣除积分
    user.c -= 50
    user.update()
    # 放生坐骑
    msg = MessageSegment.text('-⭐-🚀 坐骑放生 🚀-⭐-\n\n')
    msg += MessageSegment.text('🚨你狠心的放生了你的坐骑，你的坐骑留下了一句话：\n')
    msg += MessageSegment.text(f"{await LLM.ainvoke('你现在扮演一个坐骑，而你现在要被你的主人放生了，使用中文说一句挽留的话')}")
    msg += MessageSegment.text('\n\n-⭐- 🚀 山商AI 🚀 -⭐-')
    # 更新用户坐骑信息
    user.mount_id = -1
    user.update()
    return msg


async def main(ch, bot: Bot, event: Event):
    msg = event.get_plaintext()
    if msg == '坐骑系统':
        await ch.finish(await 坐骑系统(ch, bot, event))
    elif msg == '坐骑商店':
        await ch.finish(await menu(ch, bot, event))
    elif msg == '领养坐骑':
        await ch.finish(await 领养坐骑(ch, bot, event))
    elif msg == '我的坐骑':
        await ch.finish(await 我的坐骑(ch, bot, event))
    elif msg == '坐骑大图':
        await ch.finish(await 坐骑大图(ch, bot, event))
    elif msg == '坐骑放生':
        await ch.finish(await 坐骑放生(ch, bot, event))

from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher
from plugins.Ai.module import *
from plugins.Ai.F import is_group_message
from plugins.Ai.api import ComfyUI


async def AI绘图(ch: Matcher, bot: Bot, event: Event, cmd: list):
    # 检查指令是否正确
    if len(cmd) < 1:
        return MessageSegment.text('请提供描述！')
    # 检查积分是否足够
    user = User(event)
    if user.c < 1:
        return MessageSegment.at(user.qq) + MessageSegment.text(' 您的积分不足！')
    # 构造
    msg = MessageSegment.text('-⭐-🚀 AI绘图 🚀-⭐-\n\n')
    msg += MessageSegment.text('正在为【 ')
    msg += MessageSegment.at(user.qq)
    msg += MessageSegment.text(' 】处理绘图请求，请稍等片刻~')
    msg += MessageSegment.text('\n\n-⭐- 🚀 山商AI 🚀 -⭐-')
    # 处理请求
    await ch.send(msg)
    # 调用API
    api = ComfyUI()
    img = await api.auto_draw(''.join(cmd))
    # 扣除积分
    user.c -= 1
    user.update()
    # @提示
    msg = MessageSegment.text('-⭐-🚀 AI绘图 🚀-⭐-\n\n')
    msg += MessageSegment.text('已处理完【 ')
    msg += MessageSegment.at(user.qq)
    msg += MessageSegment.text(' 】的绘图请求，请查收')
    msg += MessageSegment.text('\n\n-⭐- 🚀 山商AI 🚀 -⭐-')
    # 发送消息
    await ch.send(msg)
    # 返回结果
    msg = MessageSegment.image(raw=img, mime='image/png')
    return msg


def menu(ch: Matcher, bot: Bot, event: Event):
    msg = '-⭐-🚀 功能尝新 🚀-⭐-\n\n'
    msg += '说明：\n'
    msg += '1. 功能尝新验是一个测试功能，可能会有不稳定的情况\n'
    msg += '2. 功能尝新可能会在正式版本中删除或修改\n'
    msg += '3. 请不要在正式场合使用，如造成后果请自负\n\n'
    msg += '🖼️【 AI绘图 】 🎖️1\n'
    msg += '📦使用指令：【 AI绘图 描述 】\n'
    msg += '📢已知问题：显存不够时无法正常输出图像以及模型不稳定\n\n'
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


async def main(ch: Matcher, bot: Bot, event: Event):
    msg = event.get_plaintext()
    if msg == '功能尝新':
        await ch.finish(menu(ch, bot, event))
    try:
        cmd = msg.split(' ')
    except Exception:
        return
    if cmd[0] == 'AI绘图':
        try:
            await ch.finish(await AI绘图(ch, bot, event, cmd[1:]))
        except IndexError:
            user = User(event)
            user.c += 1
            user.update()
            await ch.finish(MessageSegment.at(user.qq) + MessageSegment.text('绘图出问题了，积分已返还~'))

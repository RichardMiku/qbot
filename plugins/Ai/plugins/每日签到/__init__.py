from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher
from plugins.Ai.module import *
from plugins.Ai.F import is_group_message
from plugins.Ai.api import get_hitokoto


def sign_in_today() -> list:
    user = User()
    return list(user.execute_fetchall(
        f"""
        select * from user
        where date(last_sign_time) = curdate()
        order by last_sign_time
        """
    ))


def sign_in_today_num() -> int:
    """
    签到人数
    """
    return len(sign_in_today())


def sign_in(ch: Matcher, bot: Bot, event: Event):
    """
    签到
    """
    user = User(event)
    # 检查上次签到时间
    if datetime.datetime.now().date() == user.last_sign_time.date():
        return '今日已签到！'
    # 记录签到时间
    user.last_sign_time = datetime.datetime.now()
    # 记录签到次数
    user.sign_times += 1
    # 计算签到排名
    ranking = sign_in_today_num() + 1
    # 记录当前等级
    level = user.level
    # 获得签到奖励
    user.c += (c := random.randint(user.vip, user.level * user.vip) + 1)
    user.b += (b := max(0, 4 - ranking))
    user.r += (r := 1 if ranking == 1 else 0)
    # 坐骑签到额外奖励
    mc = 0
    mount = Mount().find(id=user.mount_id)
    if mount:
        mc = max(int(c * (1 + eval(mount.attributes)['sign_in_c'][0] / 100)), 1)
        user.c += mc
    # 经验奖励
    user.add_exp(e := random.randint(5, 20 * (user.vip + 1) + ((21 - ranking) if ranking <= 10 else 0)))
    # 返回界面
    msg = MessageSegment.at(user.qq) if is_group_message(event) else ''
    msg += MessageSegment.text(' -> 签到成功! \n')
    msg += MessageSegment.image(user.get_img())
    msg += MessageSegment.text(f'\n☀️ 用户昵称：{user.nickname}')
    msg += MessageSegment.text(f'\n👑 会员等级：{user.vip}级' if user.vip else '')
    msg += MessageSegment.text(f'\n🏆 当前等级：{level} -> {user.level}' if level != user.level else f'\n🏆 当前等级：{user.level}')
    msg += MessageSegment.text(f'\n✨️ 当前经验：{user.exp} ( + {e} )')
    msg += MessageSegment.text(f'\n🎖️ 当前积分：{user.c} ( + {c} {f"+ {mc}" if mc else ""} )')
    msg += MessageSegment.text(f'\n💰 当前金币：{user.b} ( + {b} )')
    msg += MessageSegment.text(f'\n💎 当前钻石：{user.r} ( + {r} )')
    msg += MessageSegment.text(f'\n📅 累计签到：{user.sign_times} 次')
    msg += MessageSegment.text(f'\n🚥 签到排名：第 {ranking} 名')
    msg += MessageSegment.text(f'\n\n{get_hitokoto()}')
    return msg


def sign_in_rank(ch: Matcher, bot: Bot, event: Event):
    """
    签到排行榜
    """
    ranking = sign_in_today()
    msg = '-⭐- 🚀 签到排行榜 🚀 -⭐-\n\n'
    for i, x in enumerate(ranking):
        v = x[2]
        if i == 0:
            msg += f'【 第 1 名 】🥇 {v}\n\n'
        elif i == 1:
            msg += f'【 第 2 名 】🥈 {v}\n\n'
        elif i == 2:
            msg += f'【 第 3 名 】🥉 {v}\n\n'
        elif i < 10:
            msg += f'【 第 {i + 1} 名 】 {v}\n\n'
        else:
            break
    msg += '排行榜只会显示当天前十名\n'
    msg += '前十名可以获得额外的奖励\n\n'
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


def menu(ch: Matcher, bot: Bot, event: Event):
    """
    目录
    """
    msg = '\n-⭐-🚀 每日签到 🚀-⭐-\n\n'
    msg += '🗒️【 签到 】\n'
    msg += '每日签到可领取积分、经验\n\n'
    msg += '📊【 签到排行榜 】\n'
    msg += '查看签到排行榜\n\n'
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


async def main(ch, bot: Bot, event: Event):
    msg = event.get_plaintext()
    if msg == '每日签到':
        await ch.finish(menu(ch, bot, event))
    elif msg == '签到':
        await ch.finish(sign_in(ch, bot, event))
    elif msg == '签到排行榜':
        await ch.finish(sign_in_rank(ch, bot, event))

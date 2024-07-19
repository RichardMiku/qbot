import httpx
from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher

from plugins.Ai.llm import LLM
from plugins.Ai.module import *

ZHSS_API_BASE = os.getenv('ZHSS_API_BASE')


def bind(ch: Matcher, bot: Bot, event: Event):
    """
    绑定智慧山商
    """
    cmd = event.get_plaintext().split(' ', 3)
    if len(cmd) != 4:
        return '参数错误！【智慧山商 绑定 用户名 密码】'
    user = User(event)
    if user.zhss_bind(cmd[2], cmd[3]):
        return '绑定成功！'
    return '绑定时间未超过24小时，无法再次绑定！'


def unbind(ch: Matcher, bot: Bot, event: Event):
    """
    解绑智慧山商
    """
    user = User(event)
    user.zhss_unbind()
    return '解绑成功！'


def menu():
    """
    目录
    """
    msg = '\n-⭐-🚀 智慧山商 🚀-⭐-\n\n'
    msg += ' 🧾我的课表 📖今日课表\n\n'
    msg += ' 🧑‍🏫教师评价 📚完成教评\n\n'
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


def help(ch: Matcher, bot: Bot, event: Event):
    """
    帮助信息
    """
    msg = '\n-⭐-🚀 智慧山商 🚀-⭐-'
    msg += '\n\n🚀【 智慧山商 绑定 用户名 密码 】'
    msg += '\n绑定智慧山商，24小时内无法重复绑定'
    msg += '\n\n🚀【 智慧山商 解绑 】'
    msg += '\n解绑智慧山商'
    msg += '\n\n-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


def score(ch: Matcher, bot: Bot, event: Event):
    """
    成绩查询
    """
    user = User(event)
    if not user.zhss_is_bind:
        return '未绑定智慧山商！请输入【智慧山商 绑定 用户名 密码】绑定智慧山商！'
    with httpx.Client() as client:
        r = client.post(f'{ZHSS_API_BASE}/exam_score', json={
            'username': user.zhss_username,
            'password': user.zhss_password
        }).json()
    if r['code'] != 200:
        user.zhss_unbind()
        return '账号或密码错误！'
    msg = '\n-⭐-🚀 成绩查询 🚀-⭐-\n\n'
    for i in r['data']:
        try:
            msg += f"{'🟢' if float(i['课程分数']) >= 60 else '🔴'} "
        except Exception:
            msg += f"🟡"
        msg += f"【 {i['课程名称']} 】\n"
        msg += f"📖分数：「 {i['课程分数']} 」\n\n"
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


async def timetable(ch: Matcher, bot: Bot, event: Event, today: bool = False):
    """
    我的课表
    """
    user = User(event)
    if not user.zhss_is_bind:
        return '未绑定智慧山商！请输入【智慧山商 绑定 用户名 密码】绑定智慧山商！'
    async with httpx.AsyncClient() as client:
        r = (await client.post(f'{ZHSS_API_BASE}/class_schedule', json={
            'username': user.zhss_username,
            'password': user.zhss_password
        })).json()
        if r['code'] != 200:
            user.zhss_unbind()
            return '账号或密码错误！'
        try:
            if not user.name:
                d = await client.get(f'{ZHSS_API_BASE}/user_info', params={
                    'uid': user.zhss_username
                })
                if d.status_code == 200 and d.json().get('code') == 200:
                    user.name = d.json().get('data').get('姓名')
                    user.update()
        except AttributeError:
            d = await client.get(f'{ZHSS_API_BASE}/user_info', params={
                'uid': user.zhss_username
            })
            if d.status_code == 200 and d.json().get('code') == 200:
                user.name = d.json().get('姓名')
                user.update()
    msg = '\n-⭐-🚀 我的课表 🚀-⭐-\n\n'
    if not r['data']:
        msg += '今天放假了！\n\n'
        msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
        return msg
    time_table_start = ['7:50', '8:45', '9:50', '10:45', '14.30', '15:35', '16:30', '17:25', '19:10', '20:05']
    time_table_end = ['8:35', '9:30', '10:35', '11:30', '15:15', '16:20', '17:15', '18:10', '19:55', '20:50']
    if today:
        data = [x for x in r['data'] if x['上课星期'] == datetime.date.today().weekday() + 1]
        data = sorted(data, key=lambda x: x['起始时间'], reverse=False)
        if len(data) == 0:
            msg += f'{LLM("今天不需要上课，使用中文一句话描述你快乐的心情")}\n\n'
            msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
            return msg
    else:
        # 排序
        data = sorted(r['data'], key=lambda x: (x['上课星期'], x['起始时间']), reverse=False)
    last_weekday = -1
    for i in data:
        if not today and i['上课星期'] != last_weekday:
            last_weekday = i['上课星期']
            msg += f"= ⏰ =【 星期{'一二三四五六日'[last_weekday - 1]} 】= ⏰ =\n\n"
        msg += f"【 {i['课程名称']} 】\n"
        msg += f"🧑‍🏫教师：「 {i['教师姓名']} 」\n"
        msg += f"📖节次：「 第"
        msg += f"{i['起始时间']}" if i['起始时间'] == i['结束时间'] else f"{i['起始时间']}~{i['结束时间']}"
        msg += "节 」\n"
        msg += f"⏰时间：「 {time_table_start[int(i['起始时间']) - 1]}~{time_table_end[int(i['结束时间']) - 1]} 」\n"
        msg += f"📌地点：「 {i['上课地点']} 」\n\n"
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


async def teacher_review(ch, bot, event):
    user = User(event)
    if not user.zhss_is_bind:
        return '未绑定智慧山商！请输入【智慧山商 绑定 用户名 密码】绑定智慧山商！'
    async with httpx.AsyncClient() as client:
        r = (await client.post(f'{ZHSS_API_BASE}/student_reviews', json={
            'username': user.zhss_username,
            'password': user.zhss_password
        })).json()
        if r['code'] != 200:
            user.zhss_unbind()
            return '账号或密码错误！'
    flag = True
    msg = '\n-⭐-🚀 教师评价 🚀-⭐-\n\n'
    for i in r['data']:
        msg += f"【 {i['教师姓名']} 】 "
        if i['是否提交'] == '否':
            flag = False
            msg += f"🔴【 {i['教师姓名']} 】未评价\n"
        else:
            msg += f"🟢【 {i['教师姓名']} 】{i['总评分']} \n"
    if flag:
        msg += '\n所有教师已评价！\n\n'
    else:
        msg += '\n有教师未评价！你可以输入指令:\n'
        msg += '【 完成教评 】完成教师评价！\n\n'
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


async def finish_teacher_review(ch, bot, event):
    user = User(event)
    if not user.zhss_is_bind:
        return '未绑定智慧山商！请输入【智慧山商 绑定 用户名 密码】绑定智慧山商！'
    msg = '\n-⭐-🚀 完成教评 🚀-⭐-\n\n'
    msg += '正在评价中，请稍后...\n\n'
    msg += '中途使用【 教师评价 】查看会中断评价！\n\n'
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    await ch.send(msg)
    async with httpx.AsyncClient() as client:
        r = (await client.post(f'{ZHSS_API_BASE}/finish_student_reviews', json={
            'username': user.zhss_username,
            'password': user.zhss_password
        }, timeout=300)).json()
        if r['code'] != 200:
            user.zhss_unbind()
            return '账号或密码错误！'
    msg = '\n-⭐-🚀 完成教评 🚀-⭐-\n\n'
    if not r['data']:
        msg += '没有需要评价的课程！\n\n'
    else:
        msg += '评价成功！\n\n'
        msg += '评价教师：\n'
        for i in r['data']:
            msg += f"🧑‍🏫「 {i} 」\n"
    msg += '-⭐- 🚀 山商AI 🚀 -⭐-'
    return msg


async def main(ch: Matcher, bot: Bot, event: Event):
    msg = event.get_plaintext()
    if msg == '成绩查询':
        await ch.finish(score(ch, bot, event))
    elif msg == '我的课表':
        await ch.finish(await timetable(ch, bot, event, today=False))
    elif msg == '今日课表':
        await ch.finish(await timetable(ch, bot, event, today=True))
    elif msg == '教师评价':
        await ch.finish(await teacher_review(ch, bot, event))
    elif msg == '完成教评':
        await ch.finish(await finish_teacher_review(ch, bot, event))
    if not msg.startswith('智慧山商'):
        return
    if msg == '智慧山商':
        await ch.finish(menu())
    cmd = msg.split(' ')
    if cmd[1] == '帮助':
        await ch.finish(help(ch, bot, event))
    elif cmd[1] == '绑定':
        await ch.finish(bind(ch, bot, event))
    elif cmd[1] == '解绑':
        await ch.finish(unbind(ch, bot, event))

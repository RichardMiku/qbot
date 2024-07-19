import datetime
import uuid

from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher
from plugins.Ai.module import Object as OBD, Plant, Farm, BackPack
from plugins.Ai.F import get_object
from plugins.Ai.object import Object
from plugins.Ai.utility.backpack import get_user_backpack
from plugins.Ai.module import User
from plugins.Ai.plugins.农场系统.plant import ALL_PLANTS


async def menu(ch, bot, event):
    msg = MessageSegment.text('-⭐-🚀 农场系统 🚀-⭐-\n\n')
    msg += MessageSegment.text('🏪【 农场商店 】\n')
    msg += MessageSegment.text('📖 查看农场商店物品\n\n')
    msg += MessageSegment.text('🎒【 农场背包 】\n')
    msg += MessageSegment.text('📖 查看农场背包物品\n\n')
    msg += MessageSegment.text('🥝【 种植 (作物名) 】\n')
    msg += MessageSegment.text('📖 种植作物\n\n')
    msg += MessageSegment.text('🥕【 农场收获 】\n')
    msg += MessageSegment.text('📖 收获作物\n\n')
    msg += MessageSegment.text('🍇【 我的农场 】\n')
    msg += MessageSegment.text('📖 查看农场状况，可以通过【 我的农场 @Ta 】查看别人的信息\n\n')
    msg += MessageSegment.text('🔈说明：\n')
    msg += MessageSegment.text('1. 农场系统是一个测试功能，可能会有不稳定的情况\n')
    msg += MessageSegment.text('2. 农场系统可能会在正式版本中删除或修改\n')
    msg += MessageSegment.text('\n-⭐- 🚀 山商AI 🚀 -⭐-')
    await ch.finish(msg)


async def 农场背包(ch, bot, event):
    farm_backpack = eval(get_user_backpack(User(event)).farm_backpack)
    msg = MessageSegment.text('-⭐-🚀 农场背包 🚀-⭐-\n\n')
    if not farm_backpack:
        msg += MessageSegment.text('你的农场背包是空的哦~~~\n')
    for k, v in farm_backpack.items():
        info = ALL_PLANTS[k[:-4]]
        msg += MessageSegment.text(f'{info["logo"]} {k} 【 {v} 】\n')
    msg += MessageSegment.text('\n-⭐- 🚀 山商AI 🚀 -⭐-')
    return msg


async def 农场商店(ch, bot, event):
    msg = MessageSegment.text('-⭐-🚀 农场商店 🚀-⭐-\n\n')
    for k, v in ALL_PLANTS.items():
        msg += MessageSegment.text(f'{v["logo"]}【 {k} 】')
        if v['data']['price']['c']:
            msg += MessageSegment.text(f'🎖️{v["data"]["price"]["c"]} ')
        if v["data"]["price"]["b"]:
            msg += MessageSegment.text(f'💰{v["data"]["price"]["b"]} ')
        if v["data"]["price"]["r"]:
            msg += MessageSegment.text(f'💎{v["data"]["price"]["r"]} ')
        t = v["grow_time"]
        t_h = t // 3600
        t_m = t % 3600 // 60
        t_s = t % 60
        msg += MessageSegment.text(f'\n🕒 时间：')
        if t_h:
            msg += MessageSegment.text(f'{t_h}小时')
        if t_m:
            msg += MessageSegment.text(f'{t_m}分钟')
        if t_s:
            msg += MessageSegment.text(f'{t_s}秒')
        msg += MessageSegment.text(f'\n📦 产量：{v["output"]}')
        msg += MessageSegment.text(f'\n✨️ 经验：{v["output_e"]}')
        msg += MessageSegment.text(f'\n🎁 收益：')
        if v['output_c']:
            msg += MessageSegment.text(f'🎖️{v["output_c"]} ')
        if v['output_b']:
            msg += MessageSegment.text(f'💰{v["output_b"]} ')
        if v['output_r']:
            msg += MessageSegment.text(f'💎{v["output_r"]} ')
        if any([
            v['output_e_mount'], v['output_atk_mount'], v['output_def_mount'], v['output_hp_mount'],
            v['output_atk_growth_mount'], v['output_def_growth_mount'], v['output_hp_growth_mount']
        ]):
            msg += MessageSegment.text('\n属性附加(使用)：')
            if v['output_e_mount']:
                msg += MessageSegment.text(f'\n坐骑经验：+{v["output_e_mount"]} ')
            if v['output_atk_mount']:
                msg += MessageSegment.text(f'\n坐骑攻击力：+{v["output_atk_mount"]} ')
            if v['output_def_mount']:
                msg += MessageSegment.text(f'\n坐骑防御力：+{v["output_def_mount"]} ')
            if v['output_hp_mount']:
                msg += MessageSegment.text(f'\n坐骑生命值：+{v["output_hp_mount"]} ')
            if v['output_atk_growth_mount']:
                msg += MessageSegment.text(f'\n坐骑攻击成长：+{v["output_atk_growth_mount"]} ')
            if v['output_def_growth_mount']:
                msg += MessageSegment.text(f'\n坐骑防御成长：+{v["output_def_growth_mount"]} ')
            if v['output_hp_growth_mount']:
                msg += MessageSegment.text(f'\n坐骑生命成长：+{v["output_hp_growth_mount"]} ')
        msg += MessageSegment.text('\n\n-⭐- 🚀 山商AI 🚀 -⭐-')
        return msg


async def 种植(ch, bot, event):
    # 获取消息
    msg = event.get_plaintext().strip()
    # 获取指令
    cmd = [x for x in msg.split(' ') if x]
    # 检查指令长度
    if len(cmd) == 1:
        msg = MessageSegment.at(event.get_user_id())
        msg += MessageSegment.text(' -> 请提供作物名！')
        return msg
    # 获取用户对象
    user = User(event)
    # 检查是否存在作物
    if cmd[1] not in ALL_PLANTS:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 未找到该作物')
        return msg
    # 检查用户背包
    backpack = get_user_backpack(user)
    if not backpack.get_farm_num(f'{cmd[1]}(种子)'):
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你的背包里没有该作物')
        return msg
    # 获取用户农场
    farm = Farm().find(owner_id=user.qq)
    # 检查是否有农场
    if not farm:
        farm = Farm()
        farm.owner_id = user.qq
        farm.uuid = uuid.uuid1()
        farm.size = 1
        farm.level = 1
        farm.update()
    # 获取种植信息
    p = list(Plant().find_all(farm_uuid=farm.uuid))
    # 计算是否超过种植上限
    if len(p) >= farm.size:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你的农场已经种满了哦！')
        return msg
    # 获取作物对象
    plant = Plant()
    plant.set(**ALL_PLANTS[cmd[1]])
    plant.name = cmd[1]
    plant.plant_time = datetime.datetime.now()
    plant.farm_uuid = farm.uuid
    plant.owner_id = user.qq
    plant.update()
    # 移除种子
    backpack.sub_farm(f'{cmd[1]}(种子)', 1)
    # 返回界面
    msg = MessageSegment.at(user.qq)
    msg += MessageSegment.text(f' -> 【 {cmd[1]} 】种植成功！')
    return msg


async def 我的农场(ch, bot, event):
    # 获取农场
    farm = Farm().find(owner_id=event.get_user_id())
    # 检查农场是否存在
    if not farm:
        msg = MessageSegment.at(event.get_user_id())
        msg += MessageSegment.text(' -> 你还没有农场哦！')
        return msg
    # 构造消息
    msg = MessageSegment.text('-⭐-🚀 我的农场 🚀-⭐-')
    # 获取作物信息
    ps: list[Plant] = list(Plant().find_all(farm_uuid=farm.uuid))
    if not ps:
        msg += MessageSegment.text('你的农场是空的哦~~~\n')
    for i in ps:
        msg += MessageSegment.text(f'\n\n{i.logo} {i.name} ')
        if int(i.time_left()) <= 0:
            if not i.count:
                i.count = i.output
            msg += MessageSegment.text(f'【 🕒 已成熟 】\n')
            msg += MessageSegment.text(f'📦 当前数量：{i.count}\n')
        else:
            t = int(i.time_left())
            t_h = t // 3600
            t_m = t % 3600 // 60
            t_s = t % 60
            msg += MessageSegment.text('【 🕒 ')
            if t_h:
                msg += MessageSegment.text(f'{t_h:02d}时{t_m:02d}分')
            elif t_m:
                msg += MessageSegment.text(f'{t_m:02d}分{t_s:02d}秒')
            else:
                msg += MessageSegment.text(f'{t_s:02d}秒')
            msg += MessageSegment.text(' 】\n')
            msg += MessageSegment.text(f'📦 预计产量：{i.output}\n')
        msg += MessageSegment.text(f'✨️ 预计收益：')
        if i.output_c:
            msg += MessageSegment.text(f'🎖️{i.output_c * (i.count if i.count else i.output)} ')
        if i.output_b:
            msg += MessageSegment.text(f'💰{i.output_b * (i.count if i.count else i.output)} ')
        if i.output_r:
            msg += MessageSegment.text(f'💎{i.output_r * (i.count if i.count else i.output)} ')
    msg += MessageSegment.text('\n\n-⭐- 🚀 山商AI 🚀 -⭐-')
    return msg


async def 农场收获(ch, bot, event):
    # 获取用户对象
    user = User(event)
    # 获取用户农场
    farm = Farm().find(owner_id=user.qq)
    # 检查农场是否存在
    if not farm:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你还没有农场哦！')
        return msg
    # 获取作物信息
    ps: list[Plant] = list(Plant().find_all(farm_uuid=farm.uuid))
    # 检查是否有作物
    if not ps:
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你的农场是空的哦！')
        return msg
    # 检查是否有成熟作物
    if all([i.time_left() > 0 for i in ps]):
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(' -> 你的农场没有成熟的作物哦！')
        return msg
    # 获取背包
    backpack = get_user_backpack(user)
    # 记录收获
    log = {}
    # 收获作物
    for i in ps:
        if i.time_left() <= 0:
            if not i.count:
                i.count = i.output
            log[i.name] = i.count
            backpack.add_farm(f'{i.name}(成熟)', i.count)
            i.delete()
    # 构造消息
    msg = MessageSegment.text('-⭐-🚀 农场收获 🚀-⭐-\n\n【 ')
    msg += MessageSegment.at(user.qq)
    msg += MessageSegment.text(' 】 -> 收获成功！\n\n')
    for k, v in log.items():
        msg += MessageSegment.text(f'{ALL_PLANTS[k]["logo"]} {k} 【 {v} 】\n')
    msg += MessageSegment.text('\n-⭐- 🚀 山商AI 🚀 -⭐-')
    return msg


async def main(ch, bot: Bot, event: Event):
    msg = event.get_plaintext().strip()
    if not msg:
        return
    if msg == '农场系统':
        await ch.finish(await menu(ch, bot, event))
    elif msg == '农场背包':
        await ch.finish(await 农场背包(ch, bot, event))
    elif msg == '农场商店':
        await ch.finish(await 农场商店(ch, bot, event))
    elif msg == '我的农场':
        await ch.finish(await 我的农场(ch, bot, event))
    elif msg == '农场收获':
        await ch.finish(await 农场收获(ch, bot, event))
    elif msg.startswith('种植'):
        await ch.finish(await 种植(ch, bot, event))

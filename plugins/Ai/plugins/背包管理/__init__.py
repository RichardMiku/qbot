from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *

from plugins.Ai.F import get_object
from plugins.Ai.module import User, Plant
from plugins.Ai.object import Object
from plugins.Ai.plugins.农场系统 import ALL_PLANTS
from plugins.Ai.utility.backpack import get_user_backpack


async def my_backpack(ch, bot: Bot, event: Event):
    # 获取背包
    backpack = get_user_backpack(User(event))
    # 获取背包物品
    obj_backpack = eval(backpack.object_backpack)
    msg = MessageSegment.text('-⭐-🚀 我的背包 🚀-⭐-\n\n')
    for obj_name, num in obj_backpack.items():
        obj = get_object(obj_name)
        msg += MessageSegment.text(f'{obj.logo} {obj_name} 【 {num} 】\n')
    msg += MessageSegment.text('\n-⭐- 🚀 山商AI 🚀 -⭐-')
    return msg


async def use_object(ch, bot: Bot, event: Event):
    # 获取消息
    msg: str = event.get_plaintext()
    # 获取指令
    cmd = [x for x in msg.strip().split(' ') if x]
    # 获取用户对象
    user = User(event)
    # 判断指令格式是否正确
    # 【 使用 [物品名称] (数量) (@使用对象) (其它参数) 】
    if len(cmd) < 2:
        await ch.finish(MessageSegment.text('指令格式错误!!!\n【 使用 [物品名称] (数量) (使用对象) (其它参数) 】'))
        return
    elif len(cmd) == 2:
        num = 1
        args = []
    elif len(cmd) > 2 and cmd[2].isdigit():
        num = int(cmd[2])
        args = cmd[3:]
    else:
        num = 1
        args = cmd[2:]
    # 检查背包物品是否足够
    backpack = get_user_backpack(user)
    backpack_num = backpack.get_object_num(cmd[1])
    if backpack_num == 0:
        backpack_num = backpack.get_farm_num(f'{cmd[1]}(成熟)')
    if backpack_num == 0:
        await ch.finish(MessageSegment.text('你还没有该物品哦~~~'))
        return
    elif backpack_num < num:
        await ch.finish(MessageSegment.text(f'你的背包还缺少【 {num - backpack_num}】 个【 {cmd[1]} 】哦~~~'))
        return
    # 获取使用对象
    message = event.get_message()
    for i in message:
        if i.type == 'at':
            use_to = User(i)
            break
    else:
        use_to = user
    # 获取物品对象
    obj: Union[Object, Plant] = get_object(cmd[1])
    # 检查是否为植物
    if obj is None:
        if cmd[1] in ALL_PLANTS:
            obj = Plant()
            obj.set(**ALL_PLANTS[cmd[1]])
    if obj is None:
        await ch.finish(MessageSegment.text('未找到该物品'))
        return
    # 使用物品
    res = await obj.use(ch, user, use_to, num, *args, event=event)
    # 判断使用结果
    if res:
        if backpack.sub_object(obj.name, num):
            await ch.finish()
        elif backpack.sub_farm_object(f'{obj.name}(成熟)', num):
            await ch.finish()
        else:
            await ch.finish(MessageSegment.text('使用失败!!!'))


async def buy_object(ch, bot, event):
    # 获取消息
    msg: str = event.get_plaintext()
    # 获取指令
    cmd = [x for x in msg.strip().split(' ') if x]
    # 获取用户对象
    user = User(event)
    # 标识符
    obj_type = True
    # 判断指令格式是否正确
    # 【 购买 [物品名称] (数量) 】
    if len(cmd) == 2:
        num = 1
    elif len(cmd) == 3 and cmd[2].isdigit():
        num = int(cmd[2])
    else:
        await ch.finish(MessageSegment.text('指令格式错误!!!\n【 购买 [物品名称] (数量) 】'))
        return
    # 获取物品对象
    obj: Union[Object, Plant] = get_object(cmd[1])
    # 检查是否为植物
    if obj is None:
        if cmd[1] in ALL_PLANTS:
            obj_type = False
            obj = Plant()
            obj.set(**ALL_PLANTS[cmd[1]])
            obj.name = cmd[1]
            obj.data = eval(obj.data)
    if obj is None:
        await ch.finish(MessageSegment.text('未找到该物品'))
        return
    # 检查货币是否足够
    if any([
        user.c < obj.data['price']['c'] * num,
        user.b < obj.data['price']['b'] * num,
        user.r < obj.data['price']['r'] * num
    ]):
        msg += MessageSegment.at(user.qq)
        msg += MessageSegment.text('你还缺少:')
        msg += MessageSegment.text(
            f'\n🎖️ {obj.data["price"]["c"] * num - user.c}' if user.c < obj.data['price']['c'] * num else ''
        )
        msg += MessageSegment.text(
            f'\n💰 {obj.data["price"]["b"] * num - user.b}' if user.b < obj.data['price']['b'] * num else ''
        )
        msg += MessageSegment.text(
            f'\n💎 {obj.data["price"]["r"] * num - user.r}' if user.r < obj.data['price']['r'] * num else ''
        )
        await ch.finish(msg)
        return
    # 购买物品
    res = obj.buy(user, num)
    # 判断购买结果
    if not res:
        await ch.finish(MessageSegment.text('购买失败!!!'))
        return
    # 更新用户信息
    backpack = get_user_backpack(user)
    if obj_type:
        backpack.add_object(obj.name, num)
    else:
        backpack.add_farm(f'{obj.name}(种子)', num)
    user.c -= (c := obj.data['price']['c'] * num)
    user.b -= (b := obj.data['price']['b'] * num)
    user.r -= (r := obj.data['price']['r'] * num)
    user.update()
    # 返回结果
    msg: MessageSegment = MessageSegment.at(user.qq)
    msg += MessageSegment.text(
        f' 您成功花费了【{(" 🎖️" + str(c)) if c else ""}{(" 💰" + str(b)) if b else ""}{(" 💎️" + str(r)) if r else ""} 】购买了【 {num} 】个【 {obj.logo} {obj.name} 】')
    await ch.finish(msg)


async def recycle_object(ch, bot, event):
    # 获取消息
    msg: str = event.get_plaintext()
    # 获取指令
    cmd = [x for x in msg.strip().split(' ') if x]
    # 判断指令格式是否正确
    # 【 回收 [物品名称] (数量) 】
    if len(cmd) == 2:
        num = 1
    elif len(cmd) == 3 and cmd[2].isdigit():
        num = int(cmd[2])
    else:
        await ch.finish(MessageSegment.text('指令格式错误!!!\n【 回收 [物品名称] (数量) 】'))
        return
    # 获取用户对象
    user = User(event)
    # 标识符
    obj_type = True
    # 检查背包物品是否足够
    backpack = get_user_backpack(user)
    backpack_num = backpack.get_object_num(cmd[1])
    if backpack_num == 0:
        backpack_num = backpack.get_farm_num(f'{cmd[1]}(成熟)')
    if backpack_num == 0:
        await ch.finish(MessageSegment.text('你还没有该物品哦~~~'))
        return
    elif backpack_num < num:
        await ch.finish(MessageSegment.text(f'你的背包还缺少【 {num - backpack_num} 】 个【 {cmd[1]} 】哦~~~'))
        return
    # 获取物品对象
    obj: Union[Object, Plant] = get_object(cmd[1])
    # 检查是否为植物
    if obj is None:
        if cmd[1] in ALL_PLANTS:
            obj_type = False
            obj = Plant()
            obj.set(**ALL_PLANTS[cmd[1]])
            obj.name = cmd[1]
            obj.data = eval(obj.data)
    if obj is None:
        await ch.finish(MessageSegment.text('未找到该物品'))
        return
    # 回收物品
    try:
        res = await obj.recycle(ch, user, num)
    except AttributeError:
        await ch.finish(MessageSegment.text('该物品不支持回收!!!'))
    # 判断回收结果
    if not res:
        await ch.finish(MessageSegment.text('回收失败!!!'))
        return
    # 更新用户信息
    if obj_type:
        backpack.sub_object(obj.name, num)
    else:
        backpack.sub_farm(f'{obj.name}(成熟)', num)
    # 结束事件
    await ch.finish()


async def main(ch, bot: Bot, event: Event):
    msg: str = event.get_plaintext()
    cmd = [x for x in msg.strip().split(' ') if x]
    if not cmd:
        return
    if msg == '我的背包':
        await ch.finish(await my_backpack(ch, bot, event))
    elif cmd[0] == '使用':
        await use_object(ch, bot, event)
    elif cmd[0] == '购买':
        await buy_object(ch, bot, event)
    elif cmd[0] == '回收':
        await recycle_object(ch, bot, event)

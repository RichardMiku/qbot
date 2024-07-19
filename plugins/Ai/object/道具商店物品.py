from nonebot.adapters.satori import MessageSegment
from nonebot.internal.matcher import Matcher

from plugins.Ai.llm import LLM
from plugins.Ai.object import Object, register_object
from plugins.Ai.utility.backpack import get_user_backpack


@register_object('道具商店')
class 红玫瑰(Object):
    def __init__(self):
        super().__init__()
        self.logo = '🌹'
        self.description = '一朵热烈如火的红玫瑰，象征着无尽的爱情和浪漫'
        self.data['price']['c'] = 2

    async def use(self, ch, owner, use_to, num=1, *arg, **kwargs):
        result = num * 2
        use_to.charm += result
        use_to.update()
        msg = MessageSegment.text('【 ')
        msg += MessageSegment.at(owner.qq)
        msg += MessageSegment.text(' 】')
        msg += MessageSegment.text('\n送给了')
        msg += MessageSegment.text('【 ')
        msg += MessageSegment.at(use_to.qq)
        msg += MessageSegment.text(' 】')
        msg += MessageSegment.text(f' {num} 朵【 {self.logo} {self.name}】\n他的【 🌸️ 魅力值 】 +{result}\n\n')
        msg += MessageSegment.text(LLM("以红玫瑰为主题，写一句浪漫的话"))
        await ch.send(msg)
        return True

    def buy(self, buy_for, num=1, *arg, **kwargs):
        return True

    async def recycle(self, ch: Matcher, recycle_for, num=1, *arg, **kwargs):
        return False


@register_object('道具商店')
class 大便(Object):
    def __init__(self):
        super().__init__()
        self.logo = '💩'
        self.description = '一坨世俗的烦恼，它只会转移而不会消失'
        self.data['price']['c'] = 3

    async def use(self, ch, owner, use_to, num=1, *arg, **kwargs):
        result = num * 1
        use_to.charm -= result
        use_to.update()
        msg = MessageSegment.text('【 ')
        msg += MessageSegment.at(owner.qq)
        msg += MessageSegment.text(' 】')
        msg += MessageSegment.text(f'将 {result} 坨')
        msg += MessageSegment.text(f'【 {self.logo} {self.name}】')
        msg += MessageSegment.text('扣在了')
        msg += MessageSegment.text('【 ')
        msg += MessageSegment.at(use_to.qq)
        msg += MessageSegment.text(' 】')
        msg += MessageSegment.text('头上\n')
        msg += MessageSegment.text(f'导致他的【 🌸️ 魅力值 】 -{result}\n\n')
        msg += MessageSegment.text(LLM("以大便为主题，写一句富有诗意的话"))
        await ch.send(msg)
        return True

    def buy(self, buy_for, num=1, *arg, **kwargs):
        return True

    async def recycle(self, ch: Matcher, recycle_for, num=1, *arg, **kwargs):
        return False

@register_object('道具商店')
class 炸弹(Object):
    def __init__(self):
        super().__init__()
        self.logo = '💣'
        self.description = '一颗炸药包，可以炸掉一切'
        self.data['price']['b'] = 1

    async def use(self, ch, owner, use_to, num=1, *arg, **kwargs):
        result = num * 10
        use_to.charm -= result
        use_to.update()
        msg = MessageSegment.text('【 ')
        msg += MessageSegment.at(owner.qq)
        msg += MessageSegment.text(' 】')
        msg += MessageSegment.text(f'将 {result} 个')
        msg += MessageSegment.text(f'【 {self.logo} {self.name}】')
        msg += MessageSegment.text('扔到了')
        msg += MessageSegment.text('【 ')
        msg += MessageSegment.at(use_to.qq)
        msg += MessageSegment.text(' 】')
        msg += MessageSegment.text('脚下\n')
        msg += MessageSegment.text(f'导致他的【 🌸️ 魅力值 】 -{result}\n\n')
        msg += MessageSegment.text(LLM("以炸弹为主题，写一句富有诗意的话"))
        await ch.send(msg)
        return True

    def buy(self, buy_for, num=1, *arg, **kwargs):
        return True

    async def recycle(self, ch: Matcher, recycle_for, num=1, *arg, **kwargs):
        return False


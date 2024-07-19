import importlib
from abc import ABC, abstractmethod

from nonebot.internal.matcher import Matcher

from plugins.Ai.module import User
from plugins.Ai.module import Object as OBD
from plugins.Ai.utility.backpack import get_user_backpack


class Object(ABC):

    def __init__(self):
        self.name = self.__class__.__name__
        self.logo = ''
        self.description = '这是一个物品'
        # 物品信息
        self.data = {
            # 物品价格
            'price': {
                'c': 0,
                'b': 0,
                'r': 0,
            },
        }

    def check_num(self, owner: User, num=1):
        backpack = get_user_backpack(owner)
        if backpack.get_object_num(self.name) < num:
            return None
        return backpack

    @abstractmethod
    async def use(self, ch: Matcher, owner: User, use_to: User, num=1, *arg, **kwargs):
        """
        :param num: 使用数量
        :param owner: 所有者
        :param use_to: 被使用者
        """

    @abstractmethod
    def buy(self, buy_for: User, num=1, *arg, **kwargs):
        """
        :param num: 购买数量
        :param buy_from: 购买者
        """

    @abstractmethod
    async def recycle(self, ch: Matcher, recycle_for: User, num=1, *arg, **kwargs):
        """
        :param num: 回收数量
        :param recycle_for: 回收者
        """


def register_object(name: str):
    def warp(cls: Object):
        if not OBD().find(name=cls.__name__):
            obj = OBD()
            obj.name = cls.__name__
            obj.owner = name
            obj.insert()
        return cls

    return warp

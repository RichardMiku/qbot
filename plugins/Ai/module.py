import base64
import datetime
import json
import os
import random
import re
import time
from abc import ABC
from io import BytesIO
from typing import Any
import uuid

import httpx
import nonebot
import pymysqlpool
from PIL import Image
from nonebot.adapters.satori import MessageSegment
from nonebot.adapters.satori.event import Event
from nonebot.adapters.satori.message import At
from nonebot.internal.matcher import Matcher

# MySQL连接池
MySQL_POOL = pymysqlpool.ConnectionPool(
    host=os.getenv('MYSQL_HOST'),
    port=int(os.getenv('MYSQL_PORT')),
    database=os.getenv('MYSQL_DATABASE'),
    user=os.getenv('MYSQL_USERNAME'),
    password=os.getenv('MYSQL_PASSWORD'),
    autocommit=True
)

"""
字段类型
"""
TINYTEXT = 'tinytext'
TEXT = 'text'
MEDIUMTEXT = 'mediumtext'
LONGTEXT = 'longtext'
INT = 'int'
FLOAT = 'float'
BOOL = 'bool'
TIMESTAMP = 'timestamp'

"""
防止重复初始化
"""
__INITIALIZED__ = {}


class DB(ABC):
    """
    数据库基类
    """

    def __init__(self: Any):
        self.pool = MySQL_POOL
        self.keys = self.__keys()
        self.length = len(self.keys)
        self.__db_keys: list = __INITIALIZED__.get(self.__table_name(), [])
        self.id = None

    def __call__(self):
        return self

    def __keys(self):
        """
        子类中的所有键
        :return: 所有键
        """
        return tuple(self.__annotations__.keys())

    def __keys_type(self):
        """
        子类中的所有键的类型
        :return: 数据类型
        """
        return self.__annotations__.values()

    @property
    def values(self):
        """
        子类中的所有值
        :return: 所有值
        """
        dic = self.to_dict()
        return tuple((v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v := dic[key], datetime.datetime) else v) for key in
                     self.keys)

    @staticmethod
    def Initialize(cls: Any):
        """
        初始化类装饰器
        :param cls: 需要初始化的类
        :return: cls
        """
        cls().initialize()
        return cls

    def initialize(self):
        """
        初始化函数
        """
        # 检查是否已经初始化
        if self.__class__.__name__ in __INITIALIZED__:
            return
        # 检查表是否存在
        self.__check_table()
        # 检查字段是否完整
        self.__check_field()

    def __check_table(self):
        """
        检查表是否存在
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'show tables like "{self.__class__.__name__}"')
                if not cursor.fetchone():
                    self.__create_table()

    def __create_table(self):
        """
        创建表
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'create table {self.__class__.__name__} (id int primary key auto_increment)')
                conn.commit()

    def __check_field(self):
        """
        检查字段是否完整
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f'show columns from {self.__class__.__name__}')
                fields = [field[0] for field in cursor.fetchall()]
                db_keys = fields.copy()
                for key in self.keys:
                    if key not in fields:
                        db_keys.append(key)
                        self.__add_field(key)
                # 记录已经初始化的字段
                __INITIALIZED__[self.__table_name()] = db_keys

    def __add_field(self, key: str):
        """
        添加字段
        :param key: 字段名
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                if (value := self.__class__.__dict__.get(key)) is not None:
                    cursor.execute(f"""
                    alter table {self.__class__.__name__} 
                    add column {key} {self.__annotations__[key]}
                    default %s
                    """, value)
                else:
                    cursor.execute(
                        f"alter table {self.__class__.__name__} add column {key} {self.__annotations__[key]}")
                conn.commit()

    def __table_name(self):
        """
        表名
        :return: 表名
        """
        return self.__class__.__name__

    @property
    def __next_id(self):
        """
        获取下一个ID
        :return: int
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f'''
                    SHOW CREATE TABLE {self.__table_name()}
                    '''
                )
                return int(re.compile(r'AUTO_INCREMENT=(\d+)').search(cursor.fetchone()[1]).group(1))

    @property
    def __max_id(self):
        """
        获取最大ID
        :return: int
        """
        return self.__next_id - 1

    def execute_fetchall(self, sql: str, *args):
        """
        执行查询
        :param sql: SQL语句
        :param args: 参数
        :return: 结果
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
                return cursor.fetchall()

    def new(self, values=None, keys=None, **kwargs):
        """
        新对象
        """
        new = self.__class__()
        if values is not None:
            keys = keys or self.__db_keys
            for key, value in zip(keys, values):
                if key in self.keys:
                    new.__setattr__(key, value)
        for key, value in kwargs.items():
            if key in self.keys:
                new.__setattr__(key, value)
        return new

    def insert(self):
        """
        插入字段
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"insert into {self.__table_name()} ({', '.join(self.keys)}) "
                    f"values ({', '.join('%s' for _ in range(self.length))})",
                    self.values
                )
                conn.commit()

    def update(self):
        """
        更新字段
        """
        if self.id is None:
            self.insert()
            return
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f'update {self.__table_name()} '
                    f'set {", ".join(f"{x} = %s" for x in self.keys)} '
                    f'where id = {self.id}',
                    self.values
                )
                conn.commit()

    def delete(self):
        """
        删除
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"delete from {self.__table_name()} "
                    f"where id = {self.id}"
                )
                conn.commit()

    def updates(self, *args, **kwargs):
        """
        更新字段
        :param kwargs: 字段名=字段值
        """
        for dic in args:
            if not isinstance(dic, dict):
                continue
            for key, value in dic.items():
                if key in self.keys:
                    self.__setattr__(key, value)
        for key, value in kwargs.items():
            if key in self.keys:
                self.__setattr__(key, value)
        self.update()

    def set(self, **kwargs):
        """
        设置字段
        :param kwargs: 字段名=字段值
        """
        for key, value in kwargs.items():
            if key in self.keys:
                if isinstance(value, dict):
                    value = str(value)
                self.__setattr__(key, value)

    def find(self, **kwargs):
        """
        查找字段(获取一条)
        :param kwargs: 字段名=字段值
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f'select * from {self.__table_name()} '
                    f'where {" and ".join(f"{k} = %s" for k in kwargs)}',
                    tuple(kwargs.values())
                )
                result = cursor.fetchone()
                if result:
                    for key, value in zip(self.__db_keys, result):
                        self.__setattr__(key, value)
                    return self
                return None

    def find_all(self, **kwargs):
        """
        查找字段(获取所有)
        :param kwargs: 字段名=字段值
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                if kwargs:
                    cursor.execute(
                        f'select * from {self.__table_name()} '
                        f'where {" and ".join(f"{k} = %s" for k in kwargs)}',
                        tuple(kwargs.values())
                    )
                else:
                    cursor.execute(f'select * from {self.__table_name()}')
                result = cursor.fetchall()
                if result:
                    for row in result:
                        data = self.__class__()
                        for key, value in zip(self.__db_keys, row):
                            data.__setattr__(key, value)
                        yield data
                return None

    def random_choice(self, **kwargs):
        """
        随机选择字段
        :param kwargs: 字段名=字段值
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                if kwargs:
                    # 如果有参数，则采用先查找全部符合要求的ID，再随机选择一个ID
                    cursor.execute(
                        f'''
                        select * from {self.__table_name()}
                        where {" and ".join(f"{k} = %s" for k in kwargs)}
                        order by rand()
                        limit 1
                        ''',
                        tuple(kwargs.values())
                    )
                    return self.new(cursor.fetchone())
                else:
                    # 如果没有参数，则直接找到最大ID，再随机选择一个ID
                    choice_id = random.randint(1, self.__max_id)
                    # 查找ID
                    return self.find(id=choice_id)

    def random_choices(self, num: int = 1, **kwargs):
        """
        随机选择字段
        :param num: 选择数量
        :param kwargs: 字段名=字段值
        """
        with self.pool.get_connection() as conn:
            with conn.cursor() as cursor:
                if kwargs:
                    # 如果有参数，则采用先查找全部符合要求的ID，再随机选择ID
                    cursor.execute(
                        f'''
                        select * from {self.__table_name()}
                        where {" and ".join(f"{k} = %s" for k in kwargs)}
                        order by rand()
                        limit {num}
                        ''',
                        tuple(kwargs.values())
                    )
                    yield from (self.new(info) for info in cursor.fetchall())
                else:
                    # 如果有参数，则采用先查找全部符合要求的ID，再随机选择ID
                    cursor.execute(
                        f'''
                        select * from {self.__table_name()}
                        order by rand()
                        limit {num}
                        '''
                    )
                    yield from (self.new(info) for info in cursor.fetchall())

    def to_dict(self) -> dict:
        """
        将字段转换为字典
        :return: 字段字典
        """
        return {key: self.__dict__.get(key, self.__class__.__dict__.get(key, None)) for key in self.__annotations__}


@DB.Initialize
class User(DB):
    qq: TINYTEXT
    nickname: TINYTEXT = ''
    level: INT = 0
    exp: INT = 0
    c: INT = 0  # 积分-低级货币
    b: INT = 0  # 金币-中级货币
    r: INT = 0  # 钻石-高级货币
    vip: INT = 0  # VIP等级
    name: TINYTEXT = ''  # 真实姓名
    last_sign_time: TIMESTAMP = datetime.datetime(year=2002, month=12, day=30)  # 最后签到时间
    sign_times: INT = 0  # 签到次数
    zhss_is_bind: INT = 0  # 智慧山商是否绑定
    zhss_username: TINYTEXT = ''  # 智慧山商用户名
    zhss_password: TINYTEXT = ''  # 智慧山商密码
    zhss_last_update: TIMESTAMP = datetime.datetime(year=2002, month=12, day=30)  # 智慧山商最后更新时间
    # 魅力值
    charm: INT = 0
    # 气运
    fortune: INT = 0
    # 坐骑id
    mount_id: INT = -1

    def __init__(self, x=None):
        super().__init__()
        # 如果x是None，则直接返回
        if x is None:
            return
        # 如果x是Event类型，则根据Event初始化
        if isinstance(x, Event):
            user = self.find(qq=x.get_user_id())
            if user is None:
                self.qq = x.get_user_id()
        # 如果x是str类型，则根据qq初始化
        elif isinstance(x, str):
            user = self.find(qq=x)
            if user is None:
                self.qq = x
        # 如果x是At类型，则根据qq初始化
        elif isinstance(x, At):
            user = self.find(qq=x.get('data').get('id'))
            if user is None:
                self.qq = x.get('data').get('id')
        else:
            raise TypeError(f'User.__init__(): x must be Event or str, not {type(x)}')
        # 更新昵称
        try:
            user.nickname
        except AttributeError:
            self.update_nickname()

    @staticmethod
    def get_nickname_by_qq(qq: str):
        with httpx.Client() as client:
            resp = client.get(f'https://api.qjqq.cn/api/qqinfo', params={
                "qq": qq
            }, timeout=2)
            if resp.status_code == 200:
                if (name := resp.json().get('name')) is not None:
                    return name
        return None

    def update_nickname(self):
        """
        更新昵称
        """
        self.nickname = User.get_nickname_by_qq(self.qq)

    def get_img(self):
        return f'https://q.qlogo.cn/headimg_dl?dst_uin={self.qq}&spec=160'

    def zhss_bind(self, username: str, password: str) -> bool:
        """
        绑定智慧山商
        """
        if self.zhss_is_bind and self.zhss_last_update > datetime.datetime.now() - datetime.timedelta(days=1):
            return False
        self.zhss_username = username
        self.zhss_password = password
        self.zhss_is_bind = 1
        self.zhss_last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update()
        return True

    def zhss_unbind(self):
        """
        解绑智慧山商
        """
        self.zhss_is_bind = 0
        self.update()

    def add_exp(self, exp: int = 0):
        """
        增加经验
        """
        self.exp += exp
        if self.exp >= self.level * self.level * 100:
            self.exp -= self.level * self.level * 100
            self.level += 1
            self.add_exp()
        else:
            self.update()

    def add_level(self, level: int):
        """
        增加等级
        """
        self.level += level
        self.update()

    def info(self):
        from plugins.Ai.api import get_hitokoto
        info = MessageSegment.image(self.get_img())
        info += MessageSegment.text(f'\n☀️ 用户昵称：{self.nickname}')
        info += MessageSegment.text(f'\n👑 会员等级：{self.vip}级' if self.vip else '')
        info += MessageSegment.text(f'\n🏆 当前等级：{self.level}')
        info += MessageSegment.text(f'\n✨️ 当前经验：{self.exp}')
        info += MessageSegment.text(f'\n🌸️ 当前魅力：{self.charm}')
        info += MessageSegment.text(f'\n🎖️ 当前积分：{self.c}')
        info += MessageSegment.text(f'\n💰 当前金币：{self.b}')
        info += MessageSegment.text(f'\n💎 当前钻石：{self.r}')
        info += MessageSegment.text(f'\n📅 累计签到：{self.sign_times} 次')
        if self.mount_id > 0:
            mount = Mount().find(id=self.mount_id)
            info += MessageSegment.text(f'\n\n🦄 坐骑名称：{mount.name} 【 等级: {mount.level} 】')
            img = Image.open(BytesIO(base64.b64decode(mount.img.encode())))
            img.thumbnail((80, 80))
            result = BytesIO()
            img.save(result, format='PNG')
            info += MessageSegment.image(raw=result.getvalue(), mime='image/png')
        info += MessageSegment.text('\n🎒 输入「 我的背包 」查看背包')
        info += MessageSegment.text(f'\n\n{get_hitokoto()}')
        return info


@DB.Initialize
class Config(DB):
    """
    type:
        0 -> 全局
        1 -> 群聊
        2 -> 私聊
        3 -> 用户
    uid:
        type = 1 -> 群号
        type = 2 -> QQ号
        type = 3 -> QQ号
        type = 4 -> QQ号
    key:
        配置名
    value:
        配置值
    """
    _type: TEXT
    uid: TINYTEXT
    _key: TINYTEXT
    _value: TEXT


@DB.Initialize
class Api(DB):
    """
    type:
        来源
    data:
        数据
    md5:
        数据md5
    """
    _type: TEXT
    _info: TEXT
    _data: LONGTEXT
    _md5: TEXT


@DB.Initialize
class Object(DB):
    """
    name:
        名称
    owner:
        来自商店
    """
    name: TEXT
    owner: TEXT


@DB.Initialize
class Mount(DB):
    """
    name:
        名称
    owner:
        主人qq
    owner_id:
        主人ID
    """
    name: TEXT
    prompt: TEXT
    owner: TEXT
    owner_id: TEXT
    attributes: TEXT
    level: INT = 0
    exp: INT = 0
    img: LONGTEXT
    created_at: TIMESTAMP
    enable: INT = 0


@DB.Initialize
class BackPack(DB):
    owner_id: INT  # 所有者
    owner: TEXT  # 所有者
    object_backpack: LONGTEXT  # 物品背包
    farm_backpack: LONGTEXT  # 农场背包

    def initialize(self):
        super().initialize()
        for i in self.find_all(farm_backpack=None):
            i.farm_backpack = '{}'
            i.update()

    def add_object(self, obj_name: str, num=1):
        obj_backpack = eval(self.object_backpack)
        if obj_name not in obj_backpack:
            obj_backpack[obj_name] = 0
        obj_backpack[obj_name] += num
        self.object_backpack = str(obj_backpack)
        self.update()
        return True

    def sub_object(self, obj_name: str, num=1):
        obj_backpack = eval(self.object_backpack)
        if obj_name not in obj_backpack:
            return False
        obj_backpack[obj_name] -= num
        if obj_backpack[obj_name] <= 0:
            obj_backpack.pop(obj_name)
        self.object_backpack = str(obj_backpack)
        self.update()
        return True

    def get_object_num(self, obj_name: str):
        obj_backpack = eval(self.object_backpack)
        return obj_backpack.get(obj_name, 0)

    def add_farm(self, farm_name: str, num=1):
        farm_backpack = eval(self.farm_backpack)
        if farm_name not in farm_backpack:
            farm_backpack[farm_name] = 0
        farm_backpack[farm_name] += num
        self.farm_backpack = str(farm_backpack)
        self.update()
        return True

    def sub_farm(self, farm_name: str, num=1):
        farm_backpack = eval(self.farm_backpack)
        if farm_name not in farm_backpack:
            return False
        farm_backpack[farm_name] -= num
        if farm_backpack[farm_name] <= 0:
            farm_backpack.pop(farm_name)
        self.farm_backpack = str(farm_backpack)
        self.update()
        return True

    def get_farm_num(self, farm_name: str):
        farm_backpack = eval(self.farm_backpack)
        return farm_backpack.get(farm_name, 0)


@DB.Initialize
class Plant(DB):
    """
    植物
    """
    name: TEXT  # 名称
    logo: TEXT  # 图标
    grow_time: INT  # 所需生长时间(秒)
    plant_time: TIMESTAMP  # 种植时间
    owner_id: INT  # 主人ID
    farm_uuid: TEXT  # 农场uuid
    # 当前数量
    count: INT = 0
    # 产量
    output: INT = 0
    # 保底产量
    output_min: INT = 0
    # 价格
    data: TEXT
    # 采摘经验
    output_e: INT = 0
    # 产出
    output_c: INT = 0
    output_b: INT = 0
    output_r: INT = 0
    # 使用
    output_e_mount: INT = 0  # 坐骑经验
    output_atk_mount: INT = 0  # 坐骑攻击力增长
    output_atk_growth_mount: INT = 0  # 坐骑攻击力成长值增长
    output_def_mount: INT = 0  # 坐骑防御力增长
    output_def_growth_mount: INT = 0  # 坐骑防御力成长值增长
    output_hp_mount: INT = 0  # 坐骑生命值增长
    output_hp_growth_mount: INT = 0  # 坐骑生命值成长值增长

    def time_left(self):
        """
        是否成熟
        """
        grow_time = time.time() - self.plant_time.timestamp()
        return self.grow_time - grow_time

    async def use(self, ch: Matcher, owner: User, use_to: User, num=1, *arg, **kwargs):
        """
        :param num: 使用数量
        :param owner: 所有者
        :param use_to: 被使用者
        """
        # 检查被使用者是否有坐骑
        if use_to.mount_id < 0:
            if owner.qq == use_to.qq:
                msg = MessageSegment.at(owner.qq)
                msg += MessageSegment.text(' -> 你没有坐骑，无法使用该物品！')
            else:
                msg = MessageSegment.at(owner.qq)
                msg += MessageSegment.text(f' -> 【 {use_to.nickname} 】没有坐骑，无法使用该物品！')
            return False
        msg = MessageSegment.at(owner.qq)
        # 检查是否使用无效
        if not any([
            self.output_e_mount, self.output_atk_mount, self.output_def_mount, self.output_hp_mount,
            self.output_atk_growth_mount, self.output_def_growth_mount, self.output_hp_growth_mount
        ]):
            if owner.qq == use_to.qq:
                msg += MessageSegment.text(' -> 该物品无法使用！')
            else:
                msg += MessageSegment.text(f' -> 【 {use_to.nickname} 】无法使用该物品！')
            return False
        if owner.qq == use_to.qq:
            msg += MessageSegment.text(f' -> 对自己坐骑使用了【 {self.name} 】')
        else:
            msg += MessageSegment.text(f' -> 对【 {use_to.nickname} 】的坐骑使用了【 {self.name} 】')
        # 使用
        mount = Mount().find(id=use_to.mount_id)
        mount.exp += self.output_e_mount * num
        if self.output_e_mount:
            msg += MessageSegment.text(f'\n🎖️ 坐骑经验：+{self.output_e_mount}')
        attr: dict = eval(mount.attributes)
        attr['hp'][0] += self.output_hp_mount * num
        attr['hp'][1] += self.output_hp_growth_mount * num
        attr['atk'][0] += self.output_atk_mount * num
        attr['atk'][1] += self.output_atk_growth_mount * num
        attr['def'][0] += self.output_def_mount * num
        attr['def'][1] += self.output_def_growth_mount * num
        mount.attributes = str(attr)
        mount.update()
        if self.output_atk_mount:
            msg += MessageSegment.text(f'🗡️坐骑攻击: +{self.output_atk_mount * num}\n')
        if self.output_def_mount:
            msg += MessageSegment.text(f'🛡️坐骑防御: +{self.output_def_mount * num}\n')
        if self.output_hp_mount:
            msg += MessageSegment.text(f'❤️坐骑生命: +{self.output_hp_mount * num}\n')
        if self.output_atk_growth_mount:
            msg += MessageSegment.text(f'🗡️坐骑攻击成长: +{self.output_atk_growth_mount * num}\n')
        if self.output_def_growth_mount:
            msg += MessageSegment.text(f'🛡️坐骑防御成长: +{self.output_def_growth_mount * num}\n')
        if self.output_hp_growth_mount:
            msg += MessageSegment.text(f'❤️坐骑生命成长: +{self.output_hp_growth_mount * num}')
        await ch.send(msg)
        return True

    def buy(self, buy_for: User, num=1, *arg, **kwargs):
        """
        :param num: 购买数量
        :param buy_from: 购买者
        """
        return True

    async def recycle(self, ch, user: User, num=1):
        """
        回收
        :param ch: 会话
        :param user: 用户
        :param num: 数量
        """
        user.c += self.output_c * num
        user.b += self.output_b * num
        user.r += self.output_r * num
        user.update()
        msg = MessageSegment.at(user.qq)
        msg += MessageSegment.text(f' -> 回收【 {self.name} 】成功！')
        msg += MessageSegment.text(f'\n🎖️ 积分：+{self.output_c * num}')
        msg += MessageSegment.text(f'\n💰 金币：+{self.output_b * num}')
        msg += MessageSegment.text(f'\n💎 钻石：+{self.output_r * num}')
        await ch.send(msg)
        return True


@DB.Initialize
class Farm(DB):
    """
    农场
    """
    owner_id: INT  # 主人ID
    uuid: TEXT  # uuid
    size: INT = 1  # 大小
    level: INT = 1  # 农场等级

    def get_all_plants(self):
        """
        获取所有植物
        """
        return list(Plant().find_all(farm_uuid=self.uuid))

    def get_plants_num(self):
        """
        获取植物数量
        """
        return len(self.get_all_plants())

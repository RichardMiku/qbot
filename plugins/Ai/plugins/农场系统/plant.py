from plugins.Ai.module import Plant

ALL_PLANTS = {
    "大萝卜": {
        # 图标
        'logo': '🥕',
        # 所需生长时间(秒)
        'grow_time': 600,
        # 产量
        'output': 20,
        # 保底产量
        'output_min': 15,
        # 价格
        'data': {
            "price": {
                'c': 15,
                'b': 0,
                'r': 0
            }
        },
        # 采摘经验
        'output_e': 10,
        # 产出(一个)
        'output_c': 1,
        'output_b': 0,
        'output_r': 0,
        # 使用
        'output_e_mount': 0,  # 坐骑经验
        'output_atk_mount': 0,  # 坐骑攻击力增长
        'output_atk_growth_mount': 0,  # 坐骑攻击力成长值增长
        'output_def_mount': 0,  # 坐骑防御力增长
        'output_def_growth_mount': 0,  # 坐骑防御力成长值增长
        'output_hp_mount': 0,  # 坐骑生命值增长
        'output_hp_growth_mount': 0  # 坐骑生命值成长值增长
    }
}

__PLANTS_NAME_LIST = list(ALL_PLANTS.keys())


def get_plant(name: str):
    if name not in __PLANTS_NAME_LIST:
        return None
    return Plant(name, **ALL_PLANTS[name])

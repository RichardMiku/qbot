from plugins.Ai.module import User, BackPack


def get_user_backpack(user: User):
    backpack = BackPack().find(owner_id=user.id)
    if backpack:
        if not backpack.farm_backpack:
            backpack.farm_backpack = '{}'
        return backpack
    backpack = BackPack()
    backpack.owner_id = user.id
    backpack.owner = user.nickname
    backpack.object_backpack = '{}'
    backpack.farm_backpack = '{}'
    return backpack



import nonebot
from nonebot.adapters.satori import Adapter
from nonebot import require

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(Adapter)

require("nonebot_plugin_apscheduler")
nonebot.load_plugins("plugins")

if __name__ == '__main__':
    nonebot.run(app="__mp_main__:app")
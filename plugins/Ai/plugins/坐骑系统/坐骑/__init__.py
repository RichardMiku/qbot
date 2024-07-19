import base64

from PIL import Image
from nonebot.adapters.satori.message import MessageSegment

from plugins.Ai.api import ComfyUI
from plugins.Ai.module import Mount as M, User

from io import BytesIO


class Mount(M):

    def __init__(self):
        super().__init__()

    async def get_img(self, size=(160, 160)):
        try:
            img = Image.open(BytesIO(base64.b64decode(self.img.encode())))
            img.thumbnail(size)
            result = BytesIO()
            img.save(result, format='PNG')
            return result.getvalue()
        except AttributeError:
            api = ComfyUI()
            img = await api.auto_draw(prompt=self.prompt, size=(512, 512))
            self.set_img(img)
            img = Image.open(BytesIO(img))
            img.thumbnail(size)
            result = BytesIO()
            img.save(result, format='PNG')
            return result.getvalue()

    def set_img(self, img):
        self.img = base64.b64encode(img).decode()

    async def info(self):
        attr = eval(self.attributes)
        msg = MessageSegment.image(raw=await self.get_img(), mime='image/png')
        msg += MessageSegment.text(f'🪧坐骑名称：{self.name}\n')
        msg += MessageSegment.text(f'🚀坐骑等级：{self.level}\n')
        msg += MessageSegment.text(f'✨坐骑经验：{self.exp}\n')
        msg += MessageSegment.text(f'🗡️攻击力：{attr["atk"][0]} ( +{attr["atk"][1]} )\n')
        msg += MessageSegment.text(f'🔰防御力：{attr["def"][0]} ( +{attr["def"][1]} )\n')
        msg += MessageSegment.text(f'❤️生命值：{attr["hp"][0]}/{attr["hp"][2]} ( +{attr["hp"][1]} )\n')
        msg += MessageSegment.text(f'🛸签到积分加成：{attr["sign_in_c"][0]}%\n')
        return msg

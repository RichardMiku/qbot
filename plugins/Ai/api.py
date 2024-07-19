import asyncio
import base64
import io
import os
import random

import httpx
from plugins.Ai.module import Api
import hashlib


def get_hitokoto():
    try:
        data = httpx.get('https://v1.hitokoto.cn/').json()['hitokoto']
        data_md5 = hashlib.md5(data.encode('utf-8')).hexdigest()
        api = Api().find_all(_type='hitokoto', _md5=data_md5)
        if api:
            for i in api:
                if i._data == data:
                    return data
        api = Api()
        api._type = 'hitokoto'
        api._data = data
        api._md5 = data_md5
        api.update()
        return data
    except Exception as e:
        if data := Api().random_choice(_type='hitokoto'):
            return data._data
    return '服务器内部错误'


async def wav2amr(wav):
    output = io.BytesIO()
    input_file = io.BytesIO(wav)
    process = await asyncio.create_subprocess_exec(
        'ffmpeg', '-i', 'pipe:', '-f', 'amr', '-acodec', 'libopencore_amrnb', '-ar', '8000', '-ac', '1', '-b:a',
        '12.2k', 'pipe:',
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate(input=input_file.read())
    output.write(stdout)
    return output.getvalue()


async def text2tts(text, voice=139, timeout=300):
    text = text.replace('\n', '').replace('\r', '').replace('\t', '')
    text = text.replace('、', '[uv_break]').replace('（', '[uv_break]').replace('）', '[uv_break]')
    text = text.replace('【', '[uv_break]').replace('】', '[uv_break]')
    text = text.replace('1', '一').replace('2', '二').replace('3', '三').replace('4', '四').replace('5', '五')
    text = text.replace('6', '六').replace('7', '七').replace('8', '八').replace('9', '九').replace('0', '零')
    text = text.replace('颀', '奇')
    data_md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
    api = Api().find_all(_type=f'text2tts-{voice}', _md5=data_md5)
    if api:
        for i in api:
            if i._info == text:
                return bytes.fromhex(i._data)
    async with httpx.AsyncClient() as client:
        r = await client.post(os.getenv('TTS_BASE_URL') + '/generate', json={
            'prompt': '',
            'text': text,
            'voice': voice,
        }, timeout=timeout)
    if r.status_code != 200:
        return None
    result = await wav2amr(r.content)
    api = Api()
    api._type = f'text2tts-{voice}'
    api._info = text
    api._data = result.hex()
    api._md5 = data_md5
    api.update()
    return result


async def get_student_info_by_name(name):
    async with httpx.AsyncClient() as client:
        r = await client.get(os.getenv('STUDENT_INFO_BASE_URL') + '/api/v1/students', params={
            'name': name,
            'token': os.getenv('STUDENT_INFO_TOKEN')
        })
    data = r.json()
    if data.get('code') != 200:
        return None
    data = data.get('data')
    if not data:
        return None
    return data


class ComfyUI:
    def __init__(self):
        self.base_url = 'http://10.32.81.20:8188'
        self.client = httpx.AsyncClient()
        self.prompt_id = None
        self.file_name = None

    async def auto_draw(self, prompt: str, size: tuple = (512, 1024)):
        await self.draw(prompt, size)
        while not await self.status():
            pass
        return await self.get_image()

    async def draw(self, prompt: str, size: tuple = (512, 1024)):
        r = await self.client.post(f'{self.base_url}/prompt', json={
            "client_id": "QBotClient",
            "prompt": {
                "3": {
                    "inputs": {
                        "seed": random.randint(0, 999999999999999),
                        "steps": 20,
                        "cfg": 8,
                        "sampler_name": "dpmpp_2m",
                        "scheduler": "karras",
                        "denoise": 1,
                        "model": [
                            "4",
                            0
                        ],
                        "positive": [
                            "6",
                            0
                        ],
                        "negative": [
                            "7",
                            0
                        ],
                        "latent_image": [
                            "5",
                            0
                        ]
                    },
                    "class_type": "KSampler",
                    "_meta": {
                        "title": "K采样器"
                    }
                },
                "4": {
                    "inputs": {
                        "ckpt_name": "revAnimated_v2Rebirth.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {
                        "title": "Checkpoint加载器(简易)"
                    }
                },
                "5": {
                    "inputs": {
                        "width": size[0],
                        "height": size[1],
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage",
                    "_meta": {
                        "title": "空Latent"
                    }
                },
                "6": {
                    "inputs": {
                        "text": [
                            "18",
                            1
                        ],
                        "clip": [
                            "4",
                            1
                        ]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {
                        "title": "CLIP文本编码器"
                    }
                },
                "7": {
                    "inputs": {
                        "text": [
                            "18",
                            2
                        ],
                        "clip": [
                            "4",
                            1
                        ]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {
                        "title": "CLIP文本编码器"
                    }
                },
                "8": {
                    "inputs": {
                        "samples": [
                            "3",
                            0
                        ],
                        "vae": [
                            "4",
                            2
                        ]
                    },
                    "class_type": "VAEDecode",
                    "_meta": {
                        "title": "VAE解码"
                    }
                },
                "18": {
                    "inputs": {
                        "input_prompt": prompt,
                        "base_ip": os.getenv('OLLAMA_HOST'),
                        "port": os.getenv('OLLAMA_PORT'),
                        "engine": "ollama",
                        "selected_model": os.getenv('CHAT_MODEL'),
                        "profile": "IF_PromptMKR",
                        "embellish_prompt": "Beautiful",
                        "style_prompt": "None",
                        "neg_prompt": "None",
                        "temperature": 0.7,
                        "max_tokens": 256,
                        "seed": random.randint(0, 999999999999999),
                        "random": True,
                        "keep_alive": True
                    },
                    "class_type": "IF_PromptMkr",
                    "_meta": {
                        "title": "提示词到提示词💬"
                    }
                },
                "22": {
                    "inputs": {
                        "filename_prefix": "QBot",
                        "images": [
                            "8",
                            0
                        ]
                    },
                    "class_type": "SaveImage",
                    "_meta": {
                        "title": "保存图像"
                    }
                }
            }
        })
        self.prompt_id = r.json()['prompt_id']
        return self.prompt_id

    async def status(self):
        if not self.prompt_id:
            return None
        r = (await self.client.get(f'{self.base_url}/history/{self.prompt_id}')).json()
        if self.prompt_id not in r:
            return None
        self.file_name = list(r[self.prompt_id]['outputs'].values())[0]['images'][0]['filename']
        return self.file_name

    async def get_image(self):
        if not self.file_name:
            return None
        r = await self.client.get(f'{self.base_url}/view', params={
            'filename': self.file_name
        })
        return r.content

    def clean(self):
        self.prompt_id = None
        self.file_name = None
        self.client.aclose()
        self.client = httpx.AsyncClient()

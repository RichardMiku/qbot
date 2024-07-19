from nonebot import *
from nonebot.adapters.satori import *
from nonebot.adapters.satori.event import *
from nonebot.adapters.satori.message import *
from nonebot.internal.matcher import Matcher
from plugins.Ai.module import *
from plugins.Ai.F import is_group_message
import random
from plugins.Ai.llm import LLM
import os
import yaml

BASE_PATH = os.path.join(os.path.dirname(__file__), 'img')
BASE_PATH1 = os.path.join(os.path.dirname(__file__), 'img1')


def run(user: User):
    with open(os.path.join(BASE_PATH1, '../TarotData.yml'), 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
        random_number = random.randint(0, 20)
        card = (result['tarot'][random_number])
        card_name = card['name']
        card_img = card['imageName']
        card_mime_t = str(card_img)
        card_mime = card_mime_t[-3:]
        random_number1 = random.randint(0, 1)
        if random_number1:
            card_meaning = '正位：'
            card_meaning += card['positive']

        else:
            card_meaning = '逆位：'
            card_meaning += card['negative']
    msg = MessageSegment.text(f'抽中卡牌：{card_name}')
    with open(os.path.join(BASE_PATH1, f'{card_img}'), 'rb') as g:
        data = g.read()
        msg += MessageSegment.image(raw=data, mime='image/png')
    msg += MessageSegment.text(f'{card_meaning}')

    return msg


# TarotCard = ['抽到的卡：愚者——旅行（对应星象：天王星）',
#              '牌面解读：①轻巧的脚步，地上的障碍物无法限制他。年轻人穿着华丽的衣服，走在悬崖边，他的眼中是他的理想。他左手拿着玫瑰，右手携带全部的家当（包裹），到处流浪。他脸部表情充满着机智和梦想。旁边的狗提醒他，不要一直勇往直前，要停下来想一想。那根支撑包裹的杖象征意志的力量，小狗是危机的暗示。②桂冠代表胜利。玫瑰花代表追求新鲜事物的愿望。五彩缤纷的衣服代表无法轻易舍去的世俗事物。红色的羽毛代表纯洁的内心。包袱代表内心的冲击。 手杖代表愚者充满力量与活力面对新旅程。③头上戴着华丽的头饰，肩上扛着手杖，映在眼中的是他的理想国。现实家说他狂妄，理想家认为他有冒险的精神。',
#              '憧憬自然的地方、毫无目的地前行、喜欢尝试挑战新鲜事物、四处流浪。明知是毫无意义的冒险，错误的选择及失败的结果，却一意孤行，盲目地追求梦想而完全忽略现实；好冒险、寻梦人、不拘泥于传统的观念、自由奔放、一切从基础出发、四处流浪。自由恋爱、不顾及他人看法、以独特的方式获得成功、轻易坠入爱河、浪漫多彩的爱情、独特的恋人、等待交往机会。工作上具冒险心、追求新奇。热衷于事业或学业、以独特的方式取得意外的收获、由于好奇心对当前的学业产生浓厚的兴趣、把握重点、寻求捷径、倾向于自由的工作氛围、适合艺术类工作或从事自由职业。健康状况佳。旅行有意外收获。美好的梦想。',
#              '冒险的行动，追求可能性，重视梦想，无视物质的损失，离开家园，过于信赖别人，为出外旅行而烦恼。心情空虚、轻率的恋情、无法长久持续的融洽感、不安的爱情的旅程、对婚姻感到束缚、彼此忽冷忽热、不顾众人反对坠入爱河、为恋人的负心所伤、感情不专一。工作缺乏稳定性、无责任。成绩一落千丈、没有耐心、行事缺乏计划、经常迟到、猜题错误导致考试失利、考前突击无法为你带来太大的效果。因不安定的生活而生病。不能放心的旅行。不能下决心、怪癖。不切实际。',
#
#              '抽到的卡：魔术师——创造（对应星象：水星）',
#              '牌面解读：①牌面为罗马神话的诸神传信使墨丘利，有着自信的笑容和炯炯有神的眼睛。 牌的桌面摆了宇宙四要素∶权杖（火）、剑（风）、星币（土）、圣杯（水）魔术师头顶上有个无限的符号，腰带为一头尾相接的蛇，是精神永恒的象征。魔术师右手拿着权杖指向天空，左手指着地面，代表权力的交流和精神的赠与。魔术师脚底下为玫瑰和百合，表示人类的动机，反映神的意志，指挥天地。 玫瑰代表生，百合代表死亡。 魔术师为第一张牌，也暗示着你本身也是个魔术师，自己能操纵宇宙的力量。②白色长袍代表纯洁的内心，深红色斗篷代表魔术师的活动意义深远。',
#              '事情的开始，行动的改变，熟练的技术及技巧，贯彻我的意志，运用自然的力量来达到野心。',
#              '意志力薄弱，起头难，走入错误的方向，知识不足，被骗和失败。',
#
#              '抽到的卡：女祭司——神秘（对应星象：月亮）',
#              '牌面解读：一个聪明的人或者女人，可能作出一个好决定。这个圣洁的女祭司，端正的坐着，手中还拿着一卷书，证明她充满智慧，放心交给她去决定好了。',
#              '开发出内在的神秘潜力，前途将有所变化的预言，深刻的思考，敏锐的洞察力，准确的直觉。',
#              '过于洁癖，无知，贪心，目光短浅，自尊心过高，偏差的判断，有勇无谋，自命不凡。',
#
#              '抽到的卡：皇后——丰收（对应星象：金星）',
#              '牌面解读：美丽的女皇坐在优雅舒适的椅子上，四周一片茂密森林，令人有种无忧无虑，悠闲自在的感觉，椅子旁还放着一颗心，似乎是她有心赐给你这些丰沃的土地和果子，圆满的爱，应该好好的谢恩了。',
#              '幸福，成功，收获，无忧无虑，圆满的家庭生活，良好的环境，美貌，艺术，与大自然接触，愉快的旅行，休闲。',
#              '不活泼，缺乏上进心，散漫的生活习惯，无法解决的事情，不能看到成果，耽于享乐，环境险恶，与家人发生纠纷。',
#
#
#
#
#     ]
#
# def run(user: User):
#     random_number = random.randint(1, 3)
#     print(LLM(f"\n\n帮我把下面的话改写一下：{TarotCard[random_number * 4 - 1]}"))
#
#
#     msg = MessageSegment.text(f'{TarotCard[random_number * 4 - 4]}\n\n{TarotCard[random_number * 4 - 3]}\n\n')
#     print(msg)
#     msg += MessageSegment.text(LLM(f"帮我把下面的话改写一下：{TarotCard[random_number * 4 - 1]}"))
#     with open(os.path.join(BASE_PATH, 'fool.png'), 'rb') as f:
#         data = f.read()
#         msg += MessageSegment.image(raw=data, mime='image/png')
#
#
#     return msg
def shuffle(user: User):
    msg = '洗牌成功！'
    with open(os.path.join(BASE_PATH, 'shuffle.png'), 'rb') as g:
        data1 = g.read()
        msg += MessageSegment.image(raw=data1, mime='image/png')
    return msg


def introduce(user: User):
    msg = '塔罗牌，由“TAROT”一词音译而来，被称为“大自然的奥秘库”。它是西方古老的占卜工具，中世纪起流行于欧洲，起源一直是个谜。塔罗牌是西方最为古老和神秘的占卜方法之一，它具有很强的准确性和多样性，至今仍是全世界广为使用的占卜方法之一。'
    with open(os.path.join(BASE_PATH, '介绍.png'), 'rb') as g:
        data2 = g.read()
        msg += MessageSegment.image(raw=data2, mime='image/png')
    return msg


async def main(ch: Matcher, bot: Bot, event: Event):
    msg = event.get_plaintext()
    if msg == '塔罗牌':
        await ch.finish(run(User(event)))
    if msg == '塔罗牌洗牌':
        await ch.finish(shuffle(User(event)))
    if msg == '塔罗牌介绍':
        await ch.finish(introduce(User(event)))

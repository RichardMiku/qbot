import datetime

from langchain.agents import initialize_agent, AgentType, create_react_agent
from langchain_core.tools import Tool
from nonebot.adapters.satori import MessageSegment

from plugins.Ai.F import get_now_time, is_group_message, get_group_id, is_private_message
from plugins.Ai.llm import LLM, QA, ChatGPT
from plugins.Ai.plugins.智慧山商 import timetable
from plugins.Ai.api import text2tts

global g_ch, g_bot, g_event


async def chat(msg: str) -> str:
    return await LLM.ainvoke(msg)


async def 查询课程表(*args, **kwargs):
    schedule = await timetable(g_ch, g_bot, g_event)
    if schedule.startswith('未绑定智慧山商') or schedule.startswith('账号或密码错误'):
        return schedule
    msg = f"""
    Answer my question in Chinese based on the following information：
    
    Now Time: {get_now_time()} 星期{'一二三四五六日'[datetime.date.today().weekday()]}
    This week's class schedule: {schedule}
    Today's class schedule: {await timetable(g_ch, g_bot, g_event, today=True)}
    
    (example) The course follows the following format: 
        【 数字（双语图像处理） 】
        🧑‍🏫教师：「 郑毅 」
        📖节次：「 第7~8节 」
        ⏰时间：「 16:30~18:10 」
        📌地点：「 西校2109 」
    
    question: {g_event.get_plaintext()}
    """
    return await LLM.ainvoke(msg)


async def 问问题(*args, **kwargs):
    msg = f"""
    Answer my question in Chinese based on the following information：
    {f"current qq group name: {g_event.__dict__.get('guild').name}" if is_group_message(g_event) else ''}
    {f"current qq group id: {get_group_id(g_event)}" if is_group_message(g_event) else ''}
    now time: {get_now_time()} 星期{'一二三四五六日'[datetime.date.today().weekday()]}
    our school: 山东工商学院
    
    If you need to display 社团 information, please follow the following format:
    【 社团名 】
    🛸 社长：「 社长名(社长QQ) 」
    🚀 副社长：「 社长名(社长QQ) 」
    🌏 社团QQ群：「 社团QQ群号 」
    📖 社团简介：「 社团简介 」
    
    If I ask another question, I don't need to follow the above format.
    
    question: {g_event.get_plaintext()}
    """
    # if not is_private_message(g_event):
    #     return QA['general']({"query": msg, "context": "group"})
    # return QA({"query": msg}).get('result')
    return (await QA.ainvoke({"query": msg})).get('result')


async def 身份(*args, **kwargs):
    msg = f"""
    <|start_header_id|>system<|end_header_id|>
    Answer my question in Chinese based on the following information：
    You were created by 【 电子2101曾钦李 】 and his partner 【 通信2202田晶晶 】、【 电子2101刘英江 】、【 电子2101阮皓颀 】
    You were created on 【 2024-5-8 】
    You name is 【 山商AI 】
    <|eot_id|>
    
    {g_event.get_plaintext()}
    """
    return await LLM.ainvoke(msg)


tools = [
    Tool(
        name="Ask a question",
        func=问问题,
        coroutine=问问题,
        description="A tool that can answer questions about school information and club information.",
        return_direct=True
    ),
    Tool(
        name="Check the course schedule",
        func=查询课程表,
        coroutine=查询课程表,
        description="Information about the course schedule can be found here.",
        return_direct=True
    ),
    Tool(
        name="get identity",
        func=身份,
        coroutine=身份,
        description="Use this tool when someone asks you who you are or who created you.",
        return_direct=True
    ),
    Tool(
        name="chat with AI",
        func=chat,
        coroutine=chat,
        description="Use this tool when other tools are unavailable",
        return_direct=True
    )
]

agent = initialize_agent(tools, LLM, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


async def main(ch, bot, event):
    global g_ch, g_bot, g_event
    if not event.is_tome():
        return
    g_ch = ch
    g_bot = bot
    g_event = event
    msg = (await agent.ainvoke(event.get_plaintext())).get('output')
    if len(msg) <= 100:
        await ch.send(msg)
        msg = MessageSegment.audio(raw=await text2tts(msg), mime='audio/amr')
    await ch.finish(msg)
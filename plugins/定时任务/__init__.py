from nonebot_plugin_apscheduler import scheduler

from plugins.Ai.llm import LLM, Embeddings


@scheduler.scheduled_job("cron", minute="*/3", id="job_0", args=[], kwargs={})
async def _():
    """
    每隔3min执行一次
    """
    await LLM.ainvoke('如果你可以看懂这句话，你只需要回复“你好”即可')

FROM nikolaik/python-nodejs:python3.11-nodejs21

COPY . /app
WORKDIR /app

# 小鱼一键换源
RUN apt update \
    && apt install wget python3-yaml -y  \
    && echo "chooses:\n" > fish_install.yaml \
    && echo "- {choose: 5, desc: '一键配置:系统源(更换系统源,支持全版本Ubuntu系统)'}\n" >> fish_install.yaml \
    && echo "- {choose: 2, desc: 更换系统源并清理第三方源}\n" >> fish_install.yaml \
    && echo "- {choose: 1, desc: 添加ROS/ROS2源}\n" >> fish_install.yaml \
    && wget http://fishros.com/install  -O fishros && /bin/bash fishros \
    && rm -rf /var/lib/apt/lists/*  /tmp/* /var/tmp/* \
    && apt-get clean && apt autoclean

# 安装ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# 安装python依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# MySQL配置
ENV MYSQL_HOST='127.0.0.1'
ENV MYSQL_PORT='3306'
ENV MYSQL_DATABASE='qbot'
ENV MYSQL_USERNAME='qbot'
ENV MYSQL_PASSWORD='tcESyrT2E4CehZZW'

# 智慧山商API后端配置
ENV ZHSS_API_BASE='http://127.0.0.1:3273/v1'

# Satori配置
ENV ENVIRONMENT='prod'
ENV DRIVER='~fastapi+~httpx+~websockets'
ENV SATORI_CLIENTS='[{"host": "10.32.81.13","port": "5500","path": "","token": "6e6ac409bd8812a202545f1acb6e9e0b12b9d4a82c011a73280800facd11d4ab"}]'

# Ollama后端配置
ENV OLLAMA_BASE_URL='http://10.32.81.11:11434'
ENV CHAT_MODEL='wangshenzhi/llama3-8b-chinese-chat-ollama-q4'
ENV EMBEDDING_MODEL='nomic-embed-text'

# Milvus配置
ENV MILVUS_HOST='127.0.0.1'
ENV MILVUS_PORT='19530'

# TTS后端
ENV TTS_BASE_URL='http://127.0.0.1:1232'

# OpenAI配置
ENV OPENAI_API_BASE='https://api.xiaoai.plus/v1'
# 用它务必联系我
ENV OPENAI_API_KEY=''

# 学生信息查询API
ENV STUDENT_INFO_BASE_URL='http://127.0.0.1:3274'
ENV STUDENT_INFO_TOKEN=''

# 主要群
ENV MAIN_GROUPS='[587392634]'

CMD ["python", "/app/bot.py"]
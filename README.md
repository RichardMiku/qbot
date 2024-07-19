# 🤖 QQ机器人
#### 先这么叫着吧
> 一个基于NoneBot2的QQ机器人，使用Satori协议与后端通信，使用nonebot-adapter-satori适配器与QQ通信  
> 
> 后端使用Chronocat，使用HTTP协议与QQ机器人通信
 
## 项目资源
> **框架**：[NoneBot2](https://nonebot.dev/)   
> **协议**：[Satori](https://satori.js.org/zh-CN/)   
> **后端**：[Chronocat](https://chronocat.vercel.app/)   
> **适配器**：[nonebot-adapter-satori](https://github.com/nonebot/adapter-satori)

## Chronocat部署
> 官方文档：[Chronocat](https://chronocat.vercel.app/install)
### 使用Docker部署
```shell
docker run -it \
  --name chronocat \
  -p 16530:16530 \
  -p 5500:5500 \
  -p 16340:16340 \
  -v ./config:/chrono/.chronocat/config \
  -v ./qq:/chrono/.config/QQ \
  chronoc/at
```
### 参数
下面解释了各个参数的意义。推荐配置的参数均已包含在上方的命令里。

端口映射
暴露 Chronocat 登录服务：
```text
-p 16340:16340
```
暴露 Chronocat Red 服务：
```text
-p 16530:16530
```
暴露 Chronocat Satori 服务：
```text
-p 5500:5500
```
持久化
下文中提供的命令都将在工作目录（当前文件夹）创建持久化目录，因此请先设定好用于 Chronocat 的工作目录。

持久化 Chronocat 配置：
```text
-v ./config:/chrono/.chronocat/config
```
默认情况下，容器停止后登录信息会被保留，但销毁容器后登录信息会被一并销毁。因此，推荐对容器进行持久化配置，以保留 QQ 的登录信息，或是直接保留所有 QQ 数据。

若要持久化登录信息：
```text
-v ./nt_db:/chrono/.config/QQ/global/nt_db
```
若要持久化 QQ 的所有数据：
```text
-v ./qq:/chrono/.config/QQ
```

### Nonebot 环境配置
#### 使用pip安装依赖
```shell
pip install 'nonebot2[fastapi]'
pip install 'nonebot2[httpx]'
pip install 'nonebot2[websockets]'
pip install nonebot-adapter-satori
```
#### 配置文件
```text
# .env
ENVIRONMENT=dev
DRIVER=~fastapi+~httpx+~websockets
```
```text
# .env.dev
SATORI_CLIENTS='
[
  {
    "host": "后端IP地址",
    "port": "5500",
    "path": "",
    "token": "这里填密钥"
  }
]
'
```
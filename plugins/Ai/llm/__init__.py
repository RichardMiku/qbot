import os

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.llms.ollama import Ollama
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Milvus
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
# from xpinyin import Pinyin
from pymilvus import utility, connections


"""
初始化 GPT-3.5-Turbo 模型
"""
ChatGPT = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
"""
初始化 Ollama 模型
"""
LLM = Ollama(model=os.getenv('CHAT_MODEL'), base_url=os.getenv('OLLAMA_BASE_URL'))
"""
初始化 OllamaEmbeddings 模型
"""
Embeddings = OllamaEmbeddings(model=os.getenv('EMBEDDING_MODEL'), base_url=os.getenv('OLLAMA_BASE_URL'))

# 建立的向量数据库
vector_db = {}
# 获取BASE路径
base_path = os.path.join(os.path.dirname(__file__), 'documents')
# 获取文档目录
dir_list = os.listdir(base_path)
# 数据
docs = []
# 读取文件夹
for d in dir_list:
    # 数据
    # docs = []
    # 获取文件列表
    file_list = os.listdir(os.path.join(base_path, d))
    # 读取文件
    for file in file_list:
        # 加载数据
        loader = TextLoader(os.path.join(base_path, d, file), encoding='utf8')
        documents = loader.load()
        # 分割文本
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        # 分割文档
        docs.extend(text_splitter.split_documents(documents))
    # if d != 'general':
    #     # 读取通用文件夹
    #     file_list = os.listdir(os.path.join(base_path, 'general'))
    #     # 读取文件
    #     for file in file_list:
    #         # 加载数据
    #         loader = TextLoader(os.path.join(base_path, 'general', file), encoding='utf8')
    #         documents = loader.load()
    #         # 分割文本
    #         text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    #         # 分割文档
    #         docs.extend(text_splitter.split_documents(documents))
# 删除数据集
connections.connect("default", host=os.getenv('MILVUS_HOST'), port=os.getenv('MILVUS_PORT'))
utility.drop_collection("LangChainCollection")

# 创建向量数据库
# vector_db[d] = Milvus.from_documents(
vector_db = Milvus.from_documents(
    docs,
    Embeddings,
    # collection_name=Pinyin().get_pinyin(d, ''),
    connection_args={"host": os.getenv('MILVUS_HOST'), "port": os.getenv('MILVUS_PORT')}
)

"""
基于 Ollama 模型和检索器创建 QA 模型
"""
# QA = {} for k, v in vector_db.items(): # 创建检索器 retriever = v.as_retriever() retriever.search_kwargs[
# 'distance_metric'] = 'cos' retriever.search_kwargs['k'] = 4 QA[k] = RetrievalQA.from_chain_type(llm=LLM,
# chain_type="stuff", retriever=retriever, return_source_documents=False)

# 创建检索器
retriever = vector_db.as_retriever()
retriever.search_kwargs['distance_metric'] = 'cos'
retriever.search_kwargs['k'] = 4

QA = RetrievalQA.from_chain_type(llm=LLM, chain_type="stuff", retriever=retriever, return_source_documents=False)
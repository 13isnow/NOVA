import os
from Log import logger
from DocLoad import YuqueBase
from RAG import EmbedBase, GraphBase
from RAG import build_rag_chain

DOC_DIR = os.path.join(os.path.dirname(__file__), "Yuque")

def DocLoad():
    token = input('input your token: ')
    yuque = YuqueBase(token, DOC_DIR)
    user_name = ['阮一海']
    yuque.get_userDoc(user_name)

def DocStore():
    embedding_base = EmbedBase()
    embedding_base.process(DOC_DIR)

def DocQuery():
    embedding_base = EmbedBase()
    query = "如何使用 RAG 模型"
    res = embedding_base.search(query)
    for hits in res:
        for hit in hits:
            print(hit)

def DocGraph():
    graph_base = GraphBase()
    graph_base.process(DOC_DIR)

def GraphQuery():
    graph_base = GraphBase()
    query = "如何使用 RAG 模型"
    res = graph_base.search(query)
    

def Nova_QA(query):
    chain = build_rag_chain()
    response = chain.invoke({"question": query})
    return response


if __name__ == '__main__':
    # DocLoad()
    # DocStore()
    # DocQuery()
    # DocGraph()
    # GraphQuery()

    query = "如何使用 RAG 模型"
    response = Nova_QA(query)
    print("Nova LLM:", response)

from typing import List
from pydantic import Field
from langchain.schema import BaseRetriever, Document
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser


from LLM import LLMAgent
from .DocBase import EmbedBase
from .GraphBase import GraphBase

class RAGBase(BaseRetriever):
    """支持多模态检索的RAG基类"""
    milvus: EmbedBase = Field(default_factory=EmbedBase)
    graph: GraphBase = Field(default_factory=GraphBase)
    llm: LLMAgent = Field(default_factory=LLMAgent)

    class Config:
        arbitrary_types_allowed = True  # 允许自定义类型字段

    def _embeddings_retrieve(self, query: str, k: int = 3) -> List[Document]:
        """向量检索核心方法"""
        try:
            # 假设milvus.search返回格式为 List[SearchResult]
            results = self.milvus.search(query, k=k)
            return [
                Document(
                    page_content=hit.entity.get("content"),
                    metadata={"id": hit.id, "score": hit.score}
                ) for result in results for hit in result
            ]
        except Exception as e:
            print(f"Vector search failed: {str(e)}")
            return []

    def _graph_retrieve(self, entities: List[str], k: int = 3) -> List[dict]:
        """知识图谱检索核心方法"""
        try:
            return self.graph.search(entities, k=k)
        except Exception as e:
            print(f"Graph search failed: {str(e)}")
            return []

    def _format_graph_results(self, graph_data: List[dict]) -> str:
        """格式化图谱结果为自然语言"""
        return "\n".join([
            f"实体「{item['source']}」通过关键词「{item['keywords']}」关联到「{item['target']}」"
            for item in graph_data
        ])

    def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        """检索流程主入口"""
        # 向量检索
        vector_docs = self._embeddings_retrieve(query, k=kwargs.get('k', 3))
        
        # 提取实体用于图谱查询
        entity_ids = list({doc.metadata["id"] for doc in vector_docs})
        
        # 知识图谱检索
        graph_data = self._graph_retrieve(entity_ids, k=kwargs.get('k', 3))
        
        # 构建综合上下文
        combined_content = (
            "【向量检索结果】\n" + 
            "\n".join([f"- {doc.page_content} (相关性：{doc.metadata['score']:.2f})" 
                      for doc in vector_docs]) +
            "\n\n【知识图谱关联】\n" + 
            self._format_graph_results(graph_data)
        )
        
        return [Document(page_content=combined_content)]

def build_rag_chain():
    """构建端到端RAG流程链"""
    retriever = RAGBase()
    
    # 支持动态参数传递
    prompt = ChatPromptTemplate.from_template("""
        基于以下多源信息回答问题：
        {context}

        用户问题：{question}
        
        请按照以下格式回答：
        1. 总结核心信息
        2. 分析关联关系
        3. 给出最终结论
    """)
    
    # 链式结构优化
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | retriever.llm  # 使用集成的LLM实例
        | StrOutputParser()
    )
    
    return chain    
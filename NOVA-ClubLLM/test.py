import os
import re
from typing import List, Dict
from milvus import MilvusClient
from markdown import markdown
from bs4 import BeautifulSoup  # 用于清理HTML标签
from sentence_transformers import SentenceTransformer
from text_splitter import SemanticChunker  # 需要安装langchain-text-splitters

# ====== 配置部分 ======
MILVUS_URI = "http://localhost:19530"  # Milvus服务地址
COLLECTION_NAME = "markdown_knowledge"  # 集合名称
EMBEDDING_MODEL = "BAAI/bge-base-zh-v1.5"  # 中文嵌入模型
MARKDOWN_DIR = "./docs"  # Markdown文件存放目录
BATCH_SIZE = 50  # 批量插入数量（提升写入效率）

# ====== 工具函数 ======
def parse_markdown(file_path: str) -> Dict:
    """解析Markdown文件，提取元数据和正文内容"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 提取标题（第一个一级标题）
    title = re.search(r'^#\s+(.+)$', content, flags=re.MULTILINE)
    title = title.group(1).strip() if title else os.path.basename(file_path)
    
    # 转换Markdown为纯文本
    html = markdown(content)
    text = BeautifulSoup(html, "html.parser").get_text(separator="\n")
    
    return {
        "title": title,
        "content": text,
        "source": os.path.basename(file_path)
    }

def split_text(text: str) -> List[str]:
    """使用语义分块策略分割文本"""
    splitter = SemanticChunker(
        embeddings=SentenceTransformer(EMBEDDING_MODEL),
        breakpoint_threshold=0.65  # 相似度低于此值时分割
    )
    return splitter.split_text(text)

# ====== 主流程 ======
def main():
    # 初始化Milvus客户端
    client = MilvusClient(uri=MILVUS_URI)
    
    # 创建集合（如果不存在）
    if not client.has_collection(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            dimension=768,  # 与嵌入模型维度一致
            primary_field_name="id",
            vector_field_name="vector",
            id_type="int",
            auto_id=True,
            enable_dynamic_field=True  # 允许存储元数据
        )
    
    # 初始化嵌入模型
    encoder = SentenceTransformer(EMBEDDING_MODEL)
    
    # 遍历Markdown文件
    batch_data = []
    for file_name in os.listdir(MARKDOWN_DIR):
        if not file_name.endswith(".md"):
            continue
            
        file_path = os.path.join(MARKDOWN_DIR, file_name)
        doc_data = parse_markdown(file_path)
        
        # 分块处理
        chunks = split_text(doc_data["content"])
        print(f"Processing {file_name}: {len(chunks)} chunks")
        
        # 生成嵌入向量
        embeddings = encoder.encode(chunks, normalize_embeddings=True)
        
        # 构建批量数据
        for i, (chunk, vec) in enumerate(zip(chunks, embeddings)):
            batch_data.append({
                "content": chunk,
                "vector": vec.tolist(),
                "metadata": {
                    "source": doc_data["source"],
                    "title": doc_data["title"],
                    "chunk_index": i
                }
            })
            
            # 批量插入
            if len(batch_data) >= BATCH_SIZE:
                client.insert(COLLECTION_NAME, batch_data)
                batch_data = []
    
    # 插入剩余数据
    if batch_data:
        client.insert(COLLECTION_NAME, batch_data)
    
    # 创建索引（提升查询性能）
    client.create_index(
        collection_name=COLLECTION_NAME,
        field_name="vector",
        index_params={
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
    )
    
    print(f"数据存储完成，共处理 {len(os.listdir(MARKDOWN_DIR))} 个Markdown文件")

if __name__ == "__main__":
    main()
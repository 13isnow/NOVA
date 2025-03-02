import os
from markdown import markdown
from bs4 import BeautifulSoup  # 用于清理HTML标签
from pymilvus import MilvusClient, DataType
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter

from Log import logger
from Param import *

def parse_markdown(file_path: str):
    """解析Markdown文件，提取元数据和正文内容"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        f.seek(0)
        lines = f.readlines()
        
    publish_time = lines[0].split()[-1]
    url = lines[1]
    author = lines[2].split()[-1]

    # 提取文件名作为标题
    title, id = os.path.basename(os.path.splitext(file_path)[0]).rsplit('-', 1)
    
    # 转换Markdown为纯文本
    html = markdown(content)
    text = BeautifulSoup(html, "html.parser").get_text(separator="\n")
    
    return {
        "publish_time": publish_time,
        "url": url,
        "author": author,
        "title": title,
        "content": text,
        "id": id
    }


class EmbedBase:
    def __init__(self):
        self.client = MilvusClient(MILVUS_URI)
        logger.info(f"Connected to Milvus server: {MILVUS_URI}")
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self.splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        self._init_collection()


    def _init_collection(self):
        # self.client.drop_collection(COLLECTION_NAME)
        if not self.client.has_collection(COLLECTION_NAME):
            schema = MilvusClient.create_schema(
                auto_id=True,
                enable_dynamic_field=True  # 允许存储额外元数据
            )

            schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True)
            schema.add_field(field_name="publish_time", datatype=DataType.VARCHAR, max_length=100)
            schema.add_field(field_name="url", datatype=DataType.VARCHAR, max_length=500)
            schema.add_field(field_name="author", datatype=DataType.VARCHAR, max_length=100)
            schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=100)
            schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=10000)
            schema.add_field(field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM)  # 维度根据模型调整

            # 定义索引参数
            index_params = self.client.prepare_index_params()
            index_params.add_index(field_name="title", index_type="Trie")
            index_params.add_index(field_name="publish_time", index_type="Trie")
            index_params.add_index(
                field_name="embedding",
                metric_type="COSINE",
                index_type="IVF_FLAT",
                index_name="vector_index",
                params={ "nlist": 128 }
            )

            # 创建集合
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                schema=schema,
                index_params=index_params
            )

        self.client.load_collection(COLLECTION_NAME)

    def _insert_docs(self, doc_list):
        self.client.insert(
                    collection_name=COLLECTION_NAME,
                    data=doc_list
                )

    def _calculate_embedding(self, text: str):
        """计算文本的嵌入向量"""
        return self.encoder.encode(text, normalize_embeddings=True)

    def _split_text(self, text: str):
        """使用语义分块策略分割文本"""
        return self.splitter.split_text(text)
        
    def _is_update(self, doc_cfg):
        """检查文档是否需要更新"""
        title = doc_cfg["title"]
        publish_time = doc_cfg["publish_time"]
        expr = f'title == "{title}" and publish_time == "{publish_time}"'
        existing_doc = self.client.query(
            collection_name=COLLECTION_NAME,
            filter = expr,
            output_fields=["id"]
        )
        return len(existing_doc) == 0

    def _process_doc(self, doc_path):
        doc_cfg = parse_markdown(doc_path)
        if not self._is_update(doc_cfg):
            return []
        
        chunks = self._split_text(doc_cfg["content"])
        embeddings = self._calculate_embedding(chunks)

        data_list = []
        for chunk, vec in zip(chunks, embeddings):
            data_list.append({
                "publish_time": doc_cfg["publish_time"],
                "title": doc_cfg["title"],
                "content": chunk,
                "embedding": vec.tolist(),
                "url": doc_cfg["url"],
                "author": doc_cfg["author"],
            })
        
        return data_list

    def process(self, docs_dir):
        batch_data = []
        for dir in os.listdir(docs_dir):
            dir_path = os.path.join(docs_dir, dir)
            for file_name in os.listdir(dir_path):
                logger.info(f"Processing {file_name}")
                if not file_name.endswith(".md"):
                    continue
                file_path = os.path.join(dir_path, file_name)
                batch_data.extend(self._process_doc(file_path))

                if len(batch_data) >= BATCH_SIZE:
                    self._insert_docs(batch_data)
                    batch_data.clear()

        if batch_data:
            self._insert_docs(batch_data)
            batch_data.clear()

    def search(self, query_text, k=3):
        query_vec = self._calculate_embedding(query_text)
        results = self.client.search(
            collection_name=COLLECTION_NAME,
            anns_field="embedding",
            data=[query_vec.tolist()],
            limit=k,
            search_params={"metric_type": "COSINE"},
            output_fields=["content", "author", "url", "title"]
        )
        return results
                

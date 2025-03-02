import os
from markdown import markdown
from bs4 import BeautifulSoup  # 用于清理HTML标签
from lightrag import LightRAG, QueryParam
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc
import re
import pandas as pd
from io import StringIO

from Log import logger
from Param import *

def parse_markdown(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 转换Markdown为纯文本
    html = markdown(content)
    text = BeautifulSoup(html, "html.parser").get_text(separator="\n")

    return text

class GraphBase:
    def __init__(self):
        working_dir = os.path.join(os.path.dirname(__file__), GRAPHDIR)
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)

        self.graph = LightRAG(
            working_dir=working_dir,
            llm_model_func=ollama_model_complete,  # Use Ollama model for text generation
            llm_model_name="llama3",  # Your model name
            # Use Ollama embedding function
            embedding_func=EmbeddingFunc(
                embedding_dim=EMBEDDING_DIM,
                max_token_size=10000,
                func=lambda texts: ollama_embedding(texts, embed_model="nomic-embed-text"),
            ),
        )
        logger.info(f"Connected to Graph: {working_dir}")

    def _process_doc(self, doc_path):
        text = parse_markdown(doc_path)
        return text

    def process(self, docs_dir):
        for dir in os.listdir(docs_dir):
            dir_path = os.path.join(docs_dir, dir)
            for file_name in os.listdir(dir_path):
                logger.info(f"Processing {file_name}")
                if not file_name.endswith(".md"):
                    continue
                file_path = os.path.join(dir_path, file_name)
                self.graph.insert(self._process_doc(file_path))

    def _extract_csv(self, text: str):
        relations_data = text.split("-----Relationships-----")[1]\
                             .split("-----Sources-----")[0]\
                             .split("```csv")[1]\
                             .split("```")[0]\
                             .strip()
        
        df = pd.read_csv(StringIO(relations_data))
        return df[["source", "target", "keywords"]].to_dict(orient="records")
    

    def search(self, query, k=3):
        result = self.graph.query(
            query,
            param=QueryParam(
                mode="local",
                top_k=k,
                only_need_context=True,
            )
        )
        return self._extract_csv(result)
        
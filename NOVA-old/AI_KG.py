import pandas as pd
import numpy as np
import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader, PyPDFium2Loader
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import json
import random
import networkx as nx
import seaborn as sns
from pyvis.network import Network

from df_helpers import documents2Dataframe, df2Graph, graph2Df
from Neo4j_operation import Graph


class term_network:

    def __init__(self, path):
        self.nodes = None
        self.dfg = None
        self.output_dir = None
        self.input_dir = None
        self.path = path

    @staticmethod
    def print_df(df, n=5):
        print(df.shape)
        print(df.head(n))

    @staticmethod
    def pages_to_df(pages):
        return documents2Dataframe(pages)

    @staticmethod
    def doc_load(data_path):
        input_directory = Path(data_path)
        out_path = r'./result'
        output_directory = Path(out_path)
        return input_directory, output_directory

    @staticmethod
    def chunk_text(input_directory, Loader, **kwargs):
        loader = Loader(input_directory, **kwargs)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150,
            length_function=len,
            is_separator_regex=False,
        )

        pages = splitter.split_documents(documents)
        print("数据块数量 = ", len(pages))
        return pages

    @staticmethod
    def print_pages(pages):
        docs_as_dicts = []
        for doc in pages:
            docs_as_dicts.append({
                'page_content': doc.page_content,
                'metadata': doc.metadata  # 假设文档对象有 metadata 属性
            })

        # 将字典列表转换为 JSON 格式的字符串
        json_data = json.dumps(docs_as_dicts, indent=4, ensure_ascii=False)

        # 打印 JSON 格式的数据
        print(json_data)

    @staticmethod
    def contextual_proximity(df: pd.DataFrame) -> pd.DataFrame:
        # 将数据集合转换成节点列表
        dfg_long = pd.melt(
            df, id_vars=["chunk_id"], value_vars=["node_1", "node_2"], value_name="node"
        )
        dfg_long.drop(columns=["variable"], inplace=True)

        # 以块id 为关键字的自连接 在同一文本块之间创建链接。
        dfg_wide = pd.merge(dfg_long, dfg_long, on="chunk_id", suffixes=("_1", "_2"))

        # 减少自循环
        self_loops_drop = dfg_wide[dfg_wide["node_1"] == dfg_wide["node_2"]].index
        dfg2 = dfg_wide.drop(index=self_loops_drop).reset_index(drop=True)
        # 对边缘进行分组和计数。
        dfg2 = (
            dfg2.groupby(["node_1", "node_2"])
            .agg({"chunk_id": [",".join, "count"]})
            .reset_index()
        )
        dfg2.columns = ["node_1", "node_2", "chunk_id", "count"]
        dfg2.replace("", np.nan, inplace=True)
        dfg2.dropna(subset=["node_1", "node_2"], inplace=True)
        # 边缘掉落 1 次
        dfg2 = dfg2[dfg2["count"] != 1]
        dfg2["edge"] = "contextual proximity"
        return dfg2

    def network_analyse(self):
        print('开始网络分析')
        print('---' * 100)
        self.input_dir, self.output_dir = self.doc_load(self.path)
        pages = self.chunk_text(self.input_dir, DirectoryLoader, show_progress=True)
        df = self.pages_to_df(pages)
        concepts_list = df2Graph(df, model='qwen-14b-chat')
        dfg1 = graph2Df(concepts_list)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        dfg1.to_csv(self.output_dir / "graph.csv", sep="|", index=False)
        df.to_csv(self.output_dir / "chunks.csv", sep="|", index=False)

        dfg1.replace("", np.nan, inplace=True)
        dfg1.dropna(subset=["node_1", "node_2", 'edge'], inplace=True)
        dfg1['count'] = 4
        dfg2 = self.contextual_proximity(dfg1)
        dfg = pd.concat([dfg1, dfg2], axis=0)
        self.dfg = (
            dfg.groupby(["node_1", "node_2"])
            .agg({"chunk_id": ",".join, "edge": ','.join, 'count': 'sum'})
            .reset_index()
        )
        self.nodes = pd.concat([dfg['node_1'], dfg['node_2']], axis=0).unique()

    @staticmethod
    def colors2Community(communities, palette="hls") -> pd.DataFrame:
        # 定义调色板
        p = sns.color_palette(palette, len(communities)).as_hex()
        random.shuffle(p)
        rows = []
        group = 0
        for community in communities:
            color = p.pop()
            group += 1
            for node in community:
                rows += [{"node": node, "color": color, "group": group}]
        df_colors = pd.DataFrame(rows)
        return df_colors

    def draw_network(self):
        print('开始网络绘制')
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(
                str(node)
            )

        for index, row in self.dfg.iterrows():
            G.add_edge(
                str(row["node_1"]),
                str(row["node_2"]),
                title=row["edge"],
                weight=row['count'] / 4
            )

        communities_generator = nx.community.girvan_newman(G)
        top_level_communities = next(communities_generator)
        next_level_communities = next(communities_generator)
        communities = sorted(map(sorted, next_level_communities))
        colors = self.colors2Community(communities)
        for index, row in colors.iterrows():
            G.nodes[row['node']]['group'] = row['group']
            G.nodes[row['node']]['color'] = row['color']
            G.nodes[row['node']]['size'] = G.degree[row['node']]

        graph_output_directory = "./docs/index.html"

        net = Network(
            notebook=False,
            # bgcolor="#1a1a1a",
            cdn_resources="remote",
            height="900px",
            width="100%",
            select_menu=True,
            # font_color="#cccccc",
            filter_menu=False,
        )

        net.from_nx(G)
        net.force_atlas_2based(central_gravity=0.015, gravity=-31)
        net.show_buttons(filter_=["physics"])

        net.show(graph_output_directory, notebook=False)


if __name__ == "__main__":
    network = term_network(r".\data")
    network.network_analyse()
    network.draw_network()

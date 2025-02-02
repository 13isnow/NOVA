from matplotlib import pyplot as plt
from openai import OpenAI
from pathlib import Path
import json
import pandas as pd
import networkx as nx
import seaborn as sns
from pyvis.network import Network
import random

client = OpenAI(
    api_key="sk-LS39YOgkuR2A4wRTVYnJuI3EuQFRk1fAMNw1z3H8mE0C4QFC",
    base_url="https://api.moonshot.cn/v1",
)


def kimi_API():
    file_object = client.files.create(file=Path(r"C:\Users\21531\Desktop\temp\test.txt"), purpose="file-extract")
    file_content = client.files.content(file_id=file_object.id).text

    messages = [
        {
            "role": "system",
            "content": "- Role: 信息分析专家"
                       "- Profile: 你是一位专业的信息分析专家，擅长从大量数据中提取关键信息，并建立文档之间的关系。"
                       "- Skills: 数据分析、模式识别、关键信息提取、逻辑推理。"
                       "- Goals: 帮助用户分析文档列表中的文件关系，包括但不限于文档间的延申、概括、继承、相关等联系。"
                       "- InputFormat: 提供的文本是各个文件的总结概括，展示文档的内容摘要。按照以下的形式"
                       "文件名A\n"
                       "{\n"
                       "'关键词':[若干文档的内容关键词提取],\n"
                       "'文章摘要':'若干文档的内容总结'\n"
                       "}\n\n"
                       "文件名B\n"
                       "{\n"
                       "'关键词':[若干文档的内容关键词提取],\n"
                       "'文章摘要':'若干文档的内容总结'\n"
                       "}\n\n"
                       "- OutputFormat: 你需要以文档名作为节点，用文本形式可视化文件之间的关系。"
                       "结构化的文本输出，展示文档间的逻辑关系。使得结果呈现类似树图的结构"
                       "如果你发现有文件和其他文件没有任何关系，可以从所有文件中找到一个内容相关的文件与之相连"
                       "按照以下的形式"
                       "{\n"
                       "    文档A->文档B->文档C\n"
                       "    文档A->文档D->文档E\n"
                       "    文档B->文档F\n"
                       "}\n"
                       "- Workflow:"
                       " 1. 接收并解析用户提供的文件列表。"
                       " 2. 分析并建立文件间的逻辑关系"
                       " 3. 以结构化格式返回文档关系分析结果。"
                       "- Examples:"
                       "    - input:"
                       "    文件A\n"
                       "        {\n"
                       "        '关键词': ['经济', '发展'], \n"
                       "        '文章摘要': '讨论了经济增长的策略。'\n"
                       "        }\n"
                       "    文件B\n"
                       "        {\n"
                       "        '关键词': ['市场', '投资'], \n"
                       "        '文章摘要': '分析了市场趋势和投资机会。'\n"
                       "        }\n"
                       "    - output:"
                       "    文档A->文档B"
        },
        {
            "role": "system",
            "content": file_content,
        },
        {"role": "user",
         "content": "请开始，注意你要以结构化的方式输出文件之间的关系，你不需要提供额外解释。为了保证丰富性，请尽量多连接一些节点"},
        {
            "role": "assistant",
            "content": "{\n",
            "partial": True
        },
    ]

    # 然后调用 chat-completion, 获取 Kimi 的回答
    completion = client.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
    )
    with open('kimi.json', 'w', encoding='utf-8') as file:
        print(completion.choices[0].message)
        file.write('{\n' + completion.choices[0].message.content)


def json_to_df(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        relations = []
        for file1, file2_s in data.items():
            for file2, relation in file2_s['连接'].items():
                relations.append([file1, file2, relation])

        return pd.DataFrame(relations, columns=['file1', 'file2', 'relation'])


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


def draw_network(df, nodes):
    print('开始网络绘制')
    G = nx.Graph()
    for node in nodes:
        G.add_node(
            str(node)
        )

    for index, row in df.iterrows():
        G.add_edge(
            str(row["file1"]),
            str(row["file2"]),
            label=row["relation"],
        )

    communities_generator = nx.community.girvan_newman(G)
    top_level_communities = next(communities_generator)
    next_level_communities = next(communities_generator)
    communities = sorted(map(sorted, next_level_communities))
    colors = colors2Community(communities)
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


if __name__ == '__main__':
    # kimi_API()
    df = json_to_df(r"C:\Users\21531\Desktop\yuque\kimi.json")
    nodes = pd.concat([df['file1'], df['file2']], axis=0).unique()
    draw_network(df, nodes)

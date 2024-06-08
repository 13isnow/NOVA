import pandas as pd
from pyvis.network import Network
import networkx as nx
import random
import seaborn as sns


def csv_to_df(file_path):
    return pd.read_csv(file_path, sep='|')


def doc_network():
    chunk_df = csv_to_df(r"C:\Users\21531\Desktop\yuque\result\chunks.csv")
    graph_df = csv_to_df(r"C:\Users\21531\Desktop\yuque\result\graph.csv")

    df = pd.merge(chunk_df, graph_df, on='chunk_id', how='right')
    df['source'] = df['source'].str.extract(r'data\\(.*?)\.txt$')

    node_to_sources = {}

    # 遍历DataFrame中的每一行，构建node到sources的映射
    for index, row in df.iterrows():
        # 为node1添加source
        if row['node_1'] not in node_to_sources:
            node_to_sources[row['node_1']] = []
        node_to_sources[row['node_1']].append(row['source'])

        # 为node2添加source
        if row['node_2'] not in node_to_sources:
            node_to_sources[row['node_2']] = []
        node_to_sources[row['node_2']].append(row['source'])

    # 找出所有通过共享节点连接的sources
    source_links = []
    for node, sources in node_to_sources.items():
        # 如果一个节点关联了多个sources，则添加这些sources之间的所有组合
        if len(sources) > 1:
            for i in range(len(sources)):
                for j in range(i + 1, len(sources)):
                    source_links.append((sources[i], sources[j]))

    # 构建一个新的DataFrame来存储source之间的关联
    df_links = pd.DataFrame(source_links, columns=['source1', 'source2'])
    df_unique = df_links.drop_duplicates().reset_index(drop=True)
    res = df_unique.query('source1 != source2')
    nodes = pd.concat([res['source1'], res['source2']], axis=0).unique()
    return res, nodes


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
            str(row["source1"]),
            str(row["source2"]),
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

    net.show(graph_output_directory, notebook=False)


if __name__ == '__main__':
    a, b = doc_network()
    draw_network(a, b)

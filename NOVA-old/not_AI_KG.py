import re
import Wiki_search
from Neo4j_operation import Graph, Node

config = {
    'uri': "bolt://localhost:7687",
    'user': "neo4j",
    'password': "12345678"
}


def extract_data(path):
    def regex(string):
        return eval('{' + string + '}')

    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
        pattern = r'\{(.*?)\}'
        match = re.findall(pattern, text, re.DOTALL)
        return map(regex, match)


if __name__ == '__main__':
    documents = extract_data(r"C:\Users\21531\Desktop\test2.txt")
    graph = Graph(config)
    for document in documents:
        for key_word in document['关键词']:
            graph.MERGE_NODE('key_word', term=key_word)
            tech_terms = Wiki_search.Wiki_links(key_word)
            for term in tech_terms:
                graph.MERGE_NODE('expert', term=term)
                node1 = Node('key_word', 'term', key_word)
                node2 = Node('expert', 'term', term)
                graph.CREATE_REL(node1, node2)

    graph.commit()



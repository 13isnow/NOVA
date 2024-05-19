from neo4j import GraphDatabase


class Node:

    def __init__(self, label, attr, name):
        self.label = label
        self.attr = attr
        self.name = name


class Graph:

    def __init__(self, config):
        self.driver = GraphDatabase.driver(config['uri'], auth=(config['user'], config['password']))
        self.session = self.driver.session()
        self.tx = self.session.begin_transaction()

    def commit(self):
        self.tx.commit()

    def DELETE_ALL(self):
        query = "MATCH (n) DETACH DELETE n"
        self.tx.run(query)

    def MERGE_NODE(self, label, **kwargs):
        props = ", ".join(f"{key}: ${key}" for key in kwargs)
        query = f"MERGE (n:{label} {{{props}}})"
        params = {key: val for key, val in kwargs.items()}

        self.tx.run(query, **params)

    def CREATE_REL(self, node1, node2, relationship_type='related'):
        query = (f"MATCH (a:`{node1.label}` {{{node1.attr}: $name1}}), "
                 f"(b:`{node2.label}` {{{node2.attr}: $name2}})"
                 f"CREATE (a)-[:`{relationship_type}`]->(b)")
        self.tx.run(query, name1=node1.name, name2=node2.name)

    def MATCH_NODE_DATA(self, label, attr, key):
        query = f"MATCH (n:{label}) WHERE n.{attr} = $key RETURN n"
        info = self.tx.run(query, key=key)
        return info.data()[0]['n']

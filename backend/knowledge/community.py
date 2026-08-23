import networkx as nx


def detect_communities(entities, relationships):
    graph = nx.Graph()

    for entity in entities:
        graph.add_node(
            entity["text"],
            type=entity["type"]
        )

    for relationship in relationships:
        graph.add_edge(
            relationship["source"],
            relationship["target"]
        )

    communities = nx.community.greedy_modularity_communities(graph)

    return [
        list(community)
        for community in communities
    ]

def detect_graph_communities(graph):
    entities, relationships = graph.get_graph_data()

    return detect_communities(
        entities,
        relationships
    )
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

    result = []

    for community in communities:
        community_entities = [
            entity
            for entity in entities
            if entity["text"] in community
        ]

        community_relationships = [
            relationship
            for relationship in relationships
            if relationship["source"] in community
            and relationship["target"] in community
        ]

        result.append({
            "entities": community_entities,
            "relationships": community_relationships
        })

    return result


def detect_graph_communities(graph):
    entities, relationships = graph.get_graph_data()

    return detect_communities(
        entities,
        relationships
    )
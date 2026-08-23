from .community import detect_graph_communities
from .community_summarizer import summarize_community
from .graph import Neo4jClient


def build_communities():
    graph = Neo4jClient()

    try:
        communities = detect_graph_communities(graph)

        for index, community in enumerate(communities, 1):
            entities = community["entities"]
            relationships = community["relationships"]

            print("COMMUNITY:", index)
            print("ENTITIES:", entities)

            summary = summarize_community(
                entities,
                relationships
            )

            graph.create_community(
                f"community-{index}",
                entities,
                summary
            )
    finally:
        graph.close()
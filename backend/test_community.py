import os
import django

# Load Django settings BEFORE importing anything that uses settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


from knowledge.community import detect_graph_communities
from knowledge.graph import Neo4jClient


graph = Neo4jClient()

communities = detect_graph_communities(graph)

graph.close()

for index, community in enumerate(communities, 1):
    print(f"Community {index}:")
    print(community)
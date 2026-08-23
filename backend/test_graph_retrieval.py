from knowledge.graph import Neo4jClient


graph = Neo4jClient()

data = graph.get_chunk_graph([
    "35-1",
    "35-2"
])

graph.close()

for item in data:
    print(item)
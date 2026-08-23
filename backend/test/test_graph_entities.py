from knowledge.graph import Neo4jClient


graph = Neo4jClient()

entity = {
    "text": "دانشگاه تهران",
    "type": "ORG"
}

graph.create_entity(
    "test-1",
    entity
)

graph.close()

print("Entity write successful")
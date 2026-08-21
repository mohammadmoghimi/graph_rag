import json

from langchain_ollama import ChatOllama


ENTITY_TYPES = [
    "Person",
    "Organization",
    "Location",
    "Event",
    "Concept",
    "Date",
]

RELATIONSHIP_TYPES = [
    "RELATED_TO",
    "PART_OF",
    "LOCATED_IN",
    "WORKS_FOR",
    "FOUNDED_BY",
    "FOUNDED_IN",
]


def get_extractor_llm():
    return ChatOllama(
        model="gemma2:2b",
        temperature=0
    )


def build_extraction_prompt(text):
    entity_types = ", ".join(ENTITY_TYPES)
    relationship_types = ", ".join(RELATIONSHIP_TYPES)

    return f"""
Extract entities and relationships from the following Persian text.

Allowed entity types:
{entity_types}

Allowed relationship types:
{relationship_types}

Return ONLY valid JSON in exactly this format:

{{
    "entities": [
        {{
            "name": "entity name",
            "type": "entity type"
        }}
    ],
    "relationships": [
        {{
            "source": "source entity",
            "type": "relationship type",
            "target": "target entity"
        }}
    ]
}}

Do not add explanations.
Do not use markdown.
Do not invent information that is not present in the text.

Text:
{text}
"""


def extract_graph_data(text):
    llm = get_extractor_llm()

    prompt = build_extraction_prompt(text)
    response = llm.invoke(prompt)

    try:
        data = parse_response(response.content)

        return validate_graph_data(data)
        
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Gemma returned invalid JSON: {response.content}"
        ) from error
    
def parse_response(content):
    content = content.strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    try:
        return json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Gemma returned invalid JSON: {content}"
        ) from error

def validate_graph_data(data):
    if not isinstance(data, dict):
        raise ValueError("Graph data must be an object.")

    entities = data.get("entities", [])
    relationships = data.get("relationships", [])

    if not isinstance(entities, list):
        raise ValueError("Entities must be a list.")

    if not isinstance(relationships, list):
        raise ValueError("Relationships must be a list.")

    valid_entities = [
        entity
        for entity in entities
        if (
            isinstance(entity, dict)
            and entity.get("name")
            and entity.get("type") in ENTITY_TYPES
        )
    ]

    valid_relationships = [
        relationship
        for relationship in relationships
        if (
            isinstance(relationship, dict)
            and relationship.get("source")
            and relationship.get("target")
            and relationship.get("type") in RELATIONSHIP_TYPES
        )
    ]

    return {
        "entities": valid_entities,
        "relationships": valid_relationships
    }
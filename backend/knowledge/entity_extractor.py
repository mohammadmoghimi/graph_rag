import spacy


class EntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("fa_core_news_sm")

    def extract(self, text):
        doc = self.nlp(text)

        entities = []

        for entity in doc.ents:
            text = entity.text.strip()

            if entity.label_ not in {"PER", "ORG", "LOC"}:
                continue

            if len(text) < 2:
                continue

            if text.isdigit():
                continue

            entities.append({
                "text": text,
                "type": entity.label_
            })

        return entities
    
    def extract_relationships(self, text):
        doc = self.nlp(text)
        entities = {}

        for entity in doc.ents:
            key = (entity.text.strip(), entity.label_)

            if key not in entities:
                entities[key] = {
                    "text": entity.text.strip(),
                    "type": entity.label_
                }

        relationships = []

        entity_list = list(entities.values())

        for i, source in enumerate(entity_list):
            for target in entity_list[i + 1:]:
                relationships.append({
                    "source": source["text"],
                    "source_type": source["type"],
                    "target": target["text"],
                    "target_type": target["type"]
                })

        return relationships
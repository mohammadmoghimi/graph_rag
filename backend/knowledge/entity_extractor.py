import spacy


class EntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("fa_core_news_sm")

    def extract(self, text):
        doc = self.nlp(text)

        entities = []

        for entity in doc.ents:
            text = entity.text.strip()

            if entity.label_ not in {"PER", "ORG", "LOC","DAT"}:
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

#         import spacy

# class EntityExtractor:
#     def __init__(self):
#         self.nlp = spacy.load("fa_core_news_sm")

#     def extract(self, text):
#         doc = self.nlp(text)

#         entities = []

#         for entity in doc.ents:
#             text = entity.text.strip()

#             if entity.label_ not in {"PER", "ORG", "LOC", "DAT"}:
#                 continue

#             if len(text) < 2 or text.isdigit():
#                 continue

#             entities.append({
#                 "text": text,
#                 "type": entity.label_
#             })

#         return entities

#     def extract_relationships(self, text):
#         doc = self.nlp(text)

#         entities = [
#             {
#                 "text": entity.text.strip(),
#                 "type": entity.label_
#             }
#             for entity in doc.ents
#             if entity.label_ in {"PER", "ORG", "LOC", "DAT"}
#             and len(entity.text.strip()) >= 2
#         ]

#         relationships = []

#         for sentence in doc.sents:
#             sentence_entities = [
#                 entity for entity in entities
#                 if entity["text"] in sentence.text
#             ]

#             if len(sentence_entities) < 2:
#                 continue

#             sentence_text = sentence.text

#             relation_rules = [
#                 (["در", "واقع شده در", "قرار دارد در", "واقع در"], "LOCATED_IN"),
#                 (["در شهر"], "LOCATED_IN"),
#                 (["در کشور"], "LOCATED_IN"),
#                 (["متعلق به"], "BELONGS_TO"),
#                 (["وابسته به"], "BELONGS_TO"),
#                 (["بخشی از"], "PART_OF"),
#                 (["تاسیس توسط", "تأسیس توسط"], "FOUNDED_BY"),
#                 (["توسط"], "ASSOCIATED_WITH"),
#                 (["مدیر", "رییس", "رئیس"], "LED_BY"),
#                 (["عضو"], "MEMBER_OF"),
#                 (["همکاری با"], "COLLABORATES_WITH"),
#                 (["مرتبط با"], "RELATED_TO"),
#             ]

#             for patterns, relation_type in relation_rules:
#                 if any(pattern in sentence_text for pattern in patterns):
#                     source = sentence_entities[0]
#                     target = sentence_entities[1]

#                     relationships.append({
#                         "source": source["text"],
#                         "source_type": source["type"],
#                         "target": target["text"],
#                         "target_type": target["type"],
#                         "type": relation_type
#                     })

#         return relationships
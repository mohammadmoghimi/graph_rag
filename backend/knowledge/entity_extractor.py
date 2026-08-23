import spacy


class EntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("fa_core_news_sm")

    def extract(self, text):
        doc = self.nlp(text)

        return [
            {
                "text": entity.text,
                "type": entity.label_
            }
            for entity in doc.ents
        ]
    
    def extract_relationships(self, text):
        doc = self.nlp(text)
        relationships = []

        for sentence in doc.sents:
            entities = list(sentence.ents)

            for i, source in enumerate(entities):
                for target in entities[i + 1:]:
                    if source.text != target.text:
                        relationships.append({
                            "source": source.text,
                            "source_type": source.label_,
                            "target": target.text,
                            "target_type": target.label_
                        })

        return relationships
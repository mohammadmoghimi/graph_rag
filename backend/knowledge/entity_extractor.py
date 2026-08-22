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
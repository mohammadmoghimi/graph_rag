from knowledge.entity_extractor import EntityExtractor


extractor = EntityExtractor()

text = "دانشگاه تهران یکی از قدیمی‌ترین دانشگاه‌های ایران است."

entities = extractor.extract(text)

for entity in entities:
    print(entity)
from knowledge.community_summarizer import summarize_community


entities = [
    {"text": "دانشگاه تهران", "type": "ORG"},
    {"text": "ایران", "type": "LOC"},
    {"text": "شهر تهران", "type": "LOC"}
]

relationships = [
    {
        "source": "دانشگاه تهران",
        "target": "ایران"
    },
    {
        "source": "دانشگاه تهران",
        "target": "شهر تهران"
    }
]

summary = summarize_community(
    entities,
    relationships
)

print(summary)
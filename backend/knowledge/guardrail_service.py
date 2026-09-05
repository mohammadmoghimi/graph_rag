from transformers import pipeline


class GuardrailService:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="HamidRezaei/Persian-Offensive-Language-Detection"
        )

    def is_allowed(self, text):
        result = self.classifier(text)[0]
        return result["score"] < 0.5


guardrail_service = GuardrailService()
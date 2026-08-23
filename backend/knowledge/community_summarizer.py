from .llm import generate


def summarize_community(entities, relationships):
    entity_text = "\n".join(
        f"- {entity['text']})"
        for entity in entities
    )

    relationship_text = "\n".join(
        f"- {item['source']} مرتبط با {item['target']}"
        for item in relationships
    )

    prompt = f"""
تو یک خلاصه‌ساز گراف دانش هستی.

موجودیت‌ها:
{entity_text}

روابط:
{relationship_text}

یک جمله فارسی بنویس که رابطه اصلی بین این موجودیت‌ها را توضیح دهد.

قوانین:
- فقط یک جمله.
- فقط اطلاعات موجود در ورودی.
- نام موجودیت‌ها را پشت سر هم تکرار نکن.
- متن ورودی را بازنویسی نکن.
- هیچ توضیح اضافی نده.
"""

    return generate(prompt)
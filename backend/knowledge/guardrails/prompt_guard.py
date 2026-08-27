import re


class PromptBlockedError(Exception):
    pass


class PromptGuard:
    SYSTEM_PATTERNS = [
        r"\bsystem\s+(prompt|instruction|instructions|message)\b",
        r"\b(hidden|secret|internal)\s+(prompt|instructions)\b",
        r"\b(show|reveal|give|provide|print|display|tell)\b.{0,40}\b(system|hidden|secret)\b",
        r"\bwhat\s+(is|are)\s+your\s+(instructions|rules|prompt)\b",
        r"\b(ignore|forget|disregard|override)\b.{0,60}\b(previous|prior|system|above)\b",
        r"\bpretend\s+you\s+(have|are)\b.{0,50}\bno\s+rules\b",

        r"دستور.{0,20}سیستم",
        r"پیام.{0,20}سیستم",
        r"دستورالعمل.{0,30}(سیستم|اصلی|پنهان)",
        r"(دستور|قوانین).{0,30}(قبلی|بالا|سیستم).{0,30}(نادیده|فراموش|لغو)",
        r"(پرامپت|دستور).{0,30}(پنهان|مخفی|داخلی)",
    ]

    EXFILTRATION_PATTERNS = [
        r"\b(show|list|give|export|dump|extract|reveal|provide)\b.{0,50}"
        r"\b(all|every|entire|complete)\b.{0,50}"
        r"\b(documents?|chunks?|data|database|knowledge\s*base)\b",

        r"\b(dump|export|extract)\b.{0,30}\b(database|knowledge\s*base|data)\b",
        r"\breveal\b.{0,40}\b(source|original)\s+(documents?|content)\b",
        r"\bshow\b.{0,30}\b(all|every)\b.{0,30}\bsource\b",

        r"همه.{0,30}(اسناد|مدارک|چانک|داده|اطلاعات)",
        r"تمام.{0,30}(اسناد|مدارک|چانک|داده|اطلاعات)",
        r"(کل|تمام|همه).{0,30}(پایگاه.?دانش|پایگاه.?داده)",
        r"(استخراج|خروجی|نمایش|نشان).{0,30}"
        r"(همه|تمام|کل).{0,30}(اطلاعات|داده|اسناد|چانک)",
        r"(اسناد|چانک).{0,30}(اصلی|منبع|خام)",
    ]

    @classmethod
    def normalize(cls, text):
        text = text.lower()
        text = text.replace("\u200c", "")
        text = text.replace("\u200d", "")
        text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def matches(cls, text, patterns):
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

    @classmethod
    def check(cls, prompt):
        normalized = cls.normalize(prompt)

        if cls.matches(normalized, cls.SYSTEM_PATTERNS):
            raise PromptBlockedError("این نوع درخواست مجاز نیست.")

        if cls.matches(normalized, cls.EXFILTRATION_PATTERNS):
            raise PromptBlockedError("این نوع درخواست مجاز نیست.")
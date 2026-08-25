from chat.chat_service import answer_question
from dotenv import load_dotenv
import django
import os
# Load Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
load_dotenv()

answer = answer_question(
    "فصل دوم سریال pluribus کی پخش میشود ؟",
    [51]
)

print(answer)
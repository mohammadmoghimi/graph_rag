import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def generate(prompt):
    endpoint = os.getenv("LLM_ENDPOINT_GENERATE")
    if not endpoint:
        raise ValueError("LLM_ENDPOINT_GENERATE environment variable is not set")
    
    response = requests.post(
        endpoint,
        json={"prompt": prompt},
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"]
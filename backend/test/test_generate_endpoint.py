import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Optional: Add the project root to path if needed (not required for this test)
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge.llm import generate


def test_generate():
    print("Testing LLM generation endpoint...")
    print("-" * 50)

    # Check if endpoint is set
    endpoint = os.getenv("LLM_ENDPOINT_GENERATE")
    if not endpoint:
        print("❌ LLM_ENDPOINT_GENERATE is not set in .env")
        return False

    print(f"✅ Endpoint found: {endpoint}")

    # Test with a simple Persian prompt
    test_prompt = "سلام، نام من چیست؟"

    print(f"\n📝 Sending prompt: {test_prompt}")
    print("⏳ Waiting for response (timeout: 120s)...")

    try:
        response = generate(test_prompt)
        print("\n✅ Response received:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        print(f"\n📊 Response length: {len(response)} characters")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_generate()
    sys.exit(0 if success else 1)
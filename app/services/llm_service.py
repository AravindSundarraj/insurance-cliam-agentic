from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()  # <-- this loads the .env file
print(os.getenv("OPENAI_API_KEY"))
# Step 1.2 — LLM Service (Centralized LLM Calls)
# Why Temperature = 0?

# Because:

# This is structured extraction.
# We want consistency.
# Not creativity.

_client = None
# Summary
# Root Cause: The OpenAI client was being initialized at module import time with an undefined OPENAI_API_KEY environment variable, causing an immediate failure.

# Fix Applied: Refactored the code to use lazy initialization:

# The client is now only initialized when call_llm() is first called
# Better error messaging if the API key is missing
# The module can now be imported for testing without the API key set

def _get_client():
    """Lazy initialize the OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is not set. "
                "Please set it before using the LLM service."
            )
        _client = OpenAI(api_key=api_key)
    return _client

def call_llm(prompt: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an insurance policy extraction assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content
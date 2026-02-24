from openai import OpenAI
import os

# Step 1.2 — LLM Service (Centralized LLM Calls)
# Why Temperature = 0?

# Because:

# This is structured extraction.
# We want consistency.
# Not creativity.

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an insurance policy extraction assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content
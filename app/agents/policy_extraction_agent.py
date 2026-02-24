# Step 1.4 — Policy Extraction Agent
import json
from app.schemas.policy_schema import Policy
from app.services.llm_service import call_llm
from app.services.phoenix_tracer import traced_llm_call

# What This Agent Does

# Builds structured extraction prompt

# Calls LLM (with Phoenix tracing)

# Parses JSON

# Validates with Pydantic

# Returns Policy object

# Clean.
# Single responsibility.
# Traceable.

def extract_policy_details(policy_text: str) -> Policy:

    prompt = f"""
    Extract the following information from the insurance policy text:

    1. Coverage types
    2. Exclusions
    3. Deductible amount (numeric only)
    4. Maximum coverage limit (numeric only)
    5. Policy number (if present)

    Return strictly valid JSON in this format:

    {{
        "coverage_types": [],
        "exclusions": [],
        "deductible": 0,
        "coverage_limit": 0,
        "policy_number": ""
    }}

    Policy Text:
    {policy_text}
    """

    raw_output = traced_llm_call(prompt, call_llm)

    try:
        parsed = json.loads(raw_output)
        policy = Policy(**parsed)
        return policy
    except Exception as e:
        raise ValueError(f"Policy extraction failed: {e}")
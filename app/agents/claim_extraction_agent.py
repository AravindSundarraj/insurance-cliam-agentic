# What This Agent Does

# Reads free text

# Converts into structured facts

# Validates structure

# Logs via Phoenix

# It does NOT:

# Approve claim

# Calculate payout

# Check coverage

# Pure extraction.

import json
from app.schemas.claim_schema import Claim
from app.services.llm_service import call_llm
from app.services.phoenix_tracer import traced_llm_call

def extract_claim_details(claim_text: str) -> Claim:

    prompt = f"""
    Extract the following from the claim description:

    1. Incident type (e.g., theft, fire, flood, accident)
    2. Incident date (if mentioned)
    3. Claimed amount (numeric only)
    4. Cause of incident
    5. Full description summary

    Return strictly valid JSON in this format:

    {{
        "incident_type": "",
        "incident_date": "",
        "claimed_amount": 0,
        "cause": "",
        "description": ""
    }}

    Claim Text:
    {claim_text}
    """

    raw_output = traced_llm_call(prompt, call_llm,'claim_extraction_llm_call')

    parsed = json.loads(raw_output)

    return Claim(**parsed)
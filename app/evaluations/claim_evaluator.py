from app.schemas.claim_schema import Claim
from app.services.llm_service import call_llm

from app.services.phoenix_tracer import tracer

# ----------------------
# Basic Validation
# ----------------------

def validate_claim_amount(claim: Claim) -> bool:
    """Check claimed_amount is positive"""
    return claim.claimed_amount > 0

def validate_claim_date(claim: Claim) -> bool:
    """Check incident_date exists"""
    return claim.incident_date is not None and len(claim.incident_date.strip()) > 0

def validate_required_fields(claim: Claim) -> bool:
    """Ensure all required text fields are filled"""
    required_fields = [claim.incident_type, claim.cause, claim.description]
    return all(field is not None and field.strip() != "" for field in required_fields)

# ----------------------
# Consistency Check
# ----------------------

def check_basic_consistency(claim: Claim) -> bool:
    """
    Basic logical check: e.g., if incident_type=flood, cause should reference water/rain
    """
    if claim.incident_type.lower() == "flood":
        return "rain" in claim.cause.lower() or "water" in claim.cause.lower()
    # Add more rules later
    return True

# ----------------------
# Faithfulness Evaluation (LLM-as-Judge)
# ----------------------

def evaluate_claim_faithfulness(claim_text: str, extracted_claim: dict) -> str:
    """
    Checks if extracted claim data is actually supported by claim text
    Returns: FAITHFUL, PARTIALLY_FAITHFUL, NOT_FAITHFUL
    """
    prompt = f"""
    Given the original claim text and extracted structured data,
    determine if the extracted information is fully supported by the text.

    Claim Text:
    {claim_text}

    Extracted Data:
    {extracted_claim}

    Answer only with one of:
    - FAITHFUL
    - PARTIALLY_FAITHFUL
    - NOT_FAITHFUL
    """

    result = call_llm(prompt)
    return result.strip()

# ----------------------
# Master Evaluation Function with OpenTelemetry Tracing
# ----------------------

def evaluate_claim(claim: Claim, claim_text: str) -> dict:
    """
    Runs all Step 2 evaluation checks
    Each check is wrapped in OpenTelemetry span for observability
    """

    with tracer.start_as_current_span("claim_numeric_validation"):
        amount_valid = validate_claim_amount(claim)

    with tracer.start_as_current_span("claim_field_completeness"):
        fields_valid = validate_required_fields(claim)

    with tracer.start_as_current_span("claim_consistency_check"):
        consistency_valid = check_basic_consistency(claim)

    with tracer.start_as_current_span("claim_faithfulness_check"):
        faithfulness = evaluate_claim_faithfulness(
            claim_text,
            claim.model_dump()
        )

    return {
        "amount_valid": amount_valid,
        "fields_valid": fields_valid,
        "consistency_valid": consistency_valid,
        "faithfulness": faithfulness
    }


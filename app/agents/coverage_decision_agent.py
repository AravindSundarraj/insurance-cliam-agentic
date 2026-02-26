from app.services.phoenix_tracer import tracer
from openinference.semconv.trace import SpanAttributes
from app.schemas.policy_schema import Policy
from app.schemas.claim_schema import Claim
from app.services.llm_service import call_llm


def generate_reasoning_llm(policy: Policy, claim: Claim, decision: dict):
    """
    Generate human-readable explanation using LLM.
    """

    prompt = f"""
You are an insurance claim decision assistant.

Policy Details:
- Coverage Types: {policy.coverage_types}
- Exclusions: {policy.exclusions}
- Deductible: {policy.deductible}
- Coverage Limit: {policy.coverage_limit}

Claim Details:
- Incident Type: {claim.incident_type}
- Claimed Amount: {claim.claimed_amount}
- Incident Date: {claim.incident_date}
- Cause: {claim.cause}

Decision:
- Status: {decision['status']}
- Approved Amount: {decision['approved_amount']}

Explain clearly why this decision was made.
Keep it concise and professional.
"""

    with tracer.start_as_current_span("coverage_reasoning_llm_call") as span:
        span.set_attribute(SpanAttributes.INPUT_VALUE, prompt)
        response = call_llm(prompt)
        span.set_attribute(SpanAttributes.OUTPUT_VALUE, response)

    return response


def coverage_decision(policy: Policy, claim: Claim):
    """
    Determine final coverage decision using deterministic logic.
    """

    decision = {
        "status": None,
        "approved_amount": 0
    }

    # ----------------------------
    # 1️⃣ Coverage Type Check
    # ----------------------------
    with tracer.start_as_current_span("coverage_type_check") as span:
        is_covered = claim.incident_type.lower() in [
            c.lower() for c in policy.coverage_types
        ]

        span.set_attribute("coverage.is_covered", is_covered)

        if not is_covered:
            decision["status"] = "REJECTED"
            decision["approved_amount"] = 0
            span.set_attribute("coverage.rejection_reason", "Incident type not covered")

            explanation = generate_reasoning_llm(policy, claim, decision)

            return {**decision, "reason": explanation}

    # ----------------------------
    # 2️⃣ Exclusion Check
    # ----------------------------
    with tracer.start_as_current_span("exclusion_check") as span:
        is_excluded = claim.incident_type.lower() in [
            e.lower() for e in policy.exclusions
        ]

        span.set_attribute("coverage.is_excluded", is_excluded)

        if is_excluded:
            decision["status"] = "REJECTED"
            decision["approved_amount"] = 0
            span.set_attribute("coverage.rejection_reason", "Incident explicitly excluded")

            explanation = generate_reasoning_llm(policy, claim, decision)

            return {**decision, "reason": explanation}

    # ----------------------------
    # 3️⃣ Deductible Calculation
    # ----------------------------
    with tracer.start_as_current_span("deductible_calculation") as span:
        payable = claim.claimed_amount - policy.deductible
        span.set_attribute("coverage.after_deductible", payable)

        if payable <= 0:
            decision["status"] = "REJECTED"
            decision["approved_amount"] = 0
            span.set_attribute("coverage.rejection_reason", "Amount below deductible")

            explanation = generate_reasoning_llm(policy, claim, decision)

            return {**decision, "reason": explanation}

    # ----------------------------
    # 4️⃣ Coverage Limit Enforcement
    # ----------------------------
    with tracer.start_as_current_span("coverage_limit_check") as span:
        if payable > policy.coverage_limit:
            approved_amount = policy.coverage_limit
            decision["status"] = "PARTIALLY_APPROVED"
        else:
            approved_amount = payable
            decision["status"] = "APPROVED"

        span.set_attribute("coverage.final_approved_amount", approved_amount)

        decision["approved_amount"] = approved_amount

    # ----------------------------
    # 5️⃣ Generate Explanation
    # ----------------------------
    explanation = generate_reasoning_llm(policy, claim, decision)

    return {
        **decision,
        "reason": explanation
    }
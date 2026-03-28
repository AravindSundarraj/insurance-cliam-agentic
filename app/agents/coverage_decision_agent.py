from app.services.phoenix_tracer import tracer
from openinference.semconv.trace import SpanAttributes
from app.schemas.policy_schema import Policy
from app.schemas.claim_schema import Claim
from app.services.llm_service import call_llm
from app.evaluations.phoenix_evaluator import (
    evaluate_decision_reasoning,
    evaluate_faithfulness_score,
)
from phoenix.trace import suppress_tracing
from phoenix.client import Client
from opentelemetry import trace as trace_api
import pandas as pd

client = Client()
# -------------------------------------------------
# LLM Explanation Generator
# -------------------------------------------------
def generate_reasoning_llm(policy: Policy, claim: Claim, decision: dict) -> str:
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


# -------------------------------------------------
# Main Coverage Decision Logic
# -------------------------------------------------
def coverage_decision(policy: Policy, claim: Claim) -> dict:
    """
    Determine final coverage decision using deterministic logic.
    Also performs LLM explanation + Phoenix evaluations.
    """

    decision = {
        "status": None,
        "approved_amount": 0,
    }

    # -------------------------------------------------
    # 1️⃣ Coverage Type Check
    # -------------------------------------------------
    with tracer.start_as_current_span("coverage_type_check") as span:
        is_covered = claim.incident_type.lower() in [
            c.lower() for c in policy.coverage_types
        ]

        span.set_attribute("coverage.is_covered", is_covered)

        if not is_covered:
            decision["status"] = "REJECTED"
            decision["approved_amount"] = 0
            span.set_attribute("coverage.rejection_reason", "Incident type not covered")

            return _finalize_decision(policy, claim, decision)

    # -------------------------------------------------
    # 2️⃣ Exclusion Check
    # -------------------------------------------------
    with tracer.start_as_current_span("exclusion_check") as span:
        is_excluded = claim.incident_type.lower() in [
            e.lower() for e in policy.exclusions
        ]

        span.set_attribute("coverage.is_excluded", is_excluded)

        if is_excluded:
            decision["status"] = "REJECTED"
            decision["approved_amount"] = 0
            span.set_attribute("coverage.rejection_reason", "Incident explicitly excluded")

            return _finalize_decision(policy, claim, decision)

    # -------------------------------------------------
    # 3️⃣ Deductible Calculation
    # -------------------------------------------------
    with tracer.start_as_current_span("deductible_calculation") as span:
        payable = claim.claimed_amount - policy.deductible
        span.set_attribute("coverage.after_deductible", payable)

        if payable <= 0:
            decision["status"] = "REJECTED"
            decision["approved_amount"] = 0
            span.set_attribute("coverage.rejection_reason", "Amount below deductible")

            return _finalize_decision(policy, claim, decision)

    # -------------------------------------------------
    # 4️⃣ Coverage Limit Enforcement
    # -------------------------------------------------
    with tracer.start_as_current_span("coverage_limit_check") as span:
        if payable > policy.coverage_limit:
            approved_amount = policy.coverage_limit
            decision["status"] = "PARTIALLY_APPROVED"
        else:
            approved_amount = payable
            decision["status"] = "APPROVED"

        decision["approved_amount"] = approved_amount
        span.set_attribute("coverage.final_approved_amount", approved_amount)

    return _finalize_decision(policy, claim, decision)


# -------------------------------------------------
# Finalization: Explanation + Evaluation Layer
# -------------------------------------------------
def _finalize_decision(policy: Policy, claim: Claim, decision: dict) -> dict:
    """
    Generates explanation and runs Phoenix evaluations.
    """

    # 1️⃣ Generate LLM explanation
    explanation = generate_reasoning_llm(policy, claim, decision)

    # Build context for faithfulness check
    context = f"""
Policy:
Coverage Types: {policy.coverage_types}
Exclusions: {policy.exclusions}
Deductible: {policy.deductible}
Coverage Limit: {policy.coverage_limit}

Claim:
Incident Type: {claim.incident_type}
Claimed Amount: {claim.claimed_amount}
Incident Date: {claim.incident_date}
Cause: {claim.cause}

Decision:
Status: {decision['status']}
Approved Amount: {decision['approved_amount']}
"""

    # 2️⃣ Reasoning Quality Evaluation
    with tracer.start_as_current_span("coverage_reasoning_evaluation") as span:
        reasoning_quality = evaluate_decision_reasoning(
            policy_text=str(policy),
            decision_reason=explanation,
        )
        span.set_attribute("evaluation.reasoning_quality", reasoning_quality)

    with tracer.start_as_current_span("coverage_faithfulness_evaluation") as span:
        faithfulness_score = evaluate_faithfulness_score(
            context=context,
            explanation=explanation,
            original_input=str(policy)
        )

        span.set_attribute("evaluation.faithfulness_score", faithfulness_score.score)

        span_id = span.get_span_context().span_id
        span_id_hex = format(span_id, '032x')

        annotations_df = pd.DataFrame([{
            "span_id": span_id_hex,
            "name": "faithfulness",
            "annotator_kind": "LLM",
            "label": faithfulness_score.label,
            "score": faithfulness_score.score,
            "explanation": faithfulness_score.explanation,
        }])
        client.spans.log_span_annotations_dataframe(dataframe=annotations_df)

    return {  # 4 spaces indent (inside def, outside with)
        **decision,
        "reason": explanation,
        "reasoning_quality": reasoning_quality,
        "faithfulness_score": faithfulness_score.score,
    }


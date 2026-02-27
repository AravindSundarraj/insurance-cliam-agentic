from app.schemas.policy_schema import Policy
from app.schemas.claim_schema import Claim
from app.services.phoenix_tracer import tracer
from openinference.semconv.trace import SpanAttributes
from app.services.llm_service import call_llm


def generate_final_report_llm(
    policy: Policy,
    claim: Claim,
    coverage_result: dict,
    fraud_risk_result: dict
):
    """
    Uses LLM to generate a final structured insurance report.
    """

    prompt = f"""
You are an insurance reporting assistant.

Create a professional insurance claim report using the information below.

Policy Details:
- Policy Number: {policy.policy_number}
- Coverage Types: {policy.coverage_types}
- Exclusions: {policy.exclusions}
- Deductible: {policy.deductible}
- Coverage Limit: {policy.coverage_limit}

Claim Details:
- Incident Type: {claim.incident_type}
- Incident Date: {claim.incident_date}
- Claimed Amount: {claim.claimed_amount}
- Cause: {claim.cause}
- Description: {claim.description}

Coverage Decision:
- Status: {coverage_result["status"]}
- Approved Amount: {coverage_result["approved_amount"]}

Fraud & Risk Assessment:
- Fraud Score: {fraud_risk_result["fraud_score"]}/100
- Risk Score: {fraud_risk_result["risk_score"]}/100
- Recommendation: {fraud_risk_result["recommendation"]}

Write a clear, structured report including:
1. Claim Summary
2. Coverage Decision Explanation
3. Fraud & Risk Summary
4. Final Recommendation

Keep tone professional and suitable for insurance documentation.
"""

    with tracer.start_as_current_span("final_report_llm_call") as span:
        span.set_attribute(SpanAttributes.INPUT_VALUE, prompt)
        report = call_llm(prompt)
        span.set_attribute(SpanAttributes.OUTPUT_VALUE, report)

    return report


def generate_final_report(
    policy: Policy,
    claim: Claim,
    coverage_result: dict,
    fraud_risk_result: dict
):
    """
    Generates final structured report combining all previous steps.
    """

    with tracer.start_as_current_span("report_generation") as span:
        span.set_attribute("report.policy_number", policy.policy_number)
        span.set_attribute("report.claim_status", coverage_result["status"])
        span.set_attribute("report.fraud_score", fraud_risk_result["fraud_score"])
        span.set_attribute("report.risk_score", fraud_risk_result["risk_score"])

        report_text = generate_final_report_llm(
            policy,
            claim,
            coverage_result,
            fraud_risk_result
        )

    return {
        "policy_number": policy.policy_number,
        "claim_status": coverage_result["status"],
        "approved_amount": coverage_result["approved_amount"],
        "fraud_score": fraud_risk_result["fraud_score"],
        "risk_score": fraud_risk_result["risk_score"],
        "recommendation": fraud_risk_result["recommendation"],
        "report": report_text
    }
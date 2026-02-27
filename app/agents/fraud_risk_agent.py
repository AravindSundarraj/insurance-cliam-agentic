# How This Works

# Historical Claim Check → detects suspicious repeated claims

# Claim Anomaly Check → flags unusually high claims

# External Indicators Check → placeholder for blacklist/external fraud data

# Risk Score Calculation → proportion of approved amount vs coverage limit

# Recommendation → if fraud_score > 70 → human review

# LLM Explanation → generates professional reasoning, traced in Phoenix

from app.schemas.policy_schema import Policy
from app.schemas.claim_schema import Claim
from app.services.phoenix_tracer import tracer
from openinference.semconv.trace import SpanAttributes
from app.services.llm_service import call_llm


def generate_risk_explanation_llm(policy: Policy, claim: Claim, fraud_score: float, risk_score: float):
    """
    Generates a human-readable explanation for fraud and risk scoring.
    """

    prompt = f"""
You are an insurance fraud and risk evaluation assistant.

Policy:
- Coverage Types: {policy.coverage_types}
- Exclusions: {policy.exclusions}
- Deductible: {policy.deductible}
- Coverage Limit: {policy.coverage_limit}

Claim:
- Incident Type: {claim.incident_type}
- Claimed Amount: {claim.claimed_amount}
- Incident Date: {claim.incident_date}
- Cause: {claim.cause}
- Description: {claim.description}

Fraud Score: {fraud_score} / 100
Risk Score: {risk_score} / 100

Explain clearly and professionally why this claim has this fraud and risk score,
and provide recommendation on human review if necessary.
"""

    with tracer.start_as_current_span("risk_reasoning_llm_call") as span:
        span.set_attribute(SpanAttributes.INPUT_VALUE, prompt)
        explanation = call_llm(prompt)
        span.set_attribute(SpanAttributes.OUTPUT_VALUE, explanation)

    return explanation


def evaluate_fraud_and_risk(policy: Policy, claim: Claim, approved_amount: float):
    """
    Evaluate fraud and risk of a claim using deterministic rules and LLM explanation.
    Returns fraud_score, risk_score, recommendation, explanation.
    """

    fraud_score = 0

    # ----------------------------
    # 1️⃣ Historical Claim Check
    # ----------------------------
    with tracer.start_as_current_span("fraud_historical_check") as span:
        # Placeholder: normally check previous claims in DB
        recent_claims_count = 1  # simulate: 1 prior claim
        if recent_claims_count > 0:
            fraud_score += min(recent_claims_count * 10, 30)
        span.set_attribute("fraud.recent_claims_count", recent_claims_count)
        span.set_attribute("fraud.partial_score", fraud_score)

    # ----------------------------
    # 2️⃣ Claim Anomaly Check
    # ----------------------------
    with tracer.start_as_current_span("fraud_anomaly_check") as span:
        # Check for unusually high claimed amounts
        if approved_amount > policy.coverage_limit * 0.8:
            fraud_score += 20
        span.set_attribute("fraud.high_amount_flag", approved_amount > policy.coverage_limit * 0.8)
        span.set_attribute("fraud.partial_score", fraud_score)

    # ----------------------------
    # 3️⃣ External Indicators Check
    # ----------------------------
    with tracer.start_as_current_span("fraud_external_check") as span:
        # Placeholder: external data (blacklists, suspicious locations)
        external_flag = False
        if external_flag:
            fraud_score += 20
        span.set_attribute("fraud.external_flag", external_flag)
        span.set_attribute("fraud.partial_score", fraud_score)

    fraud_score = min(fraud_score, 100)

    # ----------------------------
    # 4️⃣ Risk Score Calculation
    # ----------------------------
    with tracer.start_as_current_span("risk_score_calculation") as span:
        risk_score = (approved_amount / policy.coverage_limit) * 100
        risk_score = min(risk_score, 100)
        span.set_attribute("risk_score", risk_score)

    # ----------------------------
    # 5️⃣ Recommendation
    # ----------------------------
    recommendation = "Human Review" if fraud_score > 70 else "Auto-Approve"
    
    # ----------------------------
    # 6️⃣ LLM Explanation
    # ----------------------------
    explanation = generate_risk_explanation_llm(policy, claim, fraud_score, risk_score)

    return {
        "fraud_score": fraud_score,
        "risk_score": risk_score,
        "recommendation": recommendation,
        "reason": explanation
    }
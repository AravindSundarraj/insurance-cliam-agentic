from app.schemas.policy_schema import Policy
from app.schemas.claim_schema import Claim
from app.agents.coverage_decision_agent import coverage_decision
from app.agents.fraud_risk_agent import evaluate_fraud_and_risk

# Step 3: Coverage Decision
policy = Policy(
    coverage_types=["flood", "fire", "theft"],
    exclusions=["intentional_damage"],
    deductible=500,
    coverage_limit=15000
)
claim = Claim(
    incident_type="flood",
    incident_date="2024-03-12",
    claimed_amount=12000,
    cause="Heavy rain",
    description="Severe flooding in basement"
)

coverage_result = coverage_decision(policy, claim)

# Step 4: Fraud & Risk Evaluation
fraud_risk_result = evaluate_fraud_and_risk(
    policy,
    claim,
    approved_amount=coverage_result["approved_amount"]
)

print(fraud_risk_result)
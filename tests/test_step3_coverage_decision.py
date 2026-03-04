from app.schemas.policy_schema import Policy
from app.schemas.claim_schema import Claim
from app.agents.coverage_decision_agent import coverage_decision


def test_approved_claim():
    print("\n--- Test Case: Approved Claim ---")

    policy = Policy(
        coverage_types=["flood", "fire", "theft"],
        exclusions=["intentional_damage"],
        deductible=500,
        coverage_limit=15000,
        policy_number="POL-12345"
    )

    claim = Claim(
        incident_type="flood",
        incident_date="2024-03-12",
        claimed_amount=4000,
        cause="heavy rainfall",
        description="Engine and interior damaged due to flooding"
    )

    result = coverage_decision(policy, claim)
    

    print("Decision Output:")
    print(result)


def test_rejected_not_covered():
    print("\n--- Test Case: Not Covered Incident ---")

    policy = Policy(
        coverage_types=["flood", "fire"],
        exclusions=["intentional_damage"],
        deductible=500,
        coverage_limit=15000
    )

    claim = Claim(
        incident_type="earthquake",
        incident_date="2024-03-12",
        claimed_amount=4000,
        cause="ground shaking",
        description="Wall cracks due to earthquake"
    )

    result = coverage_decision(policy, claim)

    print("Decision Output:")
    print(result)


def test_partially_approved_due_to_limit():
    print("\n--- Test Case: Partial Approval (Limit Exceeded) ---")

    policy = Policy(
        coverage_types=["flood"],
        exclusions=[],
        deductible=500,
        coverage_limit=3000
    )

    claim = Claim(
        incident_type="flood",
        incident_date="2024-03-12",
        claimed_amount=6000,
        cause="heavy rainfall",
        description="Severe flood damage"
    )

    result = coverage_decision(policy, claim)

    print("Decision Output:")
    print(result)


if __name__ == "__main__":
    test_approved_claim()
    test_rejected_not_covered()
    test_partially_approved_due_to_limit()
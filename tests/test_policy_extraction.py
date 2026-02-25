from app.agents.policy_extraction_agent import extract_policy_details

sample_policy = """
AUTO PROTECT INSURANCE COMPANY
Comprehensive Motor Insurance Policy

Policy Number: AP-2024-IND-77891

COVERAGE DETAILS:
1. Accidental damage to insured vehicle
2. Theft of the insured vehicle
3. Fire damage
4. Natural calamities including flood, earthquake, and storm

EXCLUSIONS:
1. Intentional damage caused by the policy holder
2. Driving under the influence of alcohol or drugs
3. Mechanical breakdown not caused by accident
4. Wear and tear

Deductible: 500 USD per claim
Maximum Coverage Limit: 15000 USD per incident
"""

policy = extract_policy_details(sample_policy)

print("Print policy ==>>",policy)
print(policy.model_dump())
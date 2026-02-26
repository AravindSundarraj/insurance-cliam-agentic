from app.agents.claim_extraction_agent import extract_claim_details
from app.evaluations.claim_evaluator import evaluate_claim

# -----------------------------
# Sample Claim Text
# -----------------------------

sample_claim_text = """
On 12 March 2024, my car was damaged due to flooding caused by heavy rainfall.
Water entered the engine and interior of the vehicle.
The total repair cost is approximately 4000 USD.
"""

# -----------------------------
# Step 1: Extract Claim
# -----------------------------

print("---- Extracting Claim ----")

claim = extract_claim_details(sample_claim_text)

print("\nStructured Claim Object:")
print(claim)

print("\nAs Dictionary:")
print(claim.model_dump())

# -----------------------------
# Step 2: Evaluate Claim
# -----------------------------

print("\n---- Running Evaluation ----")

evaluation_results = evaluate_claim(claim, sample_claim_text)

print("\nEvaluation Results:")
print(evaluation_results)

print("\n---- Done ----")
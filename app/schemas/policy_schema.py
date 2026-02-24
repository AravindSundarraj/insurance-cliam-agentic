from pydantic import BaseModel
from typing import List, Optional
# Define Policy Schema (Very Important)
# Why This Is Important

# Enforces structured output

# Prevents random hallucinated fields

# Makes evaluation easier

# Makes payout calculation deterministic

# Keeps agent modular

class Policy(BaseModel):
    coverage_types: List[str]
    exclusions: List[str]
    deductible: float
    coverage_limit: float
    policy_number: Optional[str] = None
from pydantic import BaseModel
from typing import List, Optional

class Policy(BaseModel):
    coverage_types: List[str]
    exclusions: List[str]
    deductible: float
    coverage_limit: float
    policy_number: Optional[str] = None
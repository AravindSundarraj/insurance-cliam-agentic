# Why Structured?

# Because later:

# We compare incident_type with coverage_types

# We check exclusions

# We calculate payout

# LLM must NOT decide approval.

# It only extracts facts.

from pydantic import BaseModel
from typing import Optional
from datetime import date

class Claim(BaseModel):
    incident_type: str
    incident_date: Optional[str]
    claimed_amount: float
    cause: str
    description: str
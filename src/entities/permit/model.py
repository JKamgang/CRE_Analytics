from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Permit:
    id: str
    permit_type: str
    issue_date: str
    status: str
    location: Dict[str, float] # { 'lat': x, 'lng': y }
    estimated_cost: Optional[float] = None
    description: Optional[str] = None

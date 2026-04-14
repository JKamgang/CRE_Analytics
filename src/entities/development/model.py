from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class DevelopmentProject:
    id: str
    project_name: str
    status: str
    property_type: str
    square_footage: Optional[float]
    completion_year: Optional[int]
    location: Dict[str, float]

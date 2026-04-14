from dataclasses import dataclass

@dataclass
class CREMIIndex:
    year: int
    quarter: int
    region: str
    risk_score: float
    momentum_score: float

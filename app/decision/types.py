from dataclasses import dataclass

@dataclass(frozen=True)
class GoalDecisionResult:
    prediction: str             # over_2_5 | under_2_5 | no_clear_lean
    confidence: str             # low | moderate | high
    rates: dict                 # {'over': float, 'under': float}
    sample_size: int
    volatility_flag: bool
    reliability_score: float
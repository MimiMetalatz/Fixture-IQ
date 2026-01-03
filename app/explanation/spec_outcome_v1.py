"""
FixtureIQ v1 – Outcome Explanation Spec (Frozen)

This module is intentionally "dumb": constants only.
No business logic, no Pinecone, no decisions.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class OutcomePrediction(str, Enum):
    HOME = "home"
    DRAW = "draw"
    AWAY = "away"
    NO_CLEAR_LEAN = "no_clear_lean"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


HEADER = "FixtureIQ – Outcome Assessment (Pre-Kickoff)"

# Fixed labels
SECTION_DISTRIBUTION_INTRO = "Across comparable past fixtures:"
SECTION_RECENT_MATCHES_HEADER = "Recent comparable fixtures (this season and last):"

# Human-friendly mappings
OUTCOME_CODE_TO_TEXT: Dict[str, str] = {
    "H": "Home win",
    "D": "Draw",
    "A": "Away win",
}

PREDICTION_TO_TEXT: Dict[OutcomePrediction, str] = {
    OutcomePrediction.HOME: "Home win",
    OutcomePrediction.DRAW: "Draw",
    OutcomePrediction.AWAY: "Away win",
    OutcomePrediction.NO_CLEAR_LEAN: "No clear lean",
}

CONFIDENCE_TO_TEXT: Dict[ConfidenceLevel, str] = {
    ConfidenceLevel.LOW: "Low",
    ConfidenceLevel.MODERATE: "Moderate",
    ConfidenceLevel.HIGH: "High",
}

# Confidence-aware wording (Section 2)
# Note: keep these exactly; tests rely on them.
WORDING_NO_CLEAR_LEAN = (
    "Based on the pre-match context, this fixture does not present a clear outcome lean. "
    "Comparable historical matches with similar balance and uncertainty have produced a wide range of results, "
    "with no single outcome occurring consistently more often."
)

WORDING_LOW_LEAN = (
    "Based on the pre-match context, this fixture shows a slight lean toward the {side}. "
    "Comparable historical matches with similar balance and uncertainty have produced this outcome somewhat more often, "
    "though alternative results have been frequent."
)

WORDING_MODERATE_LEAN = (
    "Based on the pre-match context, this fixture shows a moderate confidence lean toward the {side}. "
    "Comparable historical matches with similar balance, strength, and uncertainty have seen this outcome occur more often, "
    "though alternative outcomes remain realistic."
)

WORDING_HIGH_LEAN = (
    "Based on the pre-match context, this fixture shows a high confidence lean toward the {side}. "
    "Comparable historical matches with similar balance, strength, and uncertainty have produced this outcome substantially more often than alternatives."
)


@dataclass(frozen=True)
class OutcomeExplanationSpecV1:
    """
    A frozen spec object to make it easy to inject/replace later,
    while preventing accidental mutation.
    """
    header: str = HEADER
    distribution_intro: str = SECTION_DISTRIBUTION_INTRO
    recent_matches_header: str = SECTION_RECENT_MATCHES_HEADER

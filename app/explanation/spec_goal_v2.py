"""
FixtureIQ v1 – Outcome Explanation Spec (Frozen)

This module is intentionally "dumb": constants only.
No business logic, no Pinecone, no decisions.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict

HEADER = "FixtureIQ – Goal Assessment (Pre-Kickoff)"

SECTION_DISTRIBUTION_INTRO = "Across comparable {total_matches} fixtures over the last {season_count} seasons:"

SECTION_RECENT_MATCHES_HEADER = "Recent comparable fixtures (this season and last):"

WORDING_OVER_LEAN = (
    "Comparable historical matches with similar attacking pressure and defensive openness "
    "have more often produced higher-scoring outcomes."
)

WORDING_UNDER_LEAN = (
    "Comparable historical matches with similar attacking and defensive profiles "
    "have more often resulted in lower-scoring outcomes."
)

WORDING_NO_CLEAR_LEAN = (
    "Comparable historical matches with similar attacking and defensive profiles "
    "have produced a mixed range of goal totals, with no single outcome occurring consistently more often."
)

VOLATILITY_WARNING = (
    "However, recent goal volatility increases unpredictability in this type of fixture."
)

CONFIDENCE_LOW = (
    "Confidence is limited due to high variability and inconsistent outcomes across similar fixtures."
)

CONFIDENCE_MODERATE = (
    "While the lean is supported by historical patterns, some variability limits overall confidence."
)
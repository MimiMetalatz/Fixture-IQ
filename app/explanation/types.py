from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass(frozen=True)
class ComparableEvidenceSummary:
    display_matches: List[Dict[str, Any]]
    total_matches: int
    season_count: int
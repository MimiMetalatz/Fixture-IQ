from typing import List, Dict, Set
from datetime import datetime


def _season_key(season: str) -> int:
    """
    Convert season string like '2526' or '2025/26' to sortable int.
    Higher = more recent.
    """
    if "/" in season:
        start = season.split("/")[0]
        return int(start)
    return int(season[:2]) + 2000  # e.g. '2526' -> 2025


def filter_and_sort_recent_comparable_matches(
    neighbors: List[Dict],
    allowed_seasons: Set[str],
    max_items: int = 5,
):
    """
    DISPLAY ONLY:
    - keep matches from allowed seasons
    - sort by season desc, then date desc
    - return up to max_items
    """

    # 1. Filter by season
    recent = [
        m for m in neighbors
        if m["metadata"].get("season") in allowed_seasons
    ]

    # 2. Sort by (season desc, date desc)
    recent.sort(
        key=lambda m: (
            _season_key(m["metadata"]["season"]),
            datetime.fromisoformat(m["metadata"]["date"])
        ),
        reverse=True
    )

    return recent[:max_items]

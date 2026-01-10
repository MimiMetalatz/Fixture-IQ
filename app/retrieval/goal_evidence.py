# app/retrieval/goal_evidence.py

from app.explanation.types import ComparableEvidenceSummary

def build_goal_evidence(matches: list) -> ComparableEvidenceSummary:
    total = len(matches)
    seasons = {m["metadata"]["season"] for m in matches}

    return ComparableEvidenceSummary(
        display_matches=matches[:5],   # already sorted upstream
        total_matches=total,
        season_count=len(seasons),
    )

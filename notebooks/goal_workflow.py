from app.explanation.goal_template import GoalExplanationTemplate
from app.explanation.types import ComparableEvidenceSummary
from app.vector_store.pinecone_goal_store import PineconeGoalVectorStore
from app.config.settings import settings
from app.context.goal_context_builder import GoalContextBuilder
from app.context.goal_context_vector_builder import GoalContextVectorBuilder
from app.decision.goal_decision import GoalDecisionLayer
from app.explanation.comparable_match_filter import filter_and_sort_recent_comparable_matches
from collections import Counter

import pandas as pd

pinecone_api_key = settings.pinecone_api_key
pinecone_goal_index_name = settings.pinecone_goal_index_name
goal_market_namespace = settings.goal_market_namespace


# 1) Load raw fixtures (same source as ingestion)
# You can load a single season or all seasons; all is better.
raw_df = pd.concat(
    [pd.read_csv(p) for p in settings.data_dir.glob("*.csv")],
    ignore_index=True
)

# print(f"raw data frame: {raw_df.tail(10)}")

builder = GoalContextBuilder(raw_df)

fixture_ctx = builder.build_live(
    home_team="Arsenal",
    away_team="Man United",
    over25_odds=1.80,
    under25_odds=2.05,
)

# print(fixture_ctx)

vector_builder = GoalContextVectorBuilder()
query_vector = vector_builder.build_single(fixture_ctx)

# print(f"query vector: {query_vector}")

store = PineconeGoalVectorStore(
    index_name=pinecone_goal_index_name,
    dimension=len(query_vector),
    namespace=goal_market_namespace,
)

neighbors = store.query(query_vector, top_k=25)  # returns Pinecone "matches"
# print(f"neighors - {neighbors}")

# TEST - Count retrieved matches by season
# season_counts = Counter(
#     m["metadata"].get("season") for m in neighbors
# )

# print("Season distribution in retrieved neighbors:")
# for season, count in season_counts.items():
#     print(season, count)

# TEST - current-season matches
# current_season = [
#     m for m in neighbors
#     if m["metadata"].get("season") == "2526"
# ]

# print(f"Comparable matches in 2526: {len(current_season)}")

# for m in current_season:
#     print(
#         m["metadata"]["home_team"],
#         "vs",
#         m["metadata"]["away_team"],
#         m["metadata"]["date"],
#     )

# TEST - another diagnostic
for m in neighbors:
    md = m["metadata"]
    print(
        md["season"],
        md["home_team"], "vs", md["away_team"],
        "FTHG+FTAG =", md["fthg"] + md["ftag"]
    )


# 5) Aggregate Over/Under evidence from metadata (fthg/ftag OR total_goals)
# def total_goals_from_md(md: dict) -> float:
#     if "total_goals" in md:
#         return float(md["total_goals"])
#     return float(md["fthg"] + md["ftag"])

# over_count = sum(1 for m in neighbors if total_goals_from_md(m["metadata"]) > 2.5)
# # print(f"over_count - {over_count}")
# under_count = len(neighbors) - over_count

# over_rate = over_count / len(neighbors)
# under_rate = under_count / len(neighbors)

# # print(f"over_rate  - {over_rate}")
# # print(f"under_rate - {under_rate}")

# # 6) Decision layer
# decision = GoalDecisionLayer().decide(
#     over_rate=over_rate,
#     under_rate=under_rate,
#     sample_size=len(neighbors),
#     goal_volatility=fixture_ctx.get("goal_volatility", 0.5),
#     reliability_score=fixture_ctx.get("goal_context_reliability", 1.0),
# )

# # print(f"Decision: {decision}")

# # 7) Build evidence summary for explanation (recent display only)
# display_matches = filter_and_sort_recent_comparable_matches(
#     neighbors,
#     allowed_seasons={"2526", "2425"},   # current + previous
#     max_items=5,
# )

# # print(f"display_matches: {display_matches}")

# evidence_summary = ComparableEvidenceSummary(
#     display_matches=display_matches,
#     total_matches=len(neighbors),
#     season_count=len({m["metadata"].get("season") for m in neighbors}),
# )

# print(f"evidence_summary: {evidence_summary}")

# # 8) Generate explanation
# text = GoalExplanationTemplate().generate(
#     fixture={"home_team": "Arsenal", "away_team": "Man United"},
#     decision=decision.__dict__,
#     evidence_summary=evidence_summary,
# )

# print("\n" + text)
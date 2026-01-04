from app.context.context_builder import ContextBuilder
from app.context.context_vector_builder import ContextVectorBuilder
from app.decision.outcome_decision_engine import OutcomeDecisionEngine
from app.explanation.outcome_template import OutcomeExplanationTemplate
from app.utils.aggregation import aggregate_outcomes
from app.vector_store.pinecone_vector_store import PineconeVectorStore
from app.explanation.comparable_match_filter import filter_and_sort_recent_comparable_matches
from app.explanation.types import ComparableEvidenceSummary

# --------------------------------------------------
# 1. Define a SINGLE upcoming fixture context
# --------------------------------------------------

# fixture_context = {
#     "home_team": "Chelsea",
#     "away_team": "Manchester City",
#     "home_odds": 3.10,
#     "draw_odds": 3.40,
#     "away_odds": 2.10,
#     "home_last5_points": 7,
#     "away_last5_points": 13,
#     "form_coverage": 1.0,   # all last-5 matches known
# }
context_builder = ContextBuilder(data_dir="data/raw", form_window=5)

# Odds as of January 2, 2026
# {"home_odds": 1.67, "draw_odds": 4.40, "away_odds": 4.40}
fixture_context = context_builder.build_single_context(
    home_team="Man City",
    away_team="Chelsea",
    home_odds=1.56,
    draw_odds=4.6,
    away_odds=5.7,)

# print(type(fixture_context))
# print(fixture_context["HomeTeam"])
# print(fixture_context["AwayTeam"])

# --------------------------------------------------
# 2. Build context vector (single)
# --------------------------------------------------

vector_builder = ContextVectorBuilder()
query_vector = vector_builder.build_single(fixture_context)

# --------------------------------------------------
# 3. Query Pinecone
# --------------------------------------------------

store = PineconeVectorStore(
    index_name="fixtureiq-outcome-v1",
    dimension=len(query_vector),
    namespace="outcome_market",
)

neighbors = store.query(query_vector, top_k=25)["matches"]
# print(neighbors)

# --------------------------------------------------
# 4. Aggregate historical outcomes
# --------------------------------------------------

evidence = aggregate_outcomes(neighbors)
# print(evidence)

# --------------------------------------------------
# 5. Make decision
# --------------------------------------------------

decision = OutcomeDecisionEngine().decide(
    evidence["rates"],
    evidence["sample_size"],
)

# --------------------------------------------------
# 6. Generate explanation text
# --------------------------------------------------
display_matches = filter_and_sort_recent_comparable_matches(neighbors, allowed_seasons={"2526", "2425"}, max_items=5)

# print(display_matches)

evidence_summary = ComparableEvidenceSummary(
    display_matches=display_matches,
    total_matches=len(neighbors),
    season_count=len({m["metadata"].get("season") for m in neighbors})
)

fixture = {
    "home_team": fixture_context["HomeTeam"],
    "away_team": fixture_context["AwayTeam"],
}

text = OutcomeExplanationTemplate().generate(
    decision,
    fixture=fixture,
    evidence_summary=evidence_summary,
)

print(text)

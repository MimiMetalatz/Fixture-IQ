from app.context.goal_context_vector_builder import GoalContextVectorBuilder
from app.vector_store.pinecone_goal_store import PineconeGoalVectorStore
from app.decision.goal_decision import GoalDecisionLayer
from app.explanation.goal_template import GoalExplanationTemplate
from app.retrieval.goal_evidence import build_goal_evidence


class GoalMarketPipeline:
    def __init__(self, *, vector_store: PineconeGoalVectorStore):
        self.vector_builder = GoalContextVectorBuilder()
        self.vector_store = vector_store
        self.decision_layer = GoalDecisionLayer()
        self.explainer = GoalExplanationTemplate()

    def run(self, *, fixture_context: dict) -> str:
        # 1️⃣ Build goal context vector
        vector = self.vector_builder.build_single(fixture_context)

        # 2️⃣ Retrieve comparable matches from Pinecone
        matches = self.vector_store.query(vector, top_k=25)

        if not matches:
            raise RuntimeError("No comparable matches retrieved from Pinecone")

        # 3️⃣ Aggregate Over / Under evidence
        over_count = sum(
            1 for m in matches if m["metadata"]["total_goals"] > 2.5
        )
        under_count = len(matches) - over_count

        over_rate = over_count / len(matches)
        under_rate = under_count / len(matches)

        # 4️⃣ Decision
        decision = self.decision_layer.decide(
            over_rate=over_rate,
            under_rate=under_rate,
            sample_size=len(matches),
            goal_volatility=fixture_context.get("goal_volatility", 0.5),
            reliability_score=fixture_context.get("goal_context_reliability", 1.0),
        )

        # 5️⃣ Evidence summary (for explanation)
        evidence = build_goal_evidence(matches)

        # 6️⃣ Explanation
        return self.explainer.generate(
            fixture={
                "home_team": fixture_context["home_team"],
                "away_team": fixture_context["away_team"],
            },
            decision=decision.__dict__,
            evidence_summary=evidence,
        )

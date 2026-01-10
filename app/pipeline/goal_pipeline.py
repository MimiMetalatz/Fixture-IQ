# app/pipeline/goal_pipeline.py

from app.decision.goal_decision import GoalDecisionLayer
from app.explanation.goal_template import GoalExplanationTemplate
from app.retrieval.goal_evidence import build_goal_evidence

class GoalMarketPipeline:
    def __init__(self):
        self.decision_layer = GoalDecisionLayer()
        self.explainer = GoalExplanationTemplate()

    def run(
        self,
        *,
        fixture: dict,
        over_rate: float,
        under_rate: float,
        sample_size: int,
        goal_volatility: float,
        reliability_score: float,
        comparable_matches: list,
    ) -> str:

        decision = self.decision_layer.decide(
            over_rate=over_rate,
            under_rate=under_rate,
            sample_size=sample_size,
            goal_volatility=goal_volatility,
            reliability_score=reliability_score,
        )

        evidence = build_goal_evidence(comparable_matches)

        explanation = self.explainer.generate(
            fixture=fixture,
            decision=decision.__dict__,
            evidence_summary=evidence,
        )

        return explanation

from app.decision.types import GoalDecisionResult

class GoalDecisionLayer:
    def decide(
        self, 
        *, 
        over_rate: float, 
        under_rate: float, 
        sample_size: int, 
        goal_volatility: float, 
        reliability_score: float
     ) -> GoalDecisionResult:
        
        dominance = abs(over_rate - under_rate)

        # Lean
        if over_rate >= 0.55 and dominance >= 0.10:
            prediction = "over_2_5"
        elif under_rate >= 0.55 and dominance >= 0.10:
            prediction = "under_2_5"
        else:
            prediction = "no_clear_lean"

        # Base Confidence
        if dominance < 0.10:
            confidence = "low"
        elif dominance < 0.20:
            confidence = "moderate"
        else:
            confidence = "high"

        # volatility penalty
        if goal_volatility > 0.7 and confidence != "low":
            confidence = "moderate" if confidence == "high" else "low"

        # reliability penalty
        if reliability_score  < 0.7 and confidence != "low":
            confidence = "low"

        return GoalDecisionResult(
            prediction=prediction,
            confidence=confidence,
            rates={"over": over_rate, "under": under_rate},
            sample_size=sample_size,
            volatility_flag=goal_volatility > 0.7,
            reliability_score=reliability_score,
        )
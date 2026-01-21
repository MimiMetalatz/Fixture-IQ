class GoalContextVectorBuilder:
    VECTOR_DIM = 8

    def build_single(self, ctx: dict) -> list[float]:
        try:
            # ---- 1. Team-driven goal signals (causal) ----
            attacking_pressure = (
                ctx["home_last5_goals_scored"] +
                ctx["away_last5_goals_scored"]
            ) / 10.0

            defensive_openness = (
                ctx["home_last5_goals_conceded"] +
                ctx["away_last5_goals_conceded"]
            ) / 10.0

            goal_intensity = (attacking_pressure + defensive_openness) / 2.0

            # ---- 2. Match volatility (semi-causal) ----
            goal_volatility = ctx.get("goal_volatility", 0.5)

            # ---- 3. Market expectation (proxy) ----
            over_odds = ctx.get("over25_odds")
            under_odds = ctx.get("under25_odds")

            if over_odds and under_odds:
                p_over = 1.0 / over_odds
                p_under = 1.0 / under_odds

                # remove bookmaker margin
                norm = p_over + p_under
                p_over /= norm
                p_under /= norm
            else:
                p_over = 0.5
                p_under = 0.5

            market_over_prob = p_over
            market_uncertainty = 1.0 - abs(p_over - p_under) * 2.0
            market_uncertainty = max(0.0, market_uncertainty)

            # ---- 4. Team tendencies (proxy) ----
            team_goal_tendency = (
                ctx.get("home_over_rate", 0.5) +
                ctx.get("away_over_rate", 0.5)
            ) / 2.0

            # ---- 5. Context reliability ----
            context_reliability = ctx.get("goal_context_reliability", 1.0)

            # print(f"Vector values: {[attacking_pressure, defensive_openness, goal_intensity, goal_volatility, market_over_prob, market_uncertainty, team_goal_tendency, context_reliability]}") 

            return [
                attacking_pressure,
                defensive_openness,
                goal_intensity,
                goal_volatility,
                market_over_prob,
                market_uncertainty,
                team_goal_tendency,
                context_reliability,
            ]
        except KeyError as e:
            raise ValueError(f"Incomplete context for goal vector building. Error: {e}  Context: {ctx}") from e

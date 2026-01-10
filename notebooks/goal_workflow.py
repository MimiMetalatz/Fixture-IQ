from app.pipeline.goal_pipeline import GoalMarketPipeline

def _mk_matches():
    return [
        {
            "metadata": {
                "home_team": "Arsenal",
                "away_team": "Aston Villa",
                "season": "2025/2026",
                "date": "2026-01-01",
                "total_goals": 3,
            }
        },
        {
            "metadata": {
                "home_team": "Tottenham",
                "away_team": "Man United",
                "season": "2526",
                "date": "2025-12-20",
                "total_goals": 2,
            }
        },
    ]

pipeline = GoalMarketPipeline()

text = pipeline.run(
    fixture={"home_team": "Brentford", "away_team": "Sunderland"},
    over_rate=0.62,
    under_rate=0.38,
    sample_size=25,
    goal_volatility=0.8,
    reliability_score=0.9,
    comparable_matches=_mk_matches(),
)

print(text)

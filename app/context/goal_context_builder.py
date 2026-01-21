# app/context/goal_context_builder.py

import pandas as pd
import numpy as np


class GoalContextBuilder:
    def __init__(self, raw_fixtures_df: pd.DataFrame):
        self.df = raw_fixtures_df.copy()

        self.df["Date"] = pd.to_datetime(
            self.df["Date"], dayfirst=True, errors="coerce"
        )
        self.df["FTHG"] = pd.to_numeric(self.df["FTHG"], errors="coerce")
        self.df["FTAG"] = pd.to_numeric(self.df["FTAG"], errors="coerce")

        self.df = self.df.dropna(
            subset=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
        ).sort_values("Date")

    def build_live(
        self,
        home_team: str,
        away_team: str,
        over25_odds: float,
        under25_odds: float,
        as_of_date: str | None = None,
        window: int = 5,
    ) -> dict:
        df = self.df

        if as_of_date:
            cutoff = pd.to_datetime(as_of_date)
            df = df[df["Date"] < cutoff]

        def team_rows(team: str) -> pd.DataFrame:
            home = df[df["HomeTeam"] == team][["Date", "FTHG", "FTAG"]]
            home = home.rename(columns={"FTHG": "GF", "FTAG": "GA"})

            away = df[df["AwayTeam"] == team][["Date", "FTAG", "FTHG"]]
            away = away.rename(columns={"FTAG": "GF", "FTHG": "GA"})

            t = pd.concat([home, away], ignore_index=True).sort_values("Date")
            t["total_goals"] = t["GF"] + t["GA"]
            return t

        h = team_rows(home_team).tail(window)
        a = team_rows(away_team).tail(window)

        home_last5_scored = float(h["GF"].mean()) if len(h) else np.nan
        home_last5_conceded = float(h["GA"].mean()) if len(h) else np.nan
        away_last5_scored = float(a["GF"].mean()) if len(a) else np.nan
        away_last5_conceded = float(a["GA"].mean()) if len(a) else np.nan

        home_over_rate = float((h["total_goals"] > 2.5).mean()) if len(h) else 0.5
        away_over_rate = float((a["total_goals"] > 2.5).mean()) if len(a) else 0.5

        combined = pd.concat([h["total_goals"], a["total_goals"]], ignore_index=True)
        goal_volatility = float(combined.std()) if len(combined) >= 3 else 0.5
        goal_volatility = max(0.0, min(1.0, goal_volatility / 2.0))

        goal_context_reliability = min(1.0, (len(h) + len(a)) / (2 * window))

        return {
            "home_team": home_team,
            "away_team": away_team,
            "home_last5_goals_scored": home_last5_scored,
            "home_last5_goals_conceded": home_last5_conceded,
            "away_last5_goals_scored": away_last5_scored,
            "away_last5_goals_conceded": away_last5_conceded,
            "over25_odds": float(over25_odds),
            "under25_odds": float(under25_odds),
            "home_over_rate": home_over_rate,
            "away_over_rate": away_over_rate,
            "goal_volatility": goal_volatility,
            "goal_context_reliability": goal_context_reliability,
        }

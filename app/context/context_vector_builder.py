import pandas as pd
import numpy as np


class ContextVectorBuilder:
    """
    Converts contextualized fixture data into numerical context vectors.

    This class:
    - assumes pre-match rolling form already exists
    - does NOT compute form
    - does NOT embed outcomes
    """

    REQUIRED_COLUMNS = [
        # teams
        "HomeTeam", "AwayTeam",

        # rolling form
        "home_last5_points", "away_last5_points",
        "home_last5_gf", "away_last5_gf",
        "home_last5_ga", "away_last5_ga",

        # odds
        "AvgH", "AvgD", "AvgA",
    ]

    VECTOR_COLUMNS = [
        "delta_last5_points",
        "delta_last5_goals_for",
        "delta_last5_goals_against",
        "odds_favorite_strength",
        "odds_balance",
        "draw_probability",
        "home_bias",
        "avg_form_coverage",
    ]

    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build context vectors for each fixture row.

        Returns a DataFrame with VECTOR_COLUMNS in fixed order.
        """
        self._validate_input(df)

        vectors = pd.DataFrame(index=df.index)

        # ---------- Group 1: Relative form ----------
        vectors["delta_last5_points"] = (
            df["home_last5_points"] - df["away_last5_points"]
        )

        vectors["delta_last5_goals_for"] = (
            df["home_last5_gf"] - df["away_last5_gf"]
        )

        vectors["delta_last5_goals_against"] = (
            df["home_last5_ga"] - df["away_last5_ga"]
        )

        # ---------- Group 2: Odds-derived signals ----------
        pH = 1.0 / df["AvgH"]
        pD = 1.0 / df["AvgD"]
        pA = 1.0 / df["AvgA"]

        vectors["odds_favorite_strength"] = np.maximum(pH, pA)
        vectors["odds_balance"] = np.abs(pH - pA)
        vectors["draw_probability"] = pD

        # ---------- Group 3: Home bias ----------
        vectors["home_bias"] = pH - pA

        # ---------- Group 4: Context completeness ----------
        home_coverage = (df["home_last5_points"] / 15.0).clip(0, 1)
        away_coverage = (df["away_last5_points"] / 15.0).clip(0, 1)

        vectors["avg_form_coverage"] = (home_coverage + away_coverage) / 2.0

        # Ensure column order
        vectors = vectors[self.VECTOR_COLUMNS]

        return vectors

    def build_single(self, context: dict) -> list[float]:
        """
        Build a context vector for a single upcoming fixture.

        Returns a list of floats in VECTOR_COLUMNS order.
        """
        # Convert single context dict to DataFrame
        df = pd.DataFrame([context])

        # Reuse batch logic
        vectors_df = self.build(df)

        # Extract the single vector as list
        return vectors_df.iloc[0].tolist()


    # ---------- Internal helpers ----------

    def _validate_input(self, df: pd.DataFrame) -> None:
        missing = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                f"ContextVectorBuilder missing required columns: {missing}"
            )

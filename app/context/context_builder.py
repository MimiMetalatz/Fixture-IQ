from pathlib import Path
import pandas as pd

from app.data.data_source import MatchDataSource


class ContextBuilder:
    """
    Context Builder for FixtureIQ.

    Responsibilities:
    - Load raw match data
    - Compute rolling pre-match form (last N games)
    - Produce decision-aligned context rows

    NO reasoning.
    NO prediction.
    """

    def __init__(
        self,
        data_dir: str | Path,
        form_window: int = 5,
    ):
        self.data_source = MatchDataSource(data_dir=data_dir)
        self.form_window = form_window

    # ---------- Public API ----------

    def build(self) -> pd.DataFrame:
        """
        Build contextualized match data with pre-match rolling form.
        """
        raw = self.data_source.load_all_matches()
        long = self._to_long_format(raw)
        long = self._compute_rolling_form(long)
        contextualized = self._attach_form_to_fixtures(raw, long)

        return contextualized

    def build_single_context(
        self,
        home_team: str,
        away_team: str,
        home_odds: float,
        draw_odds: float,
        away_odds: float,
    ) -> dict:
        """
        Build pre-match context for a single upcoming fixture.
        Uses historical data already loaded by ContextBuilder.
        """

        df = self.build()  # historical context with rolling features

        # --- Home team recent matches ---
        home_rows = df[
            (df["HomeTeam"] == home_team) | (df["AwayTeam"] == home_team)
        ].tail(self.form_window)

        away_rows = df[
            (df["HomeTeam"] == away_team) | (df["AwayTeam"] == away_team)
        ].tail(self.form_window)

        def compute_team_form(rows, team):
            points = 0
            gf = 0
            ga = 0

            for _, r in rows.iterrows():
                if r["HomeTeam"] == team:
                    gf += r["FTHG"]
                    ga += r["FTAG"]
                    points += 3 if r["FTR"] == "H" else 1 if r["FTR"] == "D" else 0
                else:
                    gf += r["FTAG"]
                    ga += r["FTHG"]
                    points += 3 if r["FTR"] == "A" else 1 if r["FTR"] == "D" else 0

            return points, gf, ga

        home_pts, home_gf, home_ga = compute_team_form(home_rows, home_team)
        away_pts, away_gf, away_ga = compute_team_form(away_rows, away_team)

        # --- Coverage ---
        home_cov = len(home_rows) / self.form_window
        away_cov = len(away_rows) / self.form_window
        avg_coverage = (home_cov + away_cov) / 2.0

        return {
            "HomeTeam": home_team,
            "AwayTeam": away_team,

            "home_last5_points": home_pts,
            "away_last5_points": away_pts,
            "home_last5_gf": home_gf,
            "away_last5_gf": away_gf,
            "home_last5_ga": home_ga,
            "away_last5_ga": away_ga,

            "AvgH": home_odds,
            "AvgD": draw_odds,
            "AvgA": away_odds,

            "avg_form_coverage": avg_coverage,
        }

    # ---------- Internal helpers ----------

    def _to_long_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert match-level data to team-level long format.
        One row per team per match.
        """
        home = df.copy()
        home["team"] = home["HomeTeam"]
        home["goals_for"] = home["FTHG"]
        home["goals_against"] = home["FTAG"]
        home["points"] = home["FTR"].map({"H": 3, "D": 1, "A": 0})

        away = df.copy()
        away["team"] = away["AwayTeam"]
        away["goals_for"] = away["FTAG"]
        away["goals_against"] = away["FTHG"]
        away["points"] = away["FTR"].map({"A": 3, "D": 1, "H": 0})

        long = pd.concat([home, away], ignore_index=True)

        long = long[
            ["season", "Date", "team", "goals_for", "goals_against", "points"]
        ].sort_values(["season", "team", "Date"])

        return long.reset_index(drop=True)

    def _compute_rolling_form(self, long: pd.DataFrame) -> pd.DataFrame:
        """
        Compute rolling pre-match form.
        Rolling window is shifted by 1 to avoid leakage.
        """
        window = self.form_window

        for col in ["points", "goals_for", "goals_against"]:
            long[f"last{window}_{col}"] = (
                long
                .groupby(["season", "team"])[col]
                .rolling(window, min_periods=0)
                .sum()
                .reset_index(level=[0, 1], drop=True)
                .shift(1)
                .fillna(0)
                .astype(int)
            )

        return long

    def _attach_form_to_fixtures(
        self,
        fixtures: pd.DataFrame,
        long: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Attach pre-match rolling form back to fixture-level rows.
        """
        window = self.form_window

        lookup = long[
            [
                "season", "Date", "team",
                f"last{window}_points",
                f"last{window}_goals_for",
                f"last{window}_goals_against",
            ]
        ]

        home_lookup = lookup.rename(columns={
            "team": "HomeTeam",
            f"last{window}_points": "home_last5_points",
            f"last{window}_goals_for": "home_last5_gf",
            f"last{window}_goals_against": "home_last5_ga",
        })

        away_lookup = lookup.rename(columns={
            "team": "AwayTeam",
            f"last{window}_points": "away_last5_points",
            f"last{window}_goals_for": "away_last5_gf",
            f"last{window}_goals_against": "away_last5_ga",
        })

        df = fixtures.merge(
            home_lookup,
            on=["season", "Date", "HomeTeam"],
            how="left"
        ).merge(
            away_lookup,
            on=["season", "Date", "AwayTeam"],
            how="left"
        )

        return df

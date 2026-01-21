from pathlib import Path
import pandas as pd
import numpy as np

from app.context.goal_context_vector_builder import GoalContextVectorBuilder
from app.config.settings import settings
from app.vector_store.pinecone_goal_store import PineconeGoalVectorStore
from app.utils.batch import batch  # same helper used in outcome ingestion
from app.utils.vector_validation import validate_vector 


DATA_DIR = Path(settings.data_dir)
GOAL_NAMESPACE = settings.goal_market_namespace
INDEX_NAME = settings.pinecone_goal_index_name
BATCH_SIZE = settings.pinecone_batch_size

REQUIRED_GOAL_CONTEXT = [
    "home_last5_goals_scored",
    "away_last5_goals_scored",
    "home_last5_goals_conceded",
    "away_last5_goals_conceded",
    "Avg>2.5",
    "Avg<2.5",
]

# -------------------------
# 1. Load historical data
# -------------------------
def load_historical_data() -> pd.DataFrame:
    dfs = []

    for file in DATA_DIR.glob("*.csv"):
        df = pd.read_csv(file)

        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        df["season"] = file.stem

        # Ensure numeric
        df["FTHG"] = pd.to_numeric(df["FTHG"], errors="coerce")
        df["FTAG"] = pd.to_numeric(df["FTAG"], errors="coerce")

        dfs.append(df)

    full_df = pd.concat(dfs, ignore_index=True)
    return full_df


# -----------------------------------
# 2. Build team-level goal table
# -----------------------------------
def build_team_goal_table(df: pd.DataFrame) -> pd.DataFrame:
    home = df[[
        "Date", "season", "HomeTeam", "AwayTeam", "FTHG", "FTAG"
    ]].copy()

    home["Team"] = home["HomeTeam"]
    home["Opponent"] = home["AwayTeam"]
    home["GoalsFor"] = home["FTHG"]
    home["GoalsAgainst"] = home["FTAG"]
    home["is_home"] = 1

    away = df[[
        "Date", "season", "HomeTeam", "AwayTeam", "FTHG", "FTAG"
    ]].copy()

    away["Team"] = away["AwayTeam"]
    away["Opponent"] = away["HomeTeam"]
    away["GoalsFor"] = away["FTAG"]
    away["GoalsAgainst"] = away["FTHG"]
    away["is_home"] = 0

    team_df = pd.concat([home, away], ignore_index=True)
    team_df = team_df.sort_values(["Team", "Date"])

    return team_df


# -----------------------------------
# 3. Compute rolling goal context
# -----------------------------------
def add_rolling_goal_context(team_df: pd.DataFrame) -> pd.DataFrame:
    team_df["last5_goals_for"] = (
        team_df.groupby("Team")["GoalsFor"]
        .transform(lambda s: s.shift().rolling(5).mean())
    )

    team_df["last5_goals_against"] = (
        team_df.groupby("Team")["GoalsAgainst"]
        .transform(lambda s: s.shift().rolling(5).mean())
    )

    return team_df


# -----------------------------------
# 4. Merge back to fixtures
# -----------------------------------
def merge_goal_context(df: pd.DataFrame, team_df: pd.DataFrame) -> pd.DataFrame:
    home_ctx = team_df[team_df["is_home"] == 1][
        ["Date", "Team", "last5_goals_for", "last5_goals_against"]
    ].rename(columns={
        "Team": "HomeTeam",
        "last5_goals_for": "home_last5_goals_scored",
        "last5_goals_against": "home_last5_goals_conceded",
    })

    away_ctx = team_df[team_df["is_home"] == 0][
        ["Date", "Team", "last5_goals_for", "last5_goals_against"]
    ].rename(columns={
        "Team": "AwayTeam",
        "last5_goals_for": "away_last5_goals_scored",
        "last5_goals_against": "away_last5_goals_conceded",
    })

    df = df.merge(home_ctx, on=["Date", "HomeTeam"], how="left")
    df = df.merge(away_ctx, on=["Date", "AwayTeam"], how="left")

    return df


# -----------------------------------
# 6. Main ingestion pipeline
# -----------------------------------
def main():
    # 1. Build context    
    df = load_historical_data()
    team_df = build_team_goal_table(df)
    team_df = add_rolling_goal_context(team_df)
    goal_context_df = merge_goal_context(df, team_df)
    goal_context_df = goal_context_df.dropna(subset=REQUIRED_GOAL_CONTEXT)

    # 2. Build vectors
    goal_vector_builder = GoalContextVectorBuilder()
    VECTOR_DIM = goal_vector_builder.VECTOR_DIM

    records = []    

    for idx, row in goal_context_df.iterrows():
        ctx = row.to_dict()        
        values = goal_vector_builder.build_single(ctx)

        record_id = f"goal-{idx}"
        
        validate_vector(
            values, 
            VECTOR_DIM, 
            record_id=record_id
        )

        records.append({
            "id": f"goal-{idx}",
            "values": values,   
            "metadata": {
                "season": row["season"],
                "date": str(row["Date"]),
                "home_team": row["HomeTeam"],
                "away_team": row["AwayTeam"],
                "fthg": int(row["FTHG"]),
                "ftag": int(row["FTAG"]),
            }   
        })   

    store = PineconeGoalVectorStore(
        index_name=INDEX_NAME,
        dimension=len(records[len(records)-1]["values"]),
        namespace=GOAL_NAMESPACE,
    )    

    for chunk in batch(records, batch_size=BATCH_SIZE):
        store.upsert(chunk)

    print(f"Ingested {len(records)} goal-market vectors.")


if __name__ == "__main__":
    main()

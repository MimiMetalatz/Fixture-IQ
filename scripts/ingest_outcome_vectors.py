from app.context.context_builder import ContextBuilder
from app.context.context_vector_builder import ContextVectorBuilder
from app.vector_store.pinecone_vector_store import PineconeVectorStore
from app.config.settings import settings
from app.utils.batch import batch

data_dir = settings.data_dir
outcome_market = settings.outcome_market_namespace
pinecone_outcome_index_name = settings.pinecone_outcome_index_name

def make_vector_id(row):
    return f"{row['season']}_{row['Date']}_{row['HomeTeam']}_{row['AwayTeam']}"


def main():
    # 1. Build context
    context_builder = ContextBuilder(data_dir=data_dir)
    context_df = context_builder.build()

    # 2. Build vectors
    vector_builder = ContextVectorBuilder()
    vectors_df = vector_builder.build(context_df)

    # 3. Init Pinecone
    store = PineconeVectorStore(
        index_name=pinecone_outcome_index_name,
        dimension=vectors_df.shape[1],
        namespace=outcome_market,
    )

    # 4. Prepare records
    records = []

    for idx, row in context_df.iterrows():
        records.append({
            "id": make_vector_id(row),
            "values": vectors_df.loc[idx].tolist(),
            "metadata": {
                "season": row["season"],
                "date": str(row["Date"]),
                "home_team": row["HomeTeam"],
                "away_team": row["AwayTeam"],
                "outcome": row["FTR"],
                "home_odds": float(row["AvgH"]),
                "draw_odds": float(row["AvgD"]),
                "away_odds": float(row["AvgA"]),
            }
        })

    # 5. Upsert (batching optional in v1)
    # store.upsert(records)
    for chunk in batch(records, batch_size=1000):
        store.upsert(chunk)


    print(f"Ingested {len(records)} historical fixtures.")


if __name__ == "__main__":
    main()

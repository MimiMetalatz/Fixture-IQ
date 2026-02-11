# Fixture-IQ

> A football match outcome prediction system that uses vector similarity search to find historically comparable fixtures and predict results based on past patterns.

## How It Works

1. **Context Building** — Extracts pre-match features: rolling form (last 5 games), goals scored/conceded, and betting odds
2. **Vector Embedding** — Converts match context into an 8-dimensional vector capturing relative strength, odds signals, and form coverage
3. **Similarity Search** — Queries Pinecone to find the 25 most similar historical fixtures
4. **Outcome Aggregation** — Calculates win/draw/loss rates from comparable matches
5. **Prediction & Explanation** — Generates a confidence-rated prediction with human-readable explanation

## Project Structure

```
Fixture-IQ/
├── app/
│   ├── context/
│   │   ├── context_builder.py        # Builds pre-match rolling form features
│   │   └── context_vector_builder.py # Converts context to numerical vectors
│   ├── data/
│   │   └── data_source.py            # Loads and validates match CSVs
│   ├── decision/
│   │   └── outcome_decision_engine.py # Makes predictions based on outcome rates
│   ├── explanation/
│   │   ├── spec_outcome_v1.py        # Frozen explanation format spec
│   │   ├── outcome_template.py       # Generates human-readable explanations
│   │   └── comparable_match_filter.py # Filters recent comparable matches
│   ├── utils/
│   │   └── aggregation.py            # Aggregates outcomes from similar matches
│   └── vector_store/
│       └── pinecone_vector_store.py  # Pinecone integration
├── data/
│   ├── raw/                          # Raw match CSV files
│   └── processed/                    # Processed data (if any)
├── notebooks/
│   └── main_workflow.py              # End-to-end prediction workflow
├── scripts/
│   └── ingest_outcome_vectors.py     # Ingests historical data into Pinecone
├── tests/
│   └── test_outcome_explanation_v1.py
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Fixture-IQ.git
cd Fixture-IQ
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 5. Add match data

Place your match CSV files in `data/raw/`. Each file should contain:

| Column   | Description              |
| -------- | ------------------------ |
| Date     | Match date (DD/MM/YYYY)  |
| HomeTeam | Home team name           |
| AwayTeam | Away team name           |
| FTHG     | Full-time home goals     |
| FTAG     | Full-time away goals     |
| FTR      | Full-time result (H/D/A) |
| AvgH     | Average home win odds    |
| AvgD     | Average draw odds        |
| AvgA     | Average away win odds    |

Data source: [Football-Data.co.uk](https://www.football-data.co.uk/)

## Usage

### Ingest historical data

Run once to populate Pinecone with historical fixtures:

```bash
python scripts/ingest_outcome_vectors.py
```

### Make predictions

Edit `notebooks/main_workflow.py` with your fixture details:

```python
fixture_context = context_builder.build_single_context(
    home_team="Arsenal",
    away_team="Chelsea",
    home_odds=2.10,
    draw_odds=3.40,
    away_odds=3.50,
)
```

Then run:

```bash
python notebooks/main_workflow.py
```

### Example output

```
FixtureIQ – Outcome Assessment (Pre-Kickoff)

Based on the pre-match context, this fixture shows a moderate confidence lean toward the home side.
Comparable historical matches with similar balance, strength, and uncertainty have seen this outcome
occur more often, though alternative outcomes remain realistic.

Across comparable past fixtures:
Home wins: 48% · Draws: 24% · Away wins: 28%

Prediction: Home win
Confidence: Moderate

Recent comparable fixtures (this season and last):
• Liverpool vs Man City (2025/26) – Home win
• Arsenal vs Chelsea (2024/25) – Draw
```

## Testing

```bash
pytest tests/ -v
```

## Vector Dimensions

The context vector has 8 dimensions:

| Index | Feature                   | Description                                  |
| ----- | ------------------------- | -------------------------------------------- |
| 0     | delta_last5_points        | Home minus away points (last 5)              |
| 1     | delta_last5_goals_for     | Home minus away goals scored (last 5)        |
| 2     | delta_last5_goals_against | Home minus away goals conceded (last 5)      |
| 3     | odds_favorite_strength    | Max implied probability (home or away)       |
| 4     | odds_balance              | Absolute difference in implied probabilities |
| 5     | draw_probability          | Implied draw probability from odds           |
| 6     | home_bias                 | Home minus away implied probability          |
| 7     | avg_form_coverage         | Completeness of form data (0-1)              |

```

## Logging goals (v1)

Logging should answer post-hoc questions like:
• Why did FixtureIQ lean this way?
• Was confidence justified?
• Did the explanation follow the frozen spec?

Log these (structured, low volume):

1. Decision inputs
   • prediction
   • confidence
   • outcome rates (H/D/A)
2. Retrieval summary
   • # of neighbors used
   • seasons represented
   • whether recent comparable fixtures were found
3. Explanation version
   • schema version (outcome_v1)
   • confidence wording variant used
```

## License

MIT

## Contributing

Pull requests welcome. For major changes, please open an issue first.

```

```

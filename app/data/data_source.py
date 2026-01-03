from pathlib import Path
from typing import List, Optional
import pandas as pd


class MatchDataSource:
    """
    Reads raw football match CSV files from a local data directory.
    Designed to be extended later for AWS S3.
    """

    def __init__(
        self,
        data_dir: str | Path,
        csv_extension: str = ".csv",
        date_format: str = "%d/%m/%Y",
    ):
        self.data_dir = Path(data_dir)
        self.csv_extension = csv_extension
        self.date_format = date_format

        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory does not exist: {self.data_dir}")

    # ---------- Public API ----------

    def list_files(self) -> List[Path]:
        """
        Return all CSV files in the data directory.
        """
        return sorted(
            p for p in self.data_dir.iterdir()
            if p.is_file() and p.suffix == self.csv_extension
        )

    def load_all_matches(self) -> pd.DataFrame:
        """
        Load and concatenate all match CSV files into a single DataFrame.
        """
        files = self.list_files()
        if not files:
            raise RuntimeError(f"No CSV files found in {self.data_dir}")

        frames = []
        for path in files:
            df = self._load_single_file(path)
            frames.append(df)

        combined = pd.concat(frames, ignore_index=True)
        combined = self._postprocess(combined)

        return combined

    # ---------- Internal helpers ----------

    def _load_single_file(self, path: Path) -> pd.DataFrame:
        """
        Load a single CSV file and apply minimal normalization.
        """
        df = pd.read_csv(path)

        # Required columns (fail fast if missing)
        required = [
            "Date", "HomeTeam", "AwayTeam",
            "FTHG", "FTAG", "FTR",
            "AvgH", "AvgD", "AvgA"
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"{path.name} missing columns: {missing}")

        # Keep only what we need at this layer
        df = df[required].copy()

        # Parse date
        df["Date"] = pd.to_datetime(
            df["Date"],
            format=self.date_format,
            errors="coerce"
        )

        # Attach season label from filename (e.g. 2324.csv → 2324)
        df["season"] = path.stem

        # Ensure numeric types
        for col in ["FTHG", "FTAG", "AvgH", "AvgD", "AvgA"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def _postprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Final normalization step after all files are loaded.
        """
        # Drop rows with invalid dates
        df = df.dropna(subset=["Date"])

        # Sort chronologically
        df = df.sort_values(
            ["season", "Date", "HomeTeam", "AwayTeam"]
        ).reset_index(drop=True)

        return df

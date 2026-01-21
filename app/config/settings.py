from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict  


class Settings(BaseSettings):
    # --- Pinecone --- 
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_cloud : str = "aws"
    pinecone_batch_size: int = 1000

    pinecone_outcome_index_name: str
    pinecone_goal_index_name: str

    outcome_market_namespace: str = "outcome_market"
    goal_market_namespace: str = "goal_market"

    # --- Data ---
    data_dir: Path = Path("data/raw")   

    # class Config:
    #    env_file = ".env"
    # --- Newer Pydantic v2 style ---
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

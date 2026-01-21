from pinecone import Pinecone, ServerlessSpec
from app.config.settings import settings

pinecone_api_key = settings.pinecone_api_key
pinecone_environment = settings.pinecone_environment    
goal_market_namespace = settings.goal_market_namespace
pinecone_cloud = settings.pinecone_cloud

class PineconeGoalVectorStore:
    def __init__(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        namespace: str = goal_market_namespace,
    ):        
        api_key = pinecone_api_key
        if not api_key:
            raise RuntimeError("Missing PINECONE_API_KEY")

        self.namespace = namespace or goal_market_namespace
        self.index_name = index_name

        self.pc = Pinecone(api_key=api_key)

        indexes = self.pc.list_indexes()
        existing_indexes = (
            [idx.name for idx in indexes.indexes] 
            if hasattr(indexes, 'indexes') 
            else indexes
        )

        if index_name not in existing_indexes:
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=pinecone_cloud,
                    region=pinecone_environment,
                )
            )
            self.pc.describe_index(index_name) # This prevents querying before the index is ready

        self.index = self.pc.Index(index_name)

    def upsert(self, vectors):
        self.index.upsert(
            vectors=vectors,
            namespace=self.namespace,
        )
            
    def query(self, vector: list[float], top_k: int = 25, include_metadata: bool = True) -> list[dict]:
        res = self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=include_metadata,
            namespace=self.namespace,            
        )

        return [
            {
                "id": m.id,
                "score": m.score,
                "metadata": m.metadata

            }
            for m in res.matches
        ]

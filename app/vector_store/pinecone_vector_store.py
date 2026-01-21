import os
from pinecone import Pinecone, ServerlessSpec


class PineconeVectorStore:
    def __init__(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        namespace: str = "outcome_market",
    ):
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("Missing PINECONE_API_KEY")

        self.namespace = namespace
        self.index_name = index_name

        self.pc = Pinecone(api_key=api_key)

        existing_indexes = [i["name"] for i in self.pc.list_indexes()]

        if index_name not in existing_indexes:
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

        self.index = self.pc.Index(index_name)

    def upsert(self, vectors):
        self.index.upsert(
            vectors=vectors,
            namespace=self.namespace,
        )

    def query(self, vector:list[float], top_k: int = 25, include_metadata=True) -> list[dict]:
        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=include_metadata,
            namespace=self.namespace,
        )

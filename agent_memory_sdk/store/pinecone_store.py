import os
import json
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

import pinecone

from ..models import MemoryEntry, MemoryType
from ..utils.embedding_utils import generate_embedding
from .base_store import BaseStore


class PineconeStore(BaseStore):
    def __init__(self, api_key: str = None, environment: str = None,
                 index_name: str = "agent-memory-os", dimension: int = 1024,
                 metric: str = "cosine", **kwargs):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.environment = environment or os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric

        if not self.api_key:
            raise ValueError("Pinecone API key is required. Set PINECONE_API_KEY environment variable or pass api_key parameter.")

        pinecone.init(api_key=self.api_key, environment=self.environment)

        existing_index_names = pinecone.list_indexes()
        if self.index_name not in existing_index_names:
            pinecone.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=pinecone.ServerlessSpec(cloud="aws", region="us-east-1")
            )
            while True:
                status = pinecone.describe_index(self.index_name).status
                if status.get("ready"):
                    break
                time.sleep(1)

        self.index = pinecone.Index(self.index_name)

    def upsert(self, vectors: List[dict]):
        self.index.upsert(vectors)

    def query(self, vector: List[float], top_k: int = 5, include_metadata: bool = True):
        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=include_metadata
        )

    def delete(self, ids: List[str]):
        self.index.delete({"ids": ids})
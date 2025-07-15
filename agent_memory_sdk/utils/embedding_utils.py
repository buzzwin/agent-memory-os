"""
Embedding utility functions for Agent Memory OS

Provides helper functions for generating embeddings and calculating similarities.
"""

import numpy as np
from typing import List, Optional
import hashlib


def generate_embedding(text: str, model: str = "simple") -> List[float]:
    """
    Generate embedding for text
    
    Args:
        text: Text to embed
        model: Embedding model to use (simple hash-based for now)
        
    Returns:
        List of float values representing the embedding
    """
    if model == "simple":
        # Simple hash-based embedding for demo purposes
        # In production, use proper embedding models like OpenAI, sentence-transformers, etc.
        hash_obj = hashlib.sha256(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hex to list of floats
        embedding = []
        for i in range(0, len(hash_hex), 8):
            chunk = hash_hex[i:i+8]
            if len(chunk) == 8:
                # Convert hex to float between -1 and 1
                value = int(chunk, 16) / (16**8 - 1) * 2 - 1
                embedding.append(value)
        
        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.extend(embedding[:min(384 - len(embedding), len(embedding))])
        
        return embedding[:384]
    
    else:
        raise ValueError(f"Unsupported embedding model: {model}")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score between -1 and 1
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same length")
    
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


def find_similar_embeddings(query_embedding: List[float], 
                          embeddings: List[List[float]], 
                          threshold: float = 0.5) -> List[int]:
    """
    Find embeddings similar to query embedding
    
    Args:
        query_embedding: Query embedding vector
        embeddings: List of embeddings to search
        threshold: Similarity threshold
        
    Returns:
        List of indices of similar embeddings
    """
    similar_indices = []
    
    for i, embedding in enumerate(embeddings):
        similarity = cosine_similarity(query_embedding, embedding)
        if similarity >= threshold:
            similar_indices.append(i)
    
    return similar_indices


def normalize_embedding(embedding: List[float]) -> List[float]:
    """
    Normalize embedding vector to unit length
    
    Args:
        embedding: Input embedding vector
        
    Returns:
        Normalized embedding vector
    """
    vec = np.array(embedding)
    norm = np.linalg.norm(vec)
    
    if norm == 0:
        return embedding
    
    return (vec / norm).tolist() 
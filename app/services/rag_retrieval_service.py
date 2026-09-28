import os
from typing import Any

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from app.db.mongodb import db


load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

INDEX_NAME = "civicpulse-government-policies"
MODEL_NAME = "intfloat/multilingual-e5-base"

embedding_model = SentenceTransformer(MODEL_NAME)

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

rag_chunks_collection = db["rag_chunks"]


def retrieve_policy_chunks(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve relevant government policy chunks.

    Flow:
        query
          ↓
        E5 embedding
          ↓
        Pinecone semantic search
          ↓
        chunk IDs
          ↓
        MongoDB chunk text + metadata
    """

    # E5 expects the query prefix for retrieval queries
    query_embedding = embedding_model.encode(
        f"query: {query}",
        normalize_embeddings=True,
    ).tolist()

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    matches = results.get("matches", [])

    if not matches:
        return []

    chunk_ids = [
        match["id"]
        for match in matches
    ]

    # Fetch the actual chunk text from MongoDB
    documents = rag_chunks_collection.find(
        {
            "chunk_id": {
                "$in": chunk_ids
            }
        },
        {
            "_id": 0,
            "chunk_id": 1,
            "text": 1,
            "metadata": 1,
        },
    )

    documents_by_id = {
        document["chunk_id"]: document
        for document in documents
    }

    retrieved_chunks = []

    # Preserve Pinecone ranking order
    for match in matches:
        chunk_id = match["id"]

        document = documents_by_id.get(chunk_id)

        if not document:
            continue

        metadata = document.get("metadata", {})

        retrieved_chunks.append(
            {
                "chunk_id": chunk_id,
                "score": match["score"],
                "text": document["text"],
                "title": metadata.get("title"),
                "page": metadata.get("page"),
                "section": metadata.get("section"),
                "document_type": metadata.get("document_type"),
                "source": metadata.get("source"),
                "domain": metadata.get("domain"),
            }
        )

    return retrieved_chunks
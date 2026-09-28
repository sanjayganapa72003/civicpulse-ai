import os
from typing import Any

from dotenv import load_dotenv
from pinecone import Pinecone
import voyageai

from app.db.mongodb import db


load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

INDEX_NAME = "civicpulse-government-policies-voyage"
MODEL_NAME = "voyage-4-lite"
EMBEDDING_DIMENSION = 1024


pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(
    INDEX_NAME
)

voyage_client = voyageai.Client(
    api_key=VOYAGE_API_KEY
)

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
        Voyage query embedding
          ↓
        Pinecone semantic search
          ↓
        chunk IDs
          ↓
        MongoDB chunk text + metadata
    """

    response = voyage_client.embed(
        [query],
        model=MODEL_NAME,
        input_type="query",
        output_dimension=EMBEDDING_DIMENSION,
    )

    query_embedding = response.embeddings[0]

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    matches = results.get(
        "matches",
        []
    )

    if not matches:
        return []

    chunk_ids = [
        match["id"]
        for match in matches
    ]

    # Fetch actual chunk text from MongoDB
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

        document = documents_by_id.get(
            chunk_id
        )

        if not document:
            continue

        metadata = document.get(
            "metadata",
            {}
        )

        retrieved_chunks.append(
            {
                "chunk_id": chunk_id,
                "score": match["score"],
                "text": document["text"],
                "title": metadata.get("title"),
                "page": metadata.get("page"),
                "section": metadata.get("section"),
                "document_type": metadata.get(
                    "document_type"
                ),
                "source": metadata.get(
                    "source"
                ),
                "domain": metadata.get(
                    "domain"
                ),
            }
        )

    return retrieved_chunks
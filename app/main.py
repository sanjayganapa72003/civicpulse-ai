from fastapi import UploadFile, FastAPI, File, HTTPException
from datetime import datetime, timezone
from app.services.demographics_service import get_demographics
from app.db.mongodb import citizen_requests_collection
from app.services.citizen_request_service import extract_citizen_request
from app.schemas.citizen_request import CitizenRequestCreate
from app.services.demand_service import get_district_demand
from app.services.infrastructure_service import get_district_infrastructure
from app.services.gap_service import calculate_gaps
from app.services.priority_service import build_priority_scores
from app.services.hotspot_service import get_hotspots
from app.services.rag_retrieval_service import retrieve_policy_chunks
from app.services.hotspot_policy_service import get_hotspot_policy_context
from app.services.rag_generation_service import generate_policy_answer
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from app.services.voice_service import transcribe_audio

app = FastAPI(
    title="CivicPulse AI",
    description="Multilingual Citizen Demand Intelligence Platform",
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/demographics/{district}")
def demographics(district: str):
    result = get_demographics(district)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="District not found",
        )

    return result

@app.post("/api/citizen-requests")
async def create_citizen_request(request: CitizenRequestCreate):

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Citizen request cannot be empty",
        )

    extracted = await extract_citizen_request(request.text)

    document = {
        "raw_text": request.text.strip(),

        "language": extracted["language"],
        "category": extracted["category"],
        "issue_type": extracted["issue_type"],
        "severity": extracted["severity"],

        "location": {
            "state": "Karnataka",
            "district": extracted.get("district") or request.district,
            "taluk": extracted.get("taluk") or request.taluk,
            "village": extracted.get("village") or request.village,
        },

        "source": request.source,

        "created_at": datetime.now(timezone.utc),
    }

    result = citizen_requests_collection.insert_one(document)

    return {
        "message": "Citizen request processed successfully",
        "request_id": str(result.inserted_id),
        "extracted": {
            "language": document["language"],
            "category": document["category"],
            "issue_type": document["issue_type"],
            "severity": document["severity"],
            "location": document["location"],
        },
    }

@app.get("/api/demand/districts")
async def get_demand_by_district():
    return get_district_demand()

@app.get("/api/infrastructure/districts")
async def get_infrastructure_by_district():
    return get_district_infrastructure()

@app.get("/api/gaps/districts")
async def get_district_gaps():
    return calculate_gaps()

@app.get("/api/priorities")
async def get_priorities():
    return build_priority_scores()

@app.get("/api/hotspots")
async def get_hotspot_list(limit: int = 10):
    return get_hotspots(limit)

@app.get("/api/rag/retrieve")
async def retrieve_rag_chunks(
    query: str,
    top_k: int = 5,
):
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty",
        )

    if top_k < 1 or top_k > 10:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 10",
        )

    results = retrieve_policy_chunks(
        query=query,
        top_k=top_k,
    )

    return {
        "query": query,
        "results": results,
    }

@app.get("/api/hotspots/{district}/{category}/policy")
def get_hotspot_policy(
    district: str,
    category: str,
):
    """
    Return government policy evidence and policy relevance
    for a development hotspot.
    """

    context = get_hotspot_policy_context(
        district=district,
        category=category,
        top_k=5,
    )

    if not context.get("available"):
        return context

    development_context = {
        "district": context["district"],
        "category": context["category"],
        "issue_type": context["issue_type"],
        "gap_description": context["gap_description"],
        "priority": context["priority"],
    }

    policy_answer = generate_policy_answer(
        query=context["retrieval_query"],
        top_k=5,
        development_context=development_context,
    )

    return {
        "district": district,
        "category": category,
        "issue_type": context["issue_type"],
        "gap_description": context["gap_description"],
        "priority": context["priority"],
        "policy": policy_answer,
    }

@app.post("/api/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...)
):
    try:
        audio_bytes = await audio.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=400,
                detail="Empty audio file."
            )

        transcript = transcribe_audio(
            audio_bytes=audio_bytes,
            mime_type=audio.content_type or "audio/webm",
        )

        return {
            "transcript": transcript
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(
            f"[Voice Transcription] "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Voice transcription failed."
        )

app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)




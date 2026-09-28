# CivicPulse AI

## Citizen Voice → Infrastructure Intelligence → Development Priorities

CivicPulse AI is an AI-powered civic intelligence platform that transforms multilingual citizen requests into structured infrastructure demand, identifies geographic hotspots, evaluates infrastructure gaps, and provides policy-aligned intelligence for decision-makers.

The current MVP focuses on **Karnataka** and covers three infrastructure domains:

- Road connectivity
- Water infrastructure
- Healthcare accessibility

Citizens can submit requests through **text or voice** in:

- English
- Hindi
- Kannada

CivicPulse connects citizen demand with demographic data, infrastructure data, and government policy documents to help identify areas requiring development attention.

---

# 1. Problem

Citizen feedback is often:

- Unstructured
- Multilingual
- Geographically fragmented
- Difficult to aggregate
- Difficult to connect with existing infrastructure
- Difficult to connect with government policies and development programs

For example:

> "There are so many water problems in Mysuru."

This is valuable citizen feedback, but by itself it does not provide a decision-maker with enough context to understand the scale, geographic concentration, infrastructure situation, or relevant government policy.

CivicPulse converts such requests into structured intelligence:

```text
Citizen Voice
      ↓
Citizen Demand
      ↓
Geographic Hotspot
      ↓
Infrastructure Gap
      ↓
Policy Context
      ↓
Development Priority
```

---

# 2. Solution

CivicPulse combines:

- Large Language Models
- Multilingual request understanding
- Voice transcription
- MongoDB
- Government infrastructure datasets
- Demographic data
- Deterministic analytics
- Pinecone vector search
- Retrieval-Augmented Generation (RAG)

The overall workflow is:

```text
                         ┌─────────────────────┐
                         │      Citizen        │
                         │   Text / Voice      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   AI Processing     │
                         │                     │
                         │ Language Detection  │
                         │ Speech-to-Text      │
                         │ Category Extraction │
                         │ Entity Extraction   │
                         │ Severity Detection  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      MongoDB        │
                         │                     │
                         │ Citizen Requests    │
                         │ Demographics        │
                         │ Infrastructure      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Demand Intelligence │
                         │                     │
                         │ Request Aggregation │
                         │ Category Analysis   │
                         │ Severity Analysis   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Infrastructure Gap  │
                         │      Analysis       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Priority Hotspots   │
                         │                     │
                         │ Deterministic Score │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Government RAG    │
                         │                     │
                         │ Policy Documents    │
                         │ Pinecone Retrieval  │
                         │ Gemini Generation   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Decision-Maker   │
                         │      Dashboard      │
                         └─────────────────────┘
```

---

# 3. Core Workflow

CivicPulse follows:

```text
Citizen → Demand → Hotspot → Infrastructure Gap → Policy Context → Priority
```

## Step 1 — Citizen Request

A citizen submits a request using text or voice.

Example:

```text
There are so many water issues in Mysuru.
```

## Step 2 — AI Request Understanding

Gemini converts the unstructured request into structured information.

Example:

```json
{
  "language": "english",
  "category": "water",
  "issue_type": "water infrastructure issue",
  "district": "Mysore",
  "taluk": null,
  "village": null,
  "severity": 4
}
```

The application normalizes district names to canonical names used by the datasets.

Examples:

```text
Mysuru       → Mysore
Ballari      → Bellary
Belagavi     → Belgaum
Vijayapura   → Bijapur
Kalaburagi   → Gulbarga
Davangere    → Davanagere
```

## Step 3 — Demand Aggregation

Citizen requests are aggregated by:

- District
- Infrastructure category
- Request count
- Average severity

This converts individual citizen requests into district-level demand signals.

## Step 4 — Infrastructure Analysis

Demand is combined with available infrastructure data covering:

- Roads
- Water
- Healthcare

## Step 5 — Infrastructure Gap

Where measurable indicators are available, CivicPulse calculates an infrastructure gap.

Examples:

```text
Water Gap = 1 - Household Tap Coverage
```

```text
Road Gap = 1 - Road Completion Ratio
```

Healthcare data currently does not use an invented benchmark.

## Step 6 — Priority Scoring

The system combines:

- Demand
- Severity
- Infrastructure gap
- Population

to calculate a transparent deterministic priority score.

## Step 7 — Policy Intelligence

For a selected hotspot, CivicPulse retrieves relevant government policy information using RAG.

This provides decision-makers with policy and infrastructure context relevant to the identified problem.

---

# 4. AI Architecture

CivicPulse intentionally separates **AI interpretation** from **deterministic analytical computation**.

## LLM Responsibilities

Gemini is used for:

- Multilingual citizen-request understanding
- Language identification
- Category extraction
- Issue-type extraction
- District extraction
- Taluk/village extraction when explicitly provided
- Severity interpretation
- Voice transcription
- Policy-context generation

## Deterministic Responsibilities

Python services perform:

- Request aggregation
- Category-wise demand calculations
- Severity aggregation
- Infrastructure-gap calculations
- Population normalization
- Priority scoring

This separation makes the analytical pipeline more transparent.

> **LLMs interpret unstructured information; deterministic services perform measurable calculations.**

The LLM does not directly determine the final hotspot score.

The RAG system provides policy context and does not modify the priority score.

---

# 5. Multilingual Citizen Intelligence

CivicPulse currently supports:

```text
English
Hindi
Kannada
```

The request-processing pipeline identifies the language and extracts structured information from the citizen's request.

For example:

```text
There are so many water issues in Mysuru.
```

can be converted into:

```text
Category → Water
District → Mysore
Severity → Extracted by Gemini
Language → English
```

District normalization prevents spelling and naming variations from becoming separate analytical entities.

---

# 6. Voice Processing

CivicPulse supports voice-based citizen requests.

The browser uses the `MediaRecorder` API to capture audio.

The voice-processing pipeline is:

```text
Microphone
    ↓
Browser Audio Recording
    ↓
WebM / Opus Audio
    ↓
FastAPI /api/transcribe
    ↓
FFmpeg
    ↓
Gemini Audio Transcription
    ↓
Transcript
    ↓
Citizen Request Processing
```

The resulting transcript is placed into the citizen request input box and can then be analyzed through the normal citizen-request pipeline.

---

# 7. Demand Intelligence

CivicPulse aggregates citizen requests to identify demand patterns.

Demand is analyzed by:

- District
- Infrastructure category
- Number of requests
- Average severity
- Category-specific severity

Example:

```json
{
  "Belgaum": {
    "total_requests": 31,
    "road": 9,
    "water": 15,
    "healthcare": 7,
    "average_severity": 3.03
  }
}
```

The aggregation layer provides the demand signals used by the priority engine.

---

# 8. Infrastructure Intelligence

CivicPulse combines citizen demand with government infrastructure datasets.

Current infrastructure domains:

```text
Roads
Water
Healthcare
```

This enables the system to distinguish between:

```text
High citizen demand
        +
Existing infrastructure context
        ↓
Infrastructure priority signal
```

---

# 9. Infrastructure Gap Analysis

CivicPulse only calculates infrastructure gaps where the available data supports a meaningful calculation.

## Water

The current water gap is based on household tap coverage:

```text
Water Gap =
1 - Household Tap Coverage
```

A district with lower household tap coverage therefore has a larger measurable coverage gap.

## Roads

The road gap is based on the relationship between completed and sanctioned road length:

```text
Completion Ratio =
Road Length Completed /
Road Length Sanctioned
```

Therefore:

```text
Road Gap =
1 - Completion Ratio
```

## Healthcare

The current healthcare datasets contain facility information such as:

- Community Health Centres
- Primary Health Centres
- General Hospitals

The MVP does not invent a facility-per-population benchmark.

Therefore healthcare facility counts are currently used as infrastructure context rather than an unsupported calculated gap.

---

# 10. Priority Hotspot Scoring

CivicPulse uses a transparent deterministic scoring model.

```text
Priority Score =
    0.35 × Demand
  + 0.25 × Severity
  + 0.30 × Infrastructure Gap
  + 0.10 × Population
```

## Demand — 35%

Category-specific request volume is normalized relative to the maximum category demand.

```text
Demand Score =
Category Requests /
Maximum Category Requests
```

## Severity — 25%

Average category severity is normalized against the 1–5 scale.

```text
Severity Score =
Average Severity / 5
```

## Infrastructure Gap — 30%

Uses measurable infrastructure indicators where available.

Examples:

```text
Water Gap = 1 - Household Tap Coverage
```

```text
Road Gap = 1 - Completion Ratio
```

## Population — 10%

District population is normalized against the maximum population in the available demographic dataset.

---

# 11. Government Policy RAG

CivicPulse uses Retrieval-Augmented Generation to connect infrastructure hotspots with relevant government policy documents.

The policy intelligence pipeline is:

```text
Government PDF
      ↓
Document Extraction
      ↓
Chunking
      ↓
Multilingual Embeddings
      ↓
Pinecone
      ↓
Semantic Retrieval
      ↓
Relevant Policy Chunks
      ↓
Gemini
      ↓
Policy Intelligence
```

## Embedding Model

```text
intfloat/multilingual-e5-base
```

Embedding dimension:

```text
768
```

## Vector Database

```text
Pinecone
```

Index:

```text
civicpulse-government-policies
```

Similarity metric:

```text
Cosine
```

---

# 12. Government Policy Corpus

The current policy corpus contains seven government documents.

## Water

### Jal Jeevan Mission

```text
JJM 2.0 Operational Guidelines
```

### Water Quality

```text
Drinking Water Quality Monitoring & Surveillance Framework
```

## Roads

```text
PMGSY-III Programme Guidelines
```

## Healthcare

```text
IPHS District/Sub-District Hospital 2022
IPHS CHC 2022
IPHS PHC 2022
```

## Infrastructure Planning

```text
PM GatiShakti National Master Plan
```

These documents are chunked, embedded, and indexed in Pinecone for semantic retrieval.

---

# 13. Data Sources

CivicPulse uses official government datasets and policy documents.

## Road Infrastructure

Source:

```text
Karnataka Open Government Data
```

Dataset:

```text
PMGSY Road Infrastructure
```

Indicators include:

- Road Length Sanctioned
- Road Length Completed
- Balance Road Length

---

## Water Infrastructure

Source:

```text
Karnataka Open Government Data
```

Dataset:

```text
Jal Jeevan Mission
```

Indicators include:

- PWS Villages
- Total Households
- Households with Tap Connection
- Villages with 100% FHTC
- Household Tap Coverage

---

## Healthcare

Source:

```text
Karnataka Open Government Data
Karnataka Health and Family Welfare Department
```

Datasets cover:

- Community Health Centres
- Primary Health Centres
- General Hospitals

---

## Demographics

Source:

```text
Census of India 2011
```

District-level demographic information includes:

- Population
- Rural Population
- Urban Population
- Households

---

# 14. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI |
| LLM | Google Gemini |
| Voice Transcription | Gemini |
| Database | MongoDB |
| Vector Database | Pinecone |
| Embeddings | `intfloat/multilingual-e5-base` |
| RAG | Pinecone + Gemini |
| Analytics | Python |
| Data Processing | Python / Pandas |
| Audio Processing | FFmpeg |

---

# 15. Project Structure

```text
civicpulse-ai/
│
├── app/
│   ├── db/
│   │   └── mongodb.py
│   │
│   ├── models/
│   │   ├── citizen_request.py
│   │   ├── demographics.py
│   │   └── infrastructure.py
│   │
│   ├── schemas/
│   │   └── citizen_request.py
│   │
│   ├── services/
│   │   ├── citizen_request_service.py
│   │   ├── demand_service.py
│   │   ├── demographics_service.py
│   │   ├── gap_service.py
│   │   ├── hotspot_policy_service.py
│   │   ├── hotspot_service.py
│   │   ├── infrastructure_service.py
│   │   ├── priority_service.py
│   │   ├── rag_generation_service.py
│   │   ├── rag_retrieval_service.py
│   │   └── voice_service.py
│   │
│   ├── main.py
│   └── ui.py
│
├── frontend/
│   ├── index.html
│   └── styles.css
│
├── scripts/
│   ├── create_district_mapping.py
│   ├── create_embedding_batch.py
│   ├── create_pinecone_index.py
│   ├── extract_healthcare.py
│   ├── extract_karnataka_demographics.py
│   ├── extract_roads.py
│   ├── extract_water.py
│   ├── generate_embeddings.py
│   ├── generate_synthetic_requests.py
│   ├── ingest_demographics.py
│   ├── ingest_healthcare.py
│   ├── ingest_rag_chunks.py
│   ├── ingest_rag_documents.py
│   ├── ingest_roads.py
│   ├── ingest_water.py
│   ├── submit_embedding_batch.py
│   ├── test_government_policy_retrieval.py
│   ├── test_hotspot_policy.py
│   ├── test_pinecone_retrieval.py
│   ├── test_rag_generation.py
│   ├── test_rag_retrieval.py
│   └── upload_embeddings_to_pinecone.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── rag/
│
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── test_gemini.py
└── test_mongo.py
```

---

# 16. Prerequisites

Before running CivicPulse locally, install:

- Python 3.11+
- MongoDB Community Server
- FFmpeg
- Git

You also need:

- Google Gemini API key
- Pinecone API key

---

# 17. Installation

## Step 1 — Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd civicpulse-ai
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the repository URL.

---

## Step 2 — Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# 18. MongoDB Setup

CivicPulse uses MongoDB for:

- Citizen requests
- Demographic data
- Infrastructure data

Default local configuration:

```text
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=civicpulse
```

Make sure MongoDB is running before starting the application.

You can verify the connection using:

```bash
python test_mongo.py
```

---

# 19. FFmpeg Setup

FFmpeg is required for voice transcription.

Verify that FFmpeg is available:

```powershell
ffmpeg -version
```

If the command is not recognized, install FFmpeg and make sure its executable is available through the system `PATH`.

---

# 20. Environment Configuration

Create a `.env` file in the project root.

Example:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=civicpulse

GEMINI_API_KEY=your_gemini_api_key_here

PINECONE_API_KEY=your_pinecone_api_key_here
```

The `.env.example` file provides the expected configuration structure.

### Never commit `.env`

The actual `.env` file is intentionally excluded from Git.

Never put real API keys in:

- Source code
- README
- `.env.example`
- GitHub commits

---

# 21. Verify Gemini Configuration

The repository contains:

```text
test_gemini.py
```

Run:

```bash
python test_gemini.py
```

This can be used to verify that the Gemini configuration is available.

---

# 22. Data Pipeline

The project contains separate extraction and ingestion scripts for the government datasets.

The general workflow is:

```text
Raw Government Dataset
        ↓
Extraction
        ↓
Normalization
        ↓
Processed Dataset
        ↓
MongoDB
```

The raw and processed data directories are intentionally excluded from Git because of their size.

---

# 23. Demographic Data

The demographic pipeline processes Census data for Karnataka.

Relevant scripts:

```text
scripts/extract_karnataka_demographics.py
scripts/ingest_demographics.py
```

The resulting district-level demographic information contains:

```text
State
District
Population
Rural Population
Urban Population
Households
Data Year
Source
```

---

# 24. Road Data

Relevant scripts:

```text
scripts/extract_roads.py
scripts/ingest_roads.py
```

Road data includes:

```text
Road Length Sanctioned
Road Length Completed
Balance Road Length
```

District names are normalized to match the canonical district naming used throughout the application.

---

# 25. Water Data

Relevant scripts:

```text
scripts/extract_water.py
scripts/ingest_water.py
```

Water data includes:

```text
PWS Villages
Total Households
Households with Tap Connection
Villages with 100% FHTC
Household Tap Coverage
```

---

# 26. Healthcare Data

Relevant scripts:

```text
scripts/extract_healthcare.py
scripts/ingest_healthcare.py
```

Healthcare datasets include:

```text
Community Health Centres
Primary Health Centres
General Hospitals
```

Healthcare data is treated carefully because absence from a particular facility dataset does not automatically mean that the facility count is zero.

---

# 27. Synthetic Citizen Requests

The MVP uses synthetic citizen requests for demonstration.

The generator is:

```text
scripts/generate_synthetic_requests.py
```

The generated data is used to demonstrate:

```text
Citizen Requests
      ↓
Demand Aggregation
      ↓
Hotspot Detection
      ↓
Infrastructure Gap
      ↓
Priority Score
```

> **Demo Data Notice:** Citizen requests shown in the prototype are synthetic and are not actual citizen complaints.

This distinction prevents demonstration data from being represented as real public feedback.

---

# 28. RAG Document Ingestion

The policy RAG pipeline processes government PDFs.

Relevant scripts include:

```text
scripts/ingest_rag_documents.py
scripts/ingest_rag_chunks.py
scripts/generate_embeddings.py
scripts/create_embedding_batch.py
scripts/submit_embedding_batch.py
scripts/create_pinecone_index.py
scripts/upload_embeddings_to_pinecone.py
```

The conceptual pipeline is:

```text
Government PDFs
      ↓
Document Extraction
      ↓
Chunking
      ↓
Embedding Generation
      ↓
Pinecone Index
      ↓
Semantic Retrieval
      ↓
Gemini
```

---

# 29. Pinecone Setup

CivicPulse uses Pinecone for government-policy vector retrieval.

The application expects:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
```

The intended index is:

```text
civicpulse-government-policies
```

The embedding model is:

```text
intfloat/multilingual-e5-base
```

with:

```text
Dimension: 768
Metric: cosine
```

The repository includes:

```text
scripts/create_pinecone_index.py
scripts/upload_embeddings_to_pinecone.py
scripts/test_pinecone_retrieval.py
```

for the Pinecone workflow.

---

# 30. Test RAG Retrieval

The repository contains tests for the retrieval pipeline:

```text
scripts/test_rag_retrieval.py
scripts/test_government_policy_retrieval.py
```

These can be used to validate semantic retrieval from the policy corpus.

---

# 31. Policy Generation

After relevant policy chunks are retrieved, Gemini generates policy intelligence based on the retrieved context.

Relevant components:

```text
app/services/rag_retrieval_service.py
app/services/rag_generation_service.py
app/services/hotspot_policy_service.py
```

The policy generation layer is separate from the deterministic priority-scoring layer.

---

# 32. Run the Application

After MongoDB and the required environment variables are configured:

```bash
uvicorn app.main:app --reload
```

The FastAPI application serves the CivicPulse backend and frontend.

Open the local application in a browser using the URL shown by Uvicorn.

---

# 33. API Endpoints

The current application exposes APIs supporting the main CivicPulse workflow.

## Citizen Requests

```http
POST /api/citizen-requests
```

Processes a citizen request and stores the structured result.

---

## Voice Transcription

```http
POST /api/transcribe
```

Accepts recorded audio and returns the generated transcript.

---

## Demand

```http
GET /api/demand
```

Returns aggregated citizen demand.

---

## Infrastructure

```http
GET /api/infrastructure/districts
```

Returns district-level infrastructure and demographic information.

---

## Hotspots

```http
GET /api/hotspots
```

Returns priority hotspot information.

---

## Policy Intelligence

```http
GET /api/hotspots/{district}/{category}/policy
```

Retrieves relevant government policy context for a selected district/category hotspot.

---

# 34. Example End-to-End Request

A citizen submits:

```text
There are so many water issues in Mysuru.
```

The system processes it as:

```text
Input
  ↓
Gemini
  ↓
Category = water
District = Mysore
Severity = extracted
Language = english
  ↓
MongoDB
  ↓
Demand Aggregation
  ↓
Water Infrastructure Data
  ↓
Water Coverage Gap
  ↓
Priority Score
  ↓
Hotspot
  ↓
Policy RAG
  ↓
Relevant Government Guidance
```

This demonstrates the complete CivicPulse workflow.

---

# 35. Transparency

CivicPulse does not ask an LLM to directly determine the final priority ranking.

The architecture is:

```text
LLM
 ↓
Structured Information
 ↓
Python Analytics
 ↓
Deterministic Calculations
 ↓
Priority Score
```

This provides a clear separation between:

### AI interpretation

and

### Measurable analytical computation

The RAG system provides contextual policy information but does not alter the deterministic priority score.

---

# 36. Data and Repository Policy

Large source datasets and generated artifacts are intentionally excluded from Git.

The following are ignored:

```text
.env
.venv/
data/raw/
data/processed/
data/rag/
__pycache__/
*.pyc
```

This keeps the GitHub repository lightweight and prevents accidental exposure of credentials or unnecessarily large files.

The repository retains the scripts required to understand and reproduce the data-processing pipeline.

---

# 37. Current Scope

The current MVP focuses on:

### Geography

```text
Karnataka
```

### Languages

```text
English
Hindi
Kannada
```

### Infrastructure Categories

```text
Roads
Water
Healthcare
```

### Input Modes

```text
Text
Voice
```

### Primary User

```text
Policymaker / Decision-Maker
```

Citizens provide the demand signals that feed the intelligence pipeline.

---

# 38. Current Limitations

The prototype intentionally has a focused MVP scope.

### Demographics

The demographic dataset is based on Census 2011.

### Citizen Requests

The current demonstration requests are synthetic.

### Healthcare Gap

Healthcare facility counts are available, but the MVP does not apply an unsupported facility-per-population benchmark.

### Geographic Resolution

The primary analytical aggregation is currently district-level.

### Policy Corpus

Policy intelligence is limited to the selected government documents included in the RAG corpus.

### Messaging Channels

WhatsApp and other messaging-channel integrations are outside the current MVP.

### Geographic Coverage

The initial MVP focuses on Karnataka rather than nationwide deployment.

---

# 39. Future Scope

CivicPulse can be extended to support:

- Additional Indian states
- Additional Indian languages
- Panchayat-level intelligence
- Taluk-level intelligence
- Village-level intelligence
- Additional infrastructure categories
- Live government datasets
- Additional public investment datasets
- Temporal hotspot analysis
- WhatsApp integration
- Other citizen communication channels
- Human-in-the-loop policy workflows
- Additional Digital Public Infrastructure integrations
- Continuous infrastructure monitoring
- Longitudinal citizen-demand analysis

---

# 40. Scalability

The current architecture is intentionally lightweight for an MVP.

The system can later separate major workloads into independent services:

```text
Citizen Interface
       ↓
Request Processing
       ↓
Data Platform
       ↓
Analytics
       ↓
Hotspot Engine
       ↓
Policy Retrieval
       ↓
Policy Generation
```

Potential independent services include:

- Citizen request processing
- Voice transcription
- Data ingestion
- Demand aggregation
- Hotspot computation
- RAG retrieval
- Policy generation

This allows individual components to scale independently as data volume and usage increase.

---

# 41. Security

Credentials are loaded from environment variables.

The following should never be committed:

```text
.env
Gemini API keys
Pinecone API keys
Database passwords
Private credentials
```

Use `.env.example` to document required configuration without exposing real secrets.

---

# 42. Project Status

Current MVP capabilities:

- [x] Multilingual citizen request processing
- [x] English support
- [x] Hindi support
- [x] Kannada support
- [x] Voice input
- [x] Gemini-based request extraction
- [x] District normalization
- [x] MongoDB persistence
- [x] Demographic data integration
- [x] Road infrastructure integration
- [x] Water infrastructure integration
- [x] Healthcare infrastructure integration
- [x] Demand aggregation
- [x] Infrastructure-gap analysis
- [x] Deterministic priority scoring
- [x] Priority hotspot dashboard
- [x] Government policy RAG
- [x] Pinecone vector search
- [x] Policy intelligence generation
- [x] Synthetic demonstration dataset

---

# 43. Why CivicPulse AI?

Citizen feedback contains valuable information about infrastructure problems, but individual requests are difficult to interpret at a system level.

CivicPulse connects:

```text
Citizen Voice
      +
Geography
      +
Demographics
      +
Infrastructure
      +
Government Policy
```

to create a unified infrastructure intelligence workflow.

The central idea is:

> **Citizen Voice → Infrastructure Intelligence → Development Priorities**

The current implementation demonstrates this concept through a focused Karnataka MVP.

---

# 44. Hackathon

### Track

**AI for Digital Public Infrastructure & Governance**

### Project

**CivicPulse AI**

### MVP Geography

**Karnataka**

### Core Use Case

Transforming citizen infrastructure demand into geographic hotspots, measurable infrastructure context, and policy-aligned development intelligence.

---

# 45. License

Add the project's chosen open-source license before public release.
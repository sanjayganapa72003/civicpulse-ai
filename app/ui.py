import os
import requests
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ============================================================
# CONFIG
# ============================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000",
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

STT_MODEL = "gemini-3.6-flash"

if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    gemini_client = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CivicPulse AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* -------------------------------------------------------
       GLOBAL
    ------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(37, 99, 235, 0.08),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(14, 165, 233, 0.07),
                transparent 25%
            ),
            #f7f9fc;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    /* -------------------------------------------------------
       HERO
    ------------------------------------------------------- */

    .hero {
        padding: 28px 32px;
        border-radius: 24px;
        background:
            linear-gradient(
                135deg,
                #0f172a 0%,
                #172554 55%,
                #1e3a8a 100%
            );
        color: white;
        margin-bottom: 28px;
        box-shadow:
            0 18px 45px rgba(15, 23, 42, 0.16);
    }

    .hero-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.16);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 38px;
        line-height: 1.1;
        font-weight: 750;
        margin: 0;
        letter-spacing: -0.025em;
    }

    .hero-subtitle {
        margin-top: 12px;
        max-width: 780px;
        color: #cbd5e1;
        font-size: 16px;
        line-height: 1.65;
    }

    /* -------------------------------------------------------
       SECTION HEADERS
    ------------------------------------------------------- */

    .section-title {
        font-size: 25px;
        font-weight: 720;
        color: #0f172a;
        margin-top: 12px;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 18px;
    }

    /* -------------------------------------------------------
       CITIZEN REPORT CARD
    ------------------------------------------------------- */

    .report-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 25px;
        box-shadow:
            0 8px 30px rgba(15, 23, 42, 0.06);
        margin-bottom: 30px;
    }

    .report-card-title {
        font-size: 22px;
        font-weight: 720;
        color: #0f172a;
        margin-bottom: 5px;
    }

    .report-card-description {
        color: #64748b;
        font-size: 14px;
        line-height: 1.55;
        margin-bottom: 18px;
    }

    .mode-label {
        font-size: 13px;
        font-weight: 650;
        color: #334155;
        margin-bottom: 6px;
    }

    /* -------------------------------------------------------
       METRICS
    ------------------------------------------------------- */

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 20px;
        min-height: 125px;
        box-shadow:
            0 6px 22px rgba(15, 23, 42, 0.05);
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #0f172a;
        font-size: 30px;
        font-weight: 750;
        line-height: 1;
    }

    .metric-description {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 9px;
    }

    /* -------------------------------------------------------
       HOTSPOT CARDS
    ------------------------------------------------------- */

    .hotspot-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow:
            0 5px 18px rgba(15, 23, 42, 0.05);
    }

    .hotspot-district {
        color: #0f172a;
        font-size: 19px;
        font-weight: 720;
    }

    .hotspot-category {
        color: #64748b;
        font-size: 13px;
        margin-top: 4px;
    }

    .hotspot-score {
        font-size: 25px;
        font-weight: 750;
        color: #1d4ed8;
        text-align: right;
    }

    .hotspot-score-label {
        font-size: 11px;
        color: #94a3b8;
        text-align: right;
    }

    /* -------------------------------------------------------
       EVIDENCE
    ------------------------------------------------------- */

    .evidence-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow:
            0 5px 18px rgba(15, 23, 42, 0.04);
    }

    .evidence-title {
        color: #0f172a;
        font-size: 16px;
        font-weight: 700;
    }

    .evidence-meta {
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
        margin-bottom: 10px;
    }

    .evidence-text {
        color: #475569;
        font-size: 14px;
        line-height: 1.6;
    }

    /* -------------------------------------------------------
       TAGS
    ------------------------------------------------------- */

    .tag {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        font-size: 11px;
        font-weight: 650;
        margin-right: 5px;
    }

    /* -------------------------------------------------------
       REQUEST RESULT
    ------------------------------------------------------- */

    .request-result {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 16px;
        margin-top: 14px;
    }

    .request-result-title {
        color: #166534;
        font-weight: 700;
        font-size: 14px;
    }

    .request-result-text {
        color: #365314;
        font-size: 13px;
        margin-top: 5px;
    }

    /* -------------------------------------------------------
       VOICE BOX
    ------------------------------------------------------- */

    .voice-box {
        background: #f8fafc;
        border: 1px dashed #cbd5e1;
        border-radius: 16px;
        padding: 15px;
        margin-top: 10px;
    }

    /* -------------------------------------------------------
       DIVIDER
    ------------------------------------------------------- */

    .soft-divider {
        height: 1px;
        background: #e2e8f0;
        margin: 30px 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def get_json(endpoint: str):
    """GET JSON from FastAPI."""
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        st.error(f"Unable to connect to backend: {exc}")
        return None


def submit_citizen_request(text: str):
    """Submit citizen text to existing FastAPI endpoint."""

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/citizen-requests",
            json={
                "text": text,
            },
            timeout=120,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        st.error(f"Unable to submit request: {exc}")
        return None


def speech_to_text(audio_bytes: bytes, mime_type: str) -> str:
    """
    Convert recorded audio into text using Gemini.
    """

    if gemini_client is None:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    response = gemini_client.models.generate_content(
        model=STT_MODEL,
        contents=[
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type,
            ),
            """
            Transcribe the citizen's speech exactly into text.

            The speaker may use:
            - English
            - Hindi
            - Kannada

            Preserve the original language.

            Do not translate.
            Do not summarize.
            Do not add information.

            Return only the transcription.
            """,
        ],
    )

    if not response.text:
        raise RuntimeError(
            "Speech transcription returned no text."
        )

    return response.text.strip()


def normalize_category(category: str) -> str:
    return category.replace("_", " ").title()


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">
            DIGITAL PUBLIC INFRASTRUCTURE • KARNATAKA
        </div>

        <div class="hero-title">
            Citizen Voice → Development Intelligence
        </div>

        <div class="hero-subtitle">
            Aggregate citizen needs, identify infrastructure
            hotspots, measure development gaps, and connect
            priority areas with relevant government programmes
            and policy evidence.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CITIZEN INPUT
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Report a Development Need
    </div>

    <div class="section-subtitle">
        Citizens can describe an infrastructure problem using
        text or their voice. The system will analyse the request
        and add it to the development intelligence layer.
    </div>
    """,
    unsafe_allow_html=True,
)


with st.container(border=True):

    st.markdown(
        """
        <div class="report-card-title">
            Tell us what is happening
        </div>

        <div class="report-card-description">
            Describe the problem in English, Hindi, or Kannada.
            Mention the location if you know it.
        </div>
        """,
        unsafe_allow_html=True,
    )

    input_method = st.radio(
        "Input method",
        [
            "Text",
            "Voice",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    citizen_text = ""

    # --------------------------------------------------------
    # TEXT INPUT
    # --------------------------------------------------------

    if input_method == "Text":

        citizen_text = st.text_area(
            "Development request",
            placeholder=(
                "Example: There is no proper drinking water "
                "supply in our village..."
            ),
            height=130,
            label_visibility="collapsed",
        )

    # --------------------------------------------------------
    # VOICE INPUT
    # --------------------------------------------------------

    else:

        st.markdown(
            """
            <div class="voice-box">
                🎙️ Record your request using the microphone
                below. English, Hindi and Kannada are supported.
            </div>
            """,
            unsafe_allow_html=True,
        )

        audio_value = st.audio_input(
            "Record your request",
        )

        if audio_value:

            st.audio(
                audio_value,
                format=audio_value.type,
            )

            with st.spinner(
                "Converting your speech to text..."
            ):

                try:

                    citizen_text = speech_to_text(
                        audio_value.getvalue(),
                        audio_value.type or "audio/wav",
                    )

                    st.markdown(
                        """
                        <div class="request-result">
                            <div class="request-result-title">
                                ✓ Speech transcribed
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.text_area(
                        "Transcription",
                        value=citizen_text,
                        height=110,
                        disabled=True,
                    )

                except Exception as exc:

                    st.error(
                        f"Speech transcription failed: {exc}"
                    )

    # --------------------------------------------------------
    # SUBMIT
    # --------------------------------------------------------

    if st.button(
        "Submit Development Request",
        type="primary",
        width="stretch",
    ):

        if not citizen_text.strip():

            st.warning(
                "Please enter a request or record a voice message."
            )

        else:

            with st.spinner(
                "Analysing your request..."
            ):

                result = submit_citizen_request(
                    citizen_text.strip()
                )

            if result:

                st.success(
                    "Development request submitted successfully."
                )

                st.markdown(
                    """
                    <div class="request-result">
                        <div class="request-result-title">
                            Request added to CivicPulse
                        </div>

                        <div class="request-result-text">
                            Your request has been analysed and
                            added to the citizen demand dataset.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Show extracted information if returned
                if isinstance(result, dict):

                    extracted = (
                        result.get("extracted")
                        or result.get("data")
                        or result
                    )

                    if isinstance(extracted, dict):

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            if extracted.get("language"):
                                st.metric(
                                    "Language",
                                    extracted["language"].title(),
                                )

                        with col2:
                            if extracted.get("category"):
                                st.metric(
                                    "Category",
                                    normalize_category(
                                        extracted["category"]
                                    ),
                                )

                        with col3:
                            if extracted.get("severity") is not None:
                                st.metric(
                                    "Severity",
                                    extracted["severity"],
                                )


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-title">
        Development Intelligence
    </div>

    <div class="section-subtitle">
        A consolidated view of citizen demand, infrastructure
        gaps, and priority development areas across Karnataka.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

demand_data = get_json(
    "/api/demand/districts"
)

hotspot_data = get_json(
    "/api/hotspots"
)

infrastructure_data = get_json(
    "/api/infrastructure/districts"
)


# ============================================================
# TOP METRICS
# ============================================================

if demand_data:

    total_requests = sum(
        district.get("total_requests", 0)
        for district in demand_data.values()
    )

    districts_with_demand = len(
        demand_data
    )

    categories = {
        "road": 0,
        "water": 0,
        "healthcare": 0,
    }

    severity_values = []

    for district in demand_data.values():

        for category in categories:
            categories[category] += district.get(
                category,
                0,
            )

        if district.get("average_severity") is not None:
            severity_values.append(
                district["average_severity"]
            )

    average_severity = (
        sum(severity_values) / len(severity_values)
        if severity_values
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    CITIZEN REQUESTS
                </div>
                <div class="metric-value">
                    {total_requests:,}
                </div>
                <div class="metric-description">
                    Requests currently analysed
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    DISTRICTS WITH DEMAND
                </div>
                <div class="metric-value">
                    {districts_with_demand}
                </div>
                <div class="metric-description">
                    Districts represented in requests
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    WATER REQUESTS
                </div>
                <div class="metric-value">
                    {categories["water"]:,}
                </div>
                <div class="metric-description">
                    Drinking-water related demand
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    AVG. SEVERITY
                </div>
                <div class="metric-value">
                    {average_severity:.2f}
                </div>
                <div class="metric-description">
                    Across analysed requests
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# HOTSPOTS
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Priority Development Hotspots
    </div>

    <div class="section-subtitle">
        Areas where citizen demand, severity and infrastructure
        gaps combine into a higher priority signal.
    </div>
    """,
    unsafe_allow_html=True,
)


if hotspot_data:

    hotspots = hotspot_data.get(
        "hotspots",
        [],
    )

    if hotspots:

        for index in range(
            0,
            len(hotspots),
            2,
        ):

            cols = st.columns(2)

            for column_index in range(2):

                hotspot_index = index + column_index

                if hotspot_index >= len(hotspots):
                    break

                hotspot = hotspots[
                    hotspot_index
                ]

                district = hotspot.get(
                    "district",
                    "Unknown",
                )

                category = normalize_category(
                    hotspot.get(
                        "category",
                        "unknown",
                    )
                )

                score = hotspot.get(
                    "priority_score",
                    0,
                )

                signals = hotspot.get(
                    "signals",
                    {},
                )

                with cols[column_index]:

                    st.markdown(
                        f"""
                        <div class="hotspot-card">

                            <div style="
                                display:flex;
                                justify-content:space-between;
                                align-items:flex-start;
                            ">

                                <div>
                                    <div class="hotspot-district">
                                        {district}
                                    </div>

                                    <div class="hotspot-category">
                                        {category} infrastructure
                                    </div>
                                </div>

                                <div>
                                    <div class="hotspot-score">
                                        {score:.2f}
                                    </div>

                                    <div class="hotspot-score-label">
                                        PRIORITY SCORE
                                    </div>
                                </div>

                            </div>

                            <div style="margin-top:15px;">
                                <span class="tag">
                                    {signals.get("demand_requests", 0)}
                                    requests
                                </span>

                                <span class="tag">
                                    severity
                                    {signals.get("average_severity", 0):.2f}
                                </span>

                                <span class="tag">
                                    gap
                                    {signals.get("infrastructure_gap_score", 0):.2f}
                                </span>
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# ============================================================
# DISTRICT INTELLIGENCE
# ============================================================

st.markdown(
    """
    <div class="section-title">
        District Intelligence
    </div>

    <div class="section-subtitle">
        Compare citizen demand with available infrastructure
        indicators.
    </div>
    """,
    unsafe_allow_html=True,
)


if demand_data:

    selected_district = st.selectbox(
        "Select district",
        sorted(demand_data.keys()),
    )

    district_demand = demand_data[
        selected_district
    ]

    district_infra = (
        infrastructure_data.get(
            selected_district,
            {},
        )
        if infrastructure_data
        else {}
    )

    infrastructure = district_infra.get(
        "infrastructure",
        {},
    )

    demographics = district_infra.get(
        "demographics"
    )

    # --------------------------------------------------------
    # DISTRICT SUMMARY
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Total Requests",
            district_demand.get(
                "total_requests",
                0,
            ),
        )

    with c2:
        st.metric(
            "Road",
            district_demand.get(
                "road",
                0,
            ),
        )

    with c3:
        st.metric(
            "Water",
            district_demand.get(
                "water",
                0,
            ),
        )

    with c4:
        st.metric(
            "Healthcare",
            district_demand.get(
                "healthcare",
                0,
            ),
        )

    # --------------------------------------------------------
    # INFRASTRUCTURE
    # --------------------------------------------------------

    st.markdown(
        "#### Infrastructure indicators"
    )

    infra_columns = st.columns(3)

    # Road
    with infra_columns[0]:

        road = infrastructure.get(
            "road"
        )

        if road:

            indicators = road.get(
                "indicators",
                {},
            )

            sanctioned = indicators.get(
                "road_length_sanctioned"
            )

            completed = indicators.get(
                "road_length_completed"
            )

            if sanctioned is not None and completed is not None:

                completion = (
                    completed / sanctioned
                    if sanctioned
                    else 0
                )

                st.metric(
                    "Road Completion",
                    f"{completion * 100:.1f}%",
                )

                st.caption(
                    f"{completed} / {sanctioned} "
                    "road length completed"
                )

            else:

                st.info(
                    "Road data unavailable"
                )

        else:

            st.info(
                "Road data unavailable"
            )

    # Water
    with infra_columns[1]:

        water = infrastructure.get(
            "water"
        )

        if water:

            indicators = water.get(
                "indicators",
                {},
            )

            coverage = indicators.get(
                "household_tap_coverage"
            )

            if coverage is not None:

                st.metric(
                    "Household Tap Coverage",
                    f"{coverage * 100:.1f}%",
                )

                st.caption(
                    f"Coverage gap: "
                    f"{(1 - coverage) * 100:.1f}%"
                )

            else:

                st.info(
                    "Water coverage unavailable"
                )

        else:

            st.info(
                "Water data unavailable"
            )

    # Healthcare
    with infra_columns[2]:

        healthcare = infrastructure.get(
            "healthcare"
        )

        if healthcare:

            indicators = healthcare.get(
                "indicators",
                {},
            )

            for key, label in [
                (
                    "chc_count",
                    "CHCs",
                ),
                (
                    "phc_count",
                    "PHCs",
                ),
                (
                    "general_hospital_count",
                    "General Hospitals",
                ),
            ]:

                if key in indicators:

                    st.metric(
                        label,
                        indicators[key],
                    )

        else:

            st.info(
                "Healthcare data unavailable"
            )

    # --------------------------------------------------------
    # DEMOGRAPHICS
    # --------------------------------------------------------

    if demographics:

        st.markdown(
            "#### Demographic context"
        )

        d1, d2, d3 = st.columns(3)

        with d1:
            st.metric(
                "Population",
                f"{demographics.get('population', 0):,}",
            )

        with d2:
            st.metric(
                "Rural Population",
                f"{demographics.get('rural_population', 0):,}",
            )

        with d3:
            st.metric(
                "Urban Population",
                f"{demographics.get('urban_population', 0):,}",
            )


# ============================================================
# POLICY / GOVERNMENT EVIDENCE
# ============================================================

st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-title">
        Government Policy & Evidence
    </div>

    <div class="section-subtitle">
        Connect development hotspots with relevant government
        programmes, guidelines, service standards and investment
        frameworks.
    </div>
    """,
    unsafe_allow_html=True,
)


policy_col1, policy_col2 = st.columns(
    [1, 2]
)


with policy_col1:

    policy_district = st.selectbox(
        "District",
        sorted(demand_data.keys())
        if demand_data
        else [],
        key="policy_district",
    )

    policy_categories = []

    if demand_data and policy_district:

        district_data = demand_data[
            policy_district
        ]

        for category in [
            "road",
            "water",
            "healthcare",
        ]:

            if district_data.get(
                category,
                0,
            ) > 0:

                policy_categories.append(
                    category
                )

    if policy_categories:

        policy_category = st.selectbox(
            "Development category",
            policy_categories,
            format_func=normalize_category,
        )

    else:

        policy_category = None

    get_policy = st.button(
        "Retrieve Government Evidence",
        type="primary",
        width="stretch",
    )


with policy_col2:

    if get_policy and policy_category:

        with st.spinner(
            "Retrieving relevant government evidence..."
        ):

            try:

                response = requests.get(
                    f"{API_BASE_URL}/api/hotspot-policy",
                    params={
                        "district": policy_district,
                        "category": policy_category,
                    },
                    timeout=120,
                )

                response.raise_for_status()

                policy_result = response.json()

            except requests.RequestException as exc:

                st.error(
                    f"Unable to retrieve policy evidence: {exc}"
                )

                policy_result = None

        if policy_result:

            policy = policy_result.get(
                "policy",
                {},
            )

            answer = policy.get(
                "answer"
            )

            if answer:

                st.markdown(
                    f"""
                    <div class="evidence-card">

                        <div class="evidence-title">
                            Policy relevance
                        </div>

                        <div class="evidence-text">
                            {answer}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            evidence = policy.get(
                "evidence",
                [],
            )

            if evidence:

                st.markdown(
                    "#### Supporting evidence"
                )

                for item in evidence:

                    document = item.get(
                        "document",
                        "Government document",
                    )

                    page = item.get(
                        "page"
                    )

                    claim = item.get(
                        "claim",
                        "",
                    )

                    page_text = (
                        f"Page {page}"
                        if page is not None
                        else ""
                    )

                    st.markdown(
                        f"""
                        <div class="evidence-card">

                            <div class="evidence-title">
                                {document}
                            </div>

                            <div class="evidence-meta">
                                {page_text}
                            </div>

                            <div class="evidence-text">
                                {claim}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            limitations = policy.get(
                "limitations",
                [],
            )

            if limitations:

                with st.expander(
                    "Evidence limitations"
                ):

                    for limitation in limitations:

                        st.write(
                            f"• {limitation}"
                        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="
        text-align:center;
        color:#94a3b8;
        font-size:12px;
        padding:10px;
    ">
        CivicPulse AI • Citizen demand intelligence for
        development planning
    </div>
    """,
    unsafe_allow_html=True,
)
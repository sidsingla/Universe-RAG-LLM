import sys
from pathlib import Path

# Project root so `qa_with_rag` resolves when running: streamlit run ui_frontend/app.py
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from qa_with_rag import answer_question

# Fixed retrieval depth for RAG (no UI control).
RAG_TOP_K = 5

UNIVERSE_CSS = """
<style>
/* Deep space base */
.stApp {
    background: linear-gradient(165deg, #020208 0%, #0a0620 30%, #120a32 55%, #060814 100%) !important;
}
/* Fixed cosmos layer (stars + planets) — behind app content */
#cosmos-backdrop {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}
/* Dense distant stars (tiled) */
.cosmos-stars-far {
    position: absolute;
    inset: -10%;
    background-image:
        radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.45), transparent),
        radial-gradient(1px 1px at 30% 65%, rgba(255,255,255,0.35), transparent),
        radial-gradient(1px 1px at 55% 12%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 78% 44%, rgba(200,220,255,0.35), transparent),
        radial-gradient(1px 1px at 92% 88%, rgba(255,255,255,0.3), transparent);
    background-size: 280px 280px;
    background-repeat: repeat;
    opacity: 0.65;
    animation: cosmos-twinkle 8s ease-in-out infinite;
}
/* Brighter scattered stars (larger, fewer) */
.cosmos-stars-near {
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(2px 2px at 8% 15%, rgba(255,255,255,0.95), transparent),
        radial-gradient(1.5px 1.5px at 22% 42%, rgba(186, 230, 253, 0.85), transparent),
        radial-gradient(2px 2px at 38% 78%, rgba(255,255,255,0.75), transparent),
        radial-gradient(1px 1px at 48% 8%, rgba(255,255,255,0.6), transparent),
        radial-gradient(2.5px 2.5px at 62% 55%, rgba(224, 231, 255, 0.9), transparent),
        radial-gradient(1px 1px at 72% 22%, rgba(255,255,255,0.55), transparent),
        radial-gradient(2px 2px at 88% 68%, rgba(196, 181, 253, 0.8), transparent),
        radial-gradient(1.5px 1.5px at 95% 35%, rgba(255,255,255,0.7), transparent),
        radial-gradient(1px 1px at 15% 92%, rgba(165, 243, 252, 0.65), transparent),
        radial-gradient(2px 2px at 52% 95%, rgba(255,255,255,0.5), transparent);
    background-size: 100% 100%;
    opacity: 0.85;
    animation: cosmos-twinkle 12s ease-in-out infinite reverse;
}
@keyframes cosmos-twinkle {
    0%, 100% { opacity: 0.75; }
    50% { opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
    .cosmos-stars-far, .cosmos-stars-near { animation: none; }
}
/* Nebula patches */
.cosmos-nebula-a {
    position: absolute;
    bottom: -15%;
    left: -15%;
    width: 65%;
    height: 55%;
    background: radial-gradient(ellipse at 40% 60%, rgba(88, 28, 135, 0.35) 0%, transparent 60%);
    filter: blur(2px);
}
.cosmos-nebula-b {
    position: absolute;
    top: -10%;
    right: -5%;
    width: 50%;
    height: 45%;
    background: radial-gradient(ellipse at 70% 30%, rgba(30, 58, 138, 0.28) 0%, transparent 55%);
    filter: blur(3px);
}
.cosmos-nebula-c {
    position: absolute;
    top: 35%;
    left: 5%;
    width: 35%;
    height: 30%;
    background: radial-gradient(ellipse at center, rgba(6, 182, 212, 0.12) 0%, transparent 70%);
}
/* Planet: gas giant + rings (top right) */
.planet-gas {
    position: absolute;
    width: 140px;
    height: 140px;
    right: 4%;
    top: 12%;
    border-radius: 50%;
    background:
        radial-gradient(circle at 32% 28%, #fde68a 0%, #d97706 35%, #92400e 72%, #451a03 100%);
    box-shadow:
        0 0 50px rgba(251, 191, 36, 0.25),
        inset -18px -12px 35px rgba(0,0,0,0.45);
}
.planet-gas::before {
    content: "";
    position: absolute;
    left: 50%;
    top: 50%;
    width: 220px;
    height: 48px;
    margin-left: -110px;
    margin-top: -24px;
    border-radius: 50%;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: linear-gradient(180deg, rgba(255,255,255,0.06), transparent);
    transform: rotate(-12deg);
    box-shadow: 0 0 20px rgba(251, 191, 36, 0.08);
}
/* Planet: ice / blue (bottom left) */
.planet-ice {
    position: absolute;
    width: 72px;
    height: 72px;
    left: 6%;
    bottom: 18%;
    border-radius: 50%;
    background:
        radial-gradient(circle at 35% 30%, #e0f2fe 0%, #38bdf8 40%, #0369a1 85%, #0c4a6e 100%);
    box-shadow:
        0 0 35px rgba(56, 189, 248, 0.35),
        inset -8px -6px 18px rgba(0,0,0,0.35);
}
.planet-ice::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: linear-gradient(125deg, transparent 40%, rgba(255,255,255,0.15) 48%, transparent 55%);
}
/* Planet: small red rock (upper left) */
.planet-rock {
    position: absolute;
    width: 28px;
    height: 28px;
    left: 18%;
    top: 22%;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #fca5a5, #b91c1c 70%, #450a0a);
    box-shadow: 0 0 12px rgba(248, 113, 113, 0.4);
}
/* Tiny moon near gas giant */
.planet-moon {
    position: absolute;
    width: 12px;
    height: 12px;
    right: 11%;
    top: 26%;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #e2e8f0, #64748b);
    box-shadow: 0 0 6px rgba(255,255,255,0.2);
}
.block-container {
    position: relative;
    z-index: 2;
    padding-top: 2rem !important;
    max-width: 720px !important;
}
.universe-header {
    text-align: center;
    padding: 0.5rem 0 1.25rem 0;
}
.universe-title {
    font-family: "Segoe UI", system-ui, sans-serif;
    font-weight: 700;
    font-size: 2rem;
    background: linear-gradient(90deg, #a5b4fc 0%, #c4b5fd 40%, #7dd3fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 40px rgba(165, 180, 252, 0.35);
    letter-spacing: 0.04em;
}
.universe-sub {
    color: #94a3b8 !important;
    font-size: 0.95rem;
    margin-top: 0.35rem;
}
.solar-system-hero {
    display: block;
    margin: 0 auto 0.75rem auto;
    max-width: 320px;
    width: 100%;
    height: auto;
    filter: drop-shadow(0 4px 24px rgba(99, 102, 241, 0.35));
}

/* Streamlit widgets on dark — white typed text */
.stTextArea textarea {
    background-color: rgba(15, 23, 42, 0.85) !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid rgba(99, 102, 241, 0.45) !important;
    border-radius: 10px !important;
}
.stTextArea textarea::placeholder {
    color: rgba(255, 255, 255, 0.5) !important;
    opacity: 1 !important;
}
.stTextArea textarea::-webkit-input-placeholder {
    color: rgba(255, 255, 255, 0.5) !important;
}
.stTextArea textarea::-moz-placeholder {
    color: rgba(255, 255, 255, 0.5) !important;
}
label, .stRadio label {
    color: #cbd5e1 !important;
}
[data-baseweb="radio"] {
    color: #e2e8f0 !important;
}
.stMarkdown, .stMarkdown p, .stMarkdown strong {
    color: #e2e8f0 !important;
}
hr {
    border-color: rgba(99, 102, 241, 0.2) !important;
}
</style>
"""

st.set_page_config(page_title="Universe RAG", page_icon="🌌", layout="centered")

st.markdown(UNIVERSE_CSS, unsafe_allow_html=True)

st.markdown(
    """
<div id="cosmos-backdrop" aria-hidden="true">
  <div class="cosmos-nebula-a"></div>
  <div class="cosmos-nebula-b"></div>
  <div class="cosmos-nebula-c"></div>
  <div class="cosmos-stars-far"></div>
  <div class="cosmos-stars-near"></div>
  <div class="planet-gas"></div>
  <div class="planet-moon"></div>
  <div class="planet-ice"></div>
  <div class="planet-rock"></div>
</div>
""",
    unsafe_allow_html=True,
)

SOLAR_SYSTEM_SVG = """
<svg class="solar-system-hero" viewBox="0 0 400 180" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Stylized solar system">
  <defs>
    <radialGradient id="sunGrad" cx="40%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="45%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#b45309"/>
    </radialGradient>
    <filter id="sunGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- Orbits -->
  <ellipse cx="200" cy="90" rx="155" ry="52" fill="none" stroke="rgba(148,163,184,0.25)" stroke-width="1"/>
  <ellipse cx="200" cy="90" rx="120" ry="40" fill="none" stroke="rgba(148,163,184,0.2)" stroke-width="1"/>
  <ellipse cx="200" cy="90" rx="85" ry="28" fill="none" stroke="rgba(148,163,184,0.18)" stroke-width="1"/>
  <ellipse cx="200" cy="90" rx="52" ry="17" fill="none" stroke="rgba(148,163,184,0.15)" stroke-width="1"/>
  <!-- Sun -->
  <circle cx="200" cy="90" r="22" fill="url(#sunGrad)" filter="url(#sunGlow)"/>
  <!-- Planets (schematic positions on orbits) -->
  <circle cx="252" cy="90" r="4" fill="#94a3b8"/>
  <circle cx="268" cy="78" r="5" fill="#60a5fa"/>
  <circle cx="285" cy="95" r="5.5" fill="#34d399"/>
  <circle cx="300" cy="72" r="4" fill="#f87171"/>
  <circle cx="318" cy="88" r="9" fill="#d97706"/>
  <circle cx="340" cy="82" r="8" fill="#eab308"/>
  <ellipse cx="340" cy="82" rx="14" ry="3" fill="none" stroke="rgba(254,243,199,0.35)" stroke-width="1" transform="rotate(-15 340 82)"/>
  <circle cx="72" cy="95" r="3.5" fill="#cbd5e1"/>
  <circle cx="95" cy="88" r="3" fill="#fcd34d"/>
</svg>
"""

st.markdown(
    f"""
<div class="universe-header">
  {SOLAR_SYSTEM_SVG}
  <div class="universe-title">Universe Q&A</div>
  <p class="universe-sub">RAG information from docs — or ask the model alone, among the stars.</p>
</div>
""",
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []

mode = st.radio(
    "Mode",
    ["RAG (retrieve + answer)", "Direct LLM (no retrieval)"],
    horizontal=True,
    help="RAG uses Pinecone + your indexed documents. Direct uses Gemini only.",
)
use_rag = mode.startswith("RAG")

question = st.text_area(
    "Your question",
    placeholder="e.g. What does the document say about …?",
    height=110,
)

btn = st.button("Launch answer", type="primary", use_container_width=True)

if btn:
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        spinner_text = (
            "Retrieving from the index and generating…"
            if use_rag
            else "Generating answer (no retrieval)…"
        )
        with st.spinner(spinner_text):
            try:
                ans = answer_question(
                    question.strip(),
                    top_k=RAG_TOP_K,
                    use_rag=use_rag,
                )
                st.session_state.history.insert(
                    0,
                    {
                        "question": question.strip(),
                        "answer": ans,
                        "mode": "RAG" if use_rag else "Direct",
                    },
                )
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state.history:
    st.markdown("### Recent transmissions")
    for item in st.session_state.history:
        st.markdown(
            f'<p><strong>Q. </strong> {item["question"]}</p>'
            f'<p><strong>A. </strong> {item["answer"]}</p>'
            f'<p style="font-size:0.8rem;color:#94a3b8;">Mode: {item.get("mode", "—")}</p>'
            "<hr/>",
            unsafe_allow_html=True,
        )

from pathlib import Path
import base64
import streamlit as st

st.set_page_config(page_title="ERror Normalizer", layout="centered", initial_sidebar_state="collapsed", page_icon="⚙️")

CUSTOM_CSS = """
<style>
/* App background gradient */
.stApp {
    background: radial-gradient(circle at 0% 0%, #4c1d95 0%, #020617 48%, #000000 100%) !important;
}

/* Hero section */
.dv-hero {
    text-align: center;
    margin-bottom: 1.5rem;
    min-height: 32vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.dv-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.18rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    background: rgba(148, 163, 184, 0.18);
    color: #e5e7eb;
    border: 1px solid rgba(148, 163, 184, 0.35);
    margin-bottom: 0.5rem;
}
.dv-hero-title {
    font-size: 1.5rem;
    font-weight: 600;
    letter-spacing: -0.03em;
}
.dv-hero-name {
    font-size: 3.5rem;
    font-weight: 650;
    margin-top: 0.4rem;
    margin-bottom: 0.2rem;
    text-align: center;
    color: #a855f7;
}
.dv-hero-subtitle {
    font-size: 0.95rem;
    color: #9ca3af;
    max-width: 460px;
    margin: 0.4rem auto 0;
}

/* Button */
div[data-testid="stButton"] {
    display: flex !important;
    width: 100% !important;
    text-align: center !important;
}
div[data-testid="stButton"] > button {
    width: 500px !important;  
    border-radius: 999px !important;
    padding-top: 0.8rem !important;
    padding-bottom: 0.8rem !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    color: #ffffff !important;
    background: linear-gradient(90deg, #6366f1, #a855f7) !important; 
    border: none !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.35);
    transition: all 0.2s ease-in-out;
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(90deg, #7c7ff7, #c084fc) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 22px rgba(99,102,241,0.55);
    transform: translateY(-1px);
}

/* Brands track */
.dv-brands {
    margin-top: 1rem;
    text-align: center;
}
.dv-brands-title {
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.8rem;
}
/* Marquee container */
.dv-brands-marquee {
    position: relative;
    overflow: hidden;
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
}
/* Moving track */
.dv-brands-track {
    display: flex;
    width: max-content;
    will-change: transform;
    animation: dv-brands-scroll 26s linear infinite;
}
.dv-brands-sequence {
    display: flex;
    align-items: center;
    gap: 2.5rem;
    margin-right: 2.5rem;
}
.dv-brand-logo {
    height: 40px;
    display: flex;
    align-items: center;
    opacity: 1;
    filter: none;
    transition: transform 0.25s ease, filter 0.25s ease;
    overflow: hidden;
}
.dv-brand-logo img {
    height: 32px !important;
    width: auto !important;
    display: block;
}
.dv-brand-logo:hover {
    filter: brightness(1.12);
    transform: translateY(-2px);
}
@keyframes dv-brands-scroll {
    0% {
        transform: translateX(0);
    }
    100% {
        transform: translateX(-50%);
    }
}
</style>
"""

def svg_data_url(path: str) -> str:
    """Load an SVG file and return a data:image/svg+xml;base64 URI."""
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"

python_svg = svg_data_url("logos/python.svg")
streamlit_svg = svg_data_url("logos/streamlit.svg")
llava_svg = svg_data_url("logos/llava.svg")
jaided_svg = svg_data_url("logos/jaided.svg")
github_svg = svg_data_url("logos/github.svg")
ollama_svg = svg_data_url("logos/ollama.svg")

# Apply CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Hero
st.markdown(
    """
    <div class="dv-hero">
        <div class="dv-pill">FSociety • CSCE 411</div>
        <div class="dv-hero-name">ERror Normalizer</div>
        <div class="dv-hero-title">Validate your diagrams with AI</div>
        <div class="dv-hero-subtitle">
            Upload an ERD or architecture sketch and get instant feedback on names, relationships, and structure.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div style='text-align:center; margin-top:-1rem; margin-bottom:1rem;'>",
    unsafe_allow_html=True,
)

cols = st.columns([1, 1])

with cols[0]:
    st.markdown(
        """
        <div style="text-align:center;">
            <h4>⠀⠀How it works</h4>
            <div class="dv-hero-subtitle">1. Upload an ER diagram image.<br>
            2. Entities &amp; relationships are read using OCR and/or a local vision model.<br>
            3. A text LLM scores quality and flags issues for you.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with cols[1]:
    st.markdown(
        """
        <div style="text-align:center;">
            <h4>⠀⠀What it can catch</h4>
            <div class="dv-hero-subtitle">• Naming inconsistencies<br>
            • Missing or unclear relationships<br>
            • Ambiguous cardinalities<br>
            • Other structural issues</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(" ")
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")

col1, col2, col3 = st.columns([1,3,1])

if col2.button("Try it", key="nav_button"):
    st.switch_page("pages/upload.py")

st.markdown(
    "<div style='text-align:center; font-size:0.75rem; color:#9ca3af; margin-top:0.5rem;'>"
    "Developed by Daniel Crow, Thomas Nguyen, Timi Ogunleye, and Shawn Ludena"
    "</div>",
    unsafe_allow_html=True,
)

# Brand logos section (moved above upload anchor)
brands_html = f"""
<div class="dv-brands">
    <div class="dv-brands-title">Built using the following tools</div>
    <div class="dv-brands-marquee">
        <div class="dv-brands-track">
            <div class="dv-brands-sequence">
                <div class="dv-brand-logo"><img src="{python_svg}" alt="Python" /></div>
                <div class="dv-brand-logo"><img src="{streamlit_svg}" alt="Streamlit" /></div>
                <div class="dv-brand-logo"><img src="{llava_svg}" alt="LLaVA" /></div>
                <div class="dv-brand-logo"><img src="{jaided_svg}" alt="Jaided" /></div>
                <div class="dv-brand-logo"><img src="{github_svg}" alt="GitHub" /></div>
                <div class="dv-brand-logo"><img src="{ollama_svg}" alt="Python" /></div>
            </div>
            <div class="dv-brands-sequence">
                <div class="dv-brand-logo"><img src="{python_svg}" alt="Python" /></div>
                <div class="dv-brand-logo"><img src="{streamlit_svg}" alt="Streamlit" /></div>
                <div class="dv-brand-logo"><img src="{llava_svg}" alt="LLaVA" /></div>
                <div class="dv-brand-logo"><img src="{jaided_svg}" alt="Jaided" /></div>
                <div class="dv-brand-logo"><img src="{github_svg}" alt="GitHub" /></div>
                <div class="dv-brand-logo"><img src="{ollama_svg}" alt="Python" /></div>
            </div>
        </div>
    </div>
</div>
"""

st.markdown(brands_html, unsafe_allow_html=True)

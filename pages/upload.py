import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Upload Diagram", layout="centered", initial_sidebar_state="collapsed", page_icon="📥")

CUSTOM_CSS = """
<style>
.stApp {
    background: radial-gradient(circle at 0% 0%, #4c1d95 0%, #020617 48%, #000000 100%) !important;
}

/* Upload section */
.dv-upload-title {
    text-align: left;
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}
.dv-upload-subtitle {
    font-size: 0.9rem;
    color: #9ca3af;
    margin-bottom: 1.2rem;
}
.dv-section-title {
    font-weight: 600;
    font-size: 1.2rem;
    margin-bottom: 0.35rem;
}
[data-testid="stFileUploaderDropzone"] {
    background: rgba(15,23,42,0.9) !important;
    border: 1px dashed rgba(148,163,184,0.4) !important;
    border-radius: 14px !important;
    padding: 1.2rem !important;
}

/* Internal upload button */
[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(90deg, #6366f1, #a855f7) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.45rem 0.8rem !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: linear-gradient(90deg, #7c7ff7, #c084fc) !important;
    color: #ffffff !important;
    filter: brightness(1.15) !important;
}

/* Button */
div[data-testid="stButton"] {
    display: flex !important;
    width: 100% !important;
    text-align: center !important;
}
div[data-testid="stButton"] > button {
    /* Dimensions */
    width: 500px !important; 
    
    /* Visuals */
    border-radius: 999px !important;
    padding-top: 0.8rem !important;
    padding-bottom: 0.8rem !important;
    
    /* Font & Color */
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

/* Expander Styling */
.streamlit-expanderHeader {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 0.95rem !important;
}
[data-testid="stExpanderDetails"] {
    background-color: rgba(15, 23, 42, 0.4) !important;
    border-bottom-left-radius: 8px !important;
    border-bottom-right-radius: 8px !important;
    color: #cbd5e1 !important;
}
</style>
"""

# Apply CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Page heading
st.markdown("<div class='dv-upload-title'>Upload a diagram</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='dv-upload-subtitle'>Drop in an ERD (Entity Relationship Diagram) or architecture sketch to validate names, relationships, and structure.</div>",
    unsafe_allow_html=True,
)

st.markdown("<div class='dv-section-title'>Diagram image</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Diagram image (PNG/JPEG)",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed",
    key="diagram_uploader_page",
)

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='dv-section-title'>Analysis method</div>", unsafe_allow_html=True)

analysis_method = st.radio(
    "Choose a pipeline:",
    [
        "OCR + text LLM (baseline)",
        "LLaVA image-based (Ollama)",
        "LLaVA extraction (entities & relationships)",
    ],
    horizontal=False, # Changed to False so it sits nicely above the expanders
    label_visibility="collapsed"
)

# --- EXPANDER EXPLANATIONS ---
st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

with st.expander("🔍  Why use OCR + Text LLM?"):
    st.markdown("""
    **Best for: Messy handwriting or text-heavy diagrams.**
    
    This method first runs a dedicated Optical Character Recognition (OCR) engine to read every word, then sends *only* the text to the AI.
    * **Pros:** Extremely accurate at reading variable names and labels.
    * **Cons:** Loses visual context (doesn't know which box points to which).
    """)

with st.expander("👁️  Why use LLaVA Image-Based?"):
    st.markdown("""
    **Best for: Logic checks and structural design.**
    
    This sends the actual image to the Vision model. It "looks" at the diagram like a human would.
    * **Pros:** Understands relationships (cardinality), flow, and nesting.
    * **Cons:** Can sometimes hallucinate small text or misread blurry words.
    """)

with st.expander("📝  Why use LLaVA Extraction?"):
    st.markdown("""
    **Best for: Reverse engineering and documentation.**
    
    Similar to the Image-based method, but the AI is strictly prompted to output a raw inventory (JSON-style list) of every entity and connection found.
    * **Pros:** Great for generating a list of requirements or database schemas.
    * **Cons:** Provides less "critique" or advice; focuses purely on data extraction.
    """)
# -----------------------------

image = None
if uploaded_file:
    st.markdown("---")
    # Save raw bytes so the Results page can reconstruct the image
    file_bytes = uploaded_file.getvalue()
    st.session_state["dv_image_bytes"] = file_bytes
    st.session_state["dv_image_name"] = uploaded_file.name

    image = Image.open(BytesIO(file_bytes))
    st.image(image, width="stretch")

st.markdown(" ")
col1, col2, col3 = st.columns([1,5,1])
run_button = col2.button("Validate diagram", key="validate_button_page")

# When the button is clicked, store the chosen method and navigate to the results page.
if run_button:
    if image is None:
        st.error("Please upload an image before validating.")
    else:
        # Persist the chosen analysis method and clear any previous results
        st.session_state["dv_analysis_method"] = analysis_method
        st.session_state.pop("dv_results", None)

        st.switch_page("pages/results.py")
import streamlit as st
from typing import Dict, Any
from io import BytesIO
from PIL import Image
import base64
import requests
import easyocr
import numpy as np
import re
import time

st.set_page_config(page_title="Diagram Results", layout="centered", initial_sidebar_state="collapsed", page_icon="📊")

CUSTOM_CSS = """
<style>
/* Remove white header bar and sidebar */
[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
}

.stApp {
    background: radial-gradient(circle at 0% 0%, #4c1d95 0%, #020617 48%, #000000 100%) !important;
}

[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

.main .block-container {
    background: transparent !important;
    max-width: 1600px !important;
    padding-top: 2.5rem !important;
    padding-bottom: 3rem !important;
}

.dv-title {
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
    font-size: 0.95rem;
    margin-bottom: 0.35rem;
}

.dv-results {
    margin-top: 1.25rem;
}

.dv-issue-card {
    border-radius: 12px;
    padding: 1rem; /* Slightly more padding */
    border: 1px solid rgba(148, 163, 184, 0.2);
    margin-bottom: 0.75rem;
    background: rgba(15, 23, 42, 0.6); /* Slightly more transparent */
    
    /* SCROLLING LOGIC */
    max-height: 300px;       /* Stop card from getting too tall */
    overflow-y: auto;        /* Add scrollbar if needed */
}

/* Custom Scrollbar for Webkit (Chrome/Safari) */
.dv-issue-card::-webkit-scrollbar {
    width: 6px;
}
.dv-issue-card::-webkit-scrollbar-track {
    background: transparent; 
}
.dv-issue-card::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
}
.dv-issue-card::-webkit-scrollbar-thumb:hover {
    background-color: rgba(255, 255, 255, 0.4);
}

.dv-section-text {
    font-size: 0.88rem;
    color: #9ca3af;
}

/* Button */
div[data-testid="stButton"] {
    display: flex !important;
    width: 100% !important;
    text-align: center !important;
}
div[data-testid="stButton"] > button {
    width: 700px !important; 
    
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

/* Upload animation container and bouncing arrow */
.dv-upload-animation-container {
    margin-top: 0rem;
    text-align: center;
}
.dv-arrow-bounce {
    display: inline-block;
    font-size: 4rem;
    color: #a855f7;
    animation: dv-arrow-move 1.3s infinite ease-in-out;
}
@keyframes dv-arrow-move {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(20px); }
}
</style>
"""


def parse_score_from_text(text: str) -> int:
    """
    Robustly extracts a 0-100 score from model text.
    It prioritizes explicit 'Score: NN' patterns but falls back to 'NN/100'.
    """
    if not text:
        return None

    m1 = re.search(r"Score\s*[:\-]?\s*(\d{1,3})", text, flags=re.IGNORECASE)
    
    m2 = re.search(r"(\d{1,3})\s*/\s*100", text)

    val = None
    
    # Prefer Strategy 1 if it exists and looks reasonable
    if m1:
        val = int(m1.group(1))
    
    # If Strategy 1 failed or gave a weird number (like 0 or >100), try Strategy 2
    if (val is None or val < 0 or val > 100) and m2:
        val = int(m2.group(1))

    # Final sanity check
    if val is not None:
        return max(0, min(val, 100))
        
    return None

def format_text_to_html(text: str) -> str:
    """
    Converts Markdown (bold, lists, sub-headers) to HTML.
    """
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

    text = re.sub(r'(?m)^###+\s*(.*)$', r'<div style="margin-top: 4px; font-weight: 700;">\1</div>', text)
    
    lines = text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith(('* ', '- ', '• ', '+ ')):
            content = stripped[1:].strip() 
            if not in_list:
                html_lines.append("<ul style='margin-bottom: 0; padding-left: 1.2rem;'>")
                in_list = True
            html_lines.append(f"<li>{content}</li>")
        
        elif stripped.startswith("<div"):
             if in_list:
                html_lines.append("</ul>")
                in_list = False
             html_lines.append(stripped)
             
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            
            if stripped:
                html_lines.append(f"{line}<br>")

    if in_list:
        html_lines.append("</ul>")
        
    return "\n".join(html_lines)


def _encode_image_to_base64(image: Image.Image) -> str:
    """Encode a PIL image as base64 PNG for sending to Ollama."""
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# --- 1. LLaVA IMAGE ANALYSIS (Vision Mode) ---
def analyze_diagram_with_llava(image: Image.Image) -> Dict[str, Any]:
    """
    Directly analyzes the image using LLaVA (Vision). 
    Focuses on a balanced analysis of structure and logic.
    """
    ollama_url = "http://localhost:11434/api/chat"
    img_b64 = _encode_image_to_base64(image)

    # Prompt focused on General Analysis
    prompt = (
        "You are an expert Senior Database Engineer.\n"
        "Analyze this ER diagram image.\n"
        "Ignore watermark text or software UI noise.\n\n"
        "For scoring, do not be afraid to give a good score. Sometimes no issues will be found. If there are issues give an appropriate score to reflect those.\n\n"
        "OUTPUT FORMAT (Strictly use these Markdown headers):\n\n"
        "## 1. Overview\n"
        "(1-2 sentences on what the diagram represents)\n\n"
        "## 2. Entities & Attributes\n"
        "(List detected entities and attributes. Use dashes '-' for lists.)\n\n"
        "## 3. Relationships\n"
        "(List connections between entities. Use dashes '-' for lists.)\n\n"
        "## 4. Issues\n"
        "(List logical database design issues, e.g., missing keys, bad cardinality. Do NOT mention OCR noise. It is not necessary to find issues if there are none.)\n\n"
        "## 5. Suggestions\n"
        "(Concrete fixes for the issues)\n\n"
        "## 6. Score\n"
        "Score: NN/100\n"
        "(Brief justification)\n"
    )

    payload = {
        "model": "llava",
        "stream": False,
        "messages": [{
            "role": "user",
            "content": prompt,
            "images": [img_b64],
        }],
        "options": {"temperature": 0.1}
    }

    try:
        resp = requests.post(ollama_url, json=payload, timeout=120)
        resp.raise_for_status()
        text = resp.json().get("message", {}).get("content", "").strip()
        score = parse_score_from_text(text)
    except Exception as e:
        text = f"Error calling LLaVA: {e}"
        score = None

    return {"summary": text, "raw_output": text, "score": score}


# --- 2. LLaVA EXTRACTION (Detailed Mode) ---
def extract_with_llava(image: Image.Image) -> Dict[str, Any]:
    """
    Also uses LLaVA (Vision), but the prompt is tuned slightly more 
    towards rigorous extraction of details before analysis.
    """
    ollama_url = "http://localhost:11434/api/chat"
    img_b64 = _encode_image_to_base64(image)

    # Prompt tuned for HIGH DETAIL EXTRACTION
    prompt = (
        "You are a Database Architect specializing in Reverse Engineering.\n"
        "Extract every detail from this ER diagram image into a formal report.\n"
        "Be extremely precise with attribute names and relationship types.\n\n"
        "For scoring, do not be afraid to give a good score. Sometimes no issues will be found. If there are issues give an appropriate score to reflect those.\n\n"
        "OUTPUT FORMAT (Strictly use these Markdown headers):\n\n"
        "## 1. Overview\n"
        "(Brief summary of the domain)\n\n"
        "## 2. Entities & Attributes\n"
        "(List EVERY entity and ALL its attributes found in the image. Be exhaustive.)\n\n"
        "## 3. Relationships\n"
        "(List every line connecting boxes, including cardinality labels like '1', 'N', 'M' if visible.)\n\n"
        "## 4. Issues\n"
        "(Critique the design: are Primary Keys marked? Are relationships named? Issues are not necessary to be found if there are none.)\n\n"
        "## 5. Suggestions\n"
        "(How to make this diagram professional)\n\n"
        "## 6. Score\n"
        "Score: NN/100\n"
        "(Brief justification)\n"
    )

    payload = {
        "model": "llava",
        "stream": False,
        "messages": [{
            "role": "user",
            "content": prompt,
            "images": [img_b64],
        }],
        "options": {"temperature": 0.1}
    }

    try:
        resp = requests.post(ollama_url, json=payload, timeout=120)
        resp.raise_for_status()
        text = resp.json().get("message", {}).get("content", "").strip()
        score = parse_score_from_text(text)
    except Exception as e:
        text = f"Error calling LLaVA: {e}"
        score = None

    return {"summary": text, "raw_output": text, "score": score, "entities": [], "relationships": []}

# --- 3. OCR AND TEXT LLM (Baseline Mode) ---
def run_ocr(image: Image.Image) -> Dict[str, Any]:
    """Run OCR on the uploaded image using EasyOCR."""
    np_img = np.array(image.convert("RGB"))
    
    _easyocr_reader = easyocr.Reader(["en"], gpu=True, verbose=False)
    results = _easyocr_reader.readtext(np_img, detail=0)

    extracted_text = "\n".join(results)

    return {
        "extracted_text": extracted_text,
        "entities": [], 
        "relationships": [],
    }

def analyze_ocr_with_llava(ocr_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze OCR-derived ER diagram text using LLaVA as a text-only LLM."""
    ollama_url = "http://localhost:11434/api/chat"
    model_name = "llava"

    extracted_text = ocr_payload.get("extracted_text", "")
    
    # HARDENED PROMPT
    prompt = (
        "You are an expert Senior Database Engineer acting as a Data Cleaner.\n"
        "You have been given raw, dirty OCR text from an Entity Relationship Diagram (ERD).\n"
        "The OCR text contains significant 'hallucinations' (gibberish words, random characters, misread labels).\n\n"
        "For scoring, do not be afraid to give a good score. Sometimes no issues will be found. If there are issues give an appropriate score to reflect those.\n\n"
        f"RAW OCR DATA:\n{extracted_text}\n\n"
        "### STRICT INSTRUCTIONS:\n"
        "1. **AGGRESSIVE FILTERING**: Before analyzing, mentally delete any text that does not look like a valid English word, a standard database abbreviation (e.g., PK, FK, ID), or a plausible variable name.\n"
        "   - Example: 'Checynll', 'Haptd', 'Hadidid', 'Habitnmm' -> IGNORE THESE COMPLETELY.\n"
        "   - Example: 'User', 'Student', 'enroll_date' -> KEEP THESE.\n"
        "2. **DO NOT REPORT NOISE**: Do NOT list OCR artifacts in the 'Issues' section. If you see 'Haptd', pretend you never saw it. Do not suggest removing it; just exclude it from your output entirely.\n"
        "3. **INFER CONTEXT**: If you see 'Studnt', correct it to 'Student'. If you see 'Primry Key', treat it as 'Primary Key'.\n"
        "4. **OUTPUT FORMAT**: Use Markdown headers (##) and bullet points (-).\n\n"
        "### OUTPUT SECTIONS:\n\n"
        "## 1. Overview\n"
        "(1-2 sentences on what the Valid parts of the diagram represent)\n\n"
        "## 2. Entities & Attributes\n"
        "(List ONLY the valid, real entities you detected. Correct spelling errors if obvious.)\n"
        "- **EntityName**: Attribute1, Attribute2, ...\n\n"
        "## 3. Relationships\n"
        "(List valid relationships between the real entities)\n"
        "- EntityA connects to EntityB (Type if known)\n\n"
        "## 4. Issues\n"
        "(List ONLY logical database issues like missing keys or bad cardinality. DO NOT mention OCR typos or gibberish words here. Do not need to find issues if there are none.)\n\n"
        "## 5. Suggestions\n"
        "(Standard database improvements)\n\n"
        "## 6. Score\n"
        "Score: NN/100\n"
        "(Brief justification)\n"
    )

    payload = {
        "model": model_name,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "options": {
            "temperature": 0.1,
            "num_ctx": 2048
        }
    }

    try:
        resp = requests.post(ollama_url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("message", {}).get("content", "").strip()
        score = parse_score_from_text(text)
    except Exception as e:
        text = f"Error calling LLaVA: {e}"
        score = None

    return {
        "summary": text,
        "issues": [],
        "suggested_fixes": [],
        "raw_output": text,
        "score": score,
    }

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown("<div class='dv-title'>Diagram Analysis Results</div>", unsafe_allow_html=True)
status_container = st.empty()

# Ensure we have inputs from the upload page
if "dv_image_bytes" not in st.session_state or "dv_analysis_method" not in st.session_state:
    st.markdown(
        """
        <div style='text-align:center; margin-top: 3rem;'>
            <img src="https://cdn4.iconfinder.com/data/icons/computer-emoticons/512/Sad-Emoji-Emotion-Face-Expression-Feeling_1-512.png" 
                 width="240" style="opacity:0.8; margin-bottom: 1rem;" />
            <h3 style="font-weight:600;">No diagram analysis available</h3>
            <p style="color:#9ca3af; font-size:1.1rem;">
                Upload an ER diagram to get started.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,5,1])
    if col2.button("Go to upload", key="go_to_upload"):
        st.switch_page("pages/upload.py")

    st.markdown(
        """
        <div class='dv-upload-animation-container'>
            <span class='dv-arrow-bounce'>↑</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()

image_bytes = st.session_state["dv_image_bytes"]
image_name = st.session_state.get("dv_image_name", "Uploaded diagram")
analysis_method = st.session_state["dv_analysis_method"]

image = Image.open(BytesIO(image_bytes))

current_image_hash = hash(image_bytes)

results = st.session_state.get("dv_results")

need_to_run = (
    results is None 
    or results.get("analysis_method") != analysis_method
    or results.get("image_hash") != current_image_hash
)

if need_to_run:
    if "dv_results" in st.session_state:
        del st.session_state["dv_results"]

    start_time = time.time()
    # Use st.status for a multi-step progress log
    with st.status("Starting analysis pipeline...", expanded=True) as status:

        results_payload: Dict[str, Any] = {
            "analysis_method": analysis_method,
            "image_hash": current_image_hash,
        }

        # Show the image temporarily while processing so the screen isn't empty
        with st.spinner("Processing image...", show_time=True):
            st.write("✅ Image processed")
        image_container = st.empty()
        image_container.image(image, width="stretch")

        if analysis_method == "OCR + text LLM (baseline)":
            with st.spinner("Scanning text with EasyOCR...", show_time=True):
                ocrresults = run_ocr(image)
            st.write("✅ Text scanned")
            
            with st.spinner("Analyzing logical structure...", show_time=True):
                llmresults = analyze_ocr_with_llava(ocrresults)
            st.write("✅ Logic analyzed")

            results_payload["mode"] = "ocr_llm"
            results_payload["ocrresults"] = ocrresults
            results_payload["llmresults"] = llmresults

        elif analysis_method == "LLaVA image-based (Ollama)":
            with st.spinner("Sending image to Vision model...", show_time=True):
                llavaresults = analyze_diagram_with_llava(image)
            st.write("✅ Vision analysis complete")

            results_payload["mode"] = "llava_image"
            results_payload["llavaresults"] = llavaresults

        else: 
            with st.spinner("Extracting entities and relationships...", show_time=True):
                extractresults = extract_with_llava(image)
            st.write("✅ Extraction complete")

            results_payload["mode"] = "llava_extract"
            results_payload["extractresults"] = extractresults

        end_time = time.time()
        duration = end_time - start_time

        st.write("✅ We ran your chosen analysis pipeline on the uploaded diagram. Review the findings below!")
        status.update(
            label=f"Analysis complete! ({duration:.2f}s)", 
            state="complete", 
            expanded=False
        )

    # Save to session state
    st.session_state["dv_results"] = results_payload
    results = results_payload
    
    st.warning("Results are not 100% accurate due to model hallucination. Manual review is recommended.")
    
    image_container.empty()

st.set_page_config(layout="wide")

# Layout: left = preview, right = detailed results
left_col, right_col = st.columns([1, 1])


with left_col:
    st.markdown("<div class='dv-section-title'>Diagram preview</div>", unsafe_allow_html=True)
    st.image(image, width="stretch")
    st.markdown(f"**File:** {image_name}")
    st.markdown(f"**Analysis method:** {analysis_method}")

    mode = results.get("mode")
    result_block = {}
    
    # Identify which results to use
    if mode == "ocr_llm":
        result_block = results.get("llmresults", {})
    elif mode == "llava_image":
        result_block = results.get("llavaresults", {})
    elif mode == "llava_extract":
        result_block = results.get("extractresults", {})

    score = result_block.get("score")
    summary_text = result_block.get("summary", "")

    # Display Score
    if score is not None:
        st.markdown("### Quality Score")
        st.progress(score / 100)
        st.markdown(f"**{score}/100**")

        if score >= 80:
            status_text = "EXCELLENT CONDITION"
            color_hex = "#4ade80"
        elif score >= 50:
            status_text = "NEEDS IMPROVEMENT"
            color_hex = "#facc15"
        else:
            status_text = "CRITICAL ISSUES"
            color_hex = "#f87171"

        st.markdown(
            f"""
            <div style="margin-bottom: 20px;">
                <div class="shimmer-text" style="
                    font-size: 2rem; 
                    font-weight: 800; 
                    letter-spacing: 2px; 
                    margin-bottom: 5px;
                    text-transform: uppercase;
                ">
                    {status_text}
                </div>
            </div>

            <style>
            .shimmer-text {{
                background: linear-gradient(to right, {color_hex} 20%, #ffffff 50%, {color_hex} 80%);
                background-size: 200% auto;
                color: {color_hex};
                background-clip: text;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: shine 3s linear infinite;
            }}
            
            @keyframes shine {{
                to {{
                    background-position: 200% center;
                }}
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

        # Extract Reasoning (Look for the ## Score section)
        if summary_text:
            # Split by Markdown headers (## Title)
            parts = re.split(r"(?m)^##\s+(.+)$", summary_text)
            reasoning_body = ""
            
            if len(parts) > 1:
                for i in range(1, len(parts), 2):
                    title = parts[i].strip().lower()
                    if "score" in title:
                        raw_body = parts[i+1].strip()
                        clean_lines = [line for line in raw_body.splitlines() if "Score:" not in line]
                        reasoning_body = "\n".join(clean_lines).strip()
                        break
            
            if reasoning_body:
                st.markdown("**Score reasoning**")
                reasoning_html = format_text_to_html(reasoning_body)
                st.markdown(
                    f"<div class='dv-section-text'>{reasoning_html}</div>",
                    unsafe_allow_html=True,
                )

    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    if st.button("Try another diagram", key="try_another_button"):
        st.switch_page("pages/upload.py")

with right_col:
    mode = results.get("mode")
    summary_text = ""
    ocr_debug_text = None

    if mode == "ocr_llm":
        st.markdown("<div class='dv-section-title'>Analysis: OCR + Text LLM</div>", unsafe_allow_html=True)
        summary_text = results.get("llmresults", {}).get("summary", "")
        ocr_debug_text = results.get("ocrresults", {}).get("extracted_text", "")
        
    elif mode == "llava_image":
        st.markdown("<div class='dv-section-title'>Analysis: LLaVA (Vision)</div>", unsafe_allow_html=True)
        summary_text = results.get("llavaresults", {}).get("summary", "")
        
    elif mode == "llava_extract":
        st.markdown("<div class='dv-section-title'>Analysis: LLaVA (Extraction Focused)</div>", unsafe_allow_html=True)
        summary_text = results.get("extractresults", {}).get("summary", "")

    if summary_text:
        parts = re.split(r"(?m)^##\s+(.+)$", summary_text)

        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                title = parts[i].strip()
                body = parts[i + 1].strip() if i + 1 < len(parts) else ""

                if "score" in title.lower():
                    continue

                card_style = "border: 1px solid rgba(148, 163, 184, 0.2);" # Default Slate
                icon = "📄"
                
                t_lower = title.lower()
                
                if "issue" in t_lower or "error" in t_lower or "problem" in t_lower:
                    # Red styling for Issues
                    card_style = "border: 1px solid rgba(239, 68, 68, 0.5); background: rgba(239, 68, 68, 0.1);" 
                    icon = "⚠️"
                elif "suggestion" in t_lower or "fix" in t_lower or "recommend" in t_lower:
                    # Green styling for Suggestions
                    card_style = "border: 1px solid rgba(34, 197, 94, 0.5); background: rgba(34, 197, 94, 0.1);" 
                    icon = "💡"
                elif "entity" in t_lower or "attribute" in t_lower or "relationship" in t_lower:
                    # Blue styling for Structural Data (Entities/Relationships)
                    card_style = "border: 1px solid rgba(59, 130, 246, 0.5); background: rgba(59, 130, 246, 0.1);"
                    icon = "🧬"

                formatted_body = format_text_to_html(body)

                st.markdown(
                    f"""
                    <div class='dv-issue-card' style='{card_style}'>
                        <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                            <span style='font-size: 1.2rem; margin-right: 8px;'>{icon}</span>
                            <strong>{title}</strong>
                        </div>
                        <div style='font-size: 0.9rem; color: #cbd5e1;'>
                            {formatted_body}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("Analysis generated, but section headers were missing.")
            st.info(summary_text)
    else:
        st.error("No analysis text returned.")

    if ocr_debug_text:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='dv-section-title'>Extracted Text Content</div>", unsafe_allow_html=True)
        
        with st.expander("Show raw text detected by OCR"):
            st.code(ocr_debug_text, language="text")
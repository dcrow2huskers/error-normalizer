# 🍌 Error Normalizer

**Error Normalizer** is an interactive, local-first tool for validating database diagrams. Using OCR and vision-based AI (LLaVA), it grades Entity Relationship Diagrams (ERDs) and identifies structural mistakes, naming issues, and logic problems.

Upload a diagram, and the system behaves like a **Senior Database Engineer** providing detailed feedback.

---

## ✨ Features

- **Multi-Mode Analysis**
  - **OCR + Text LLM:** Ideal for reading variable names, labels, and handwritten text.
  - **Vision (LLaVA):** Understands structural layout, flow, and cardinality.
  - **Extraction Mode:** Generates a strict JSON-style inventory of entities and relationships.
- **Visual Grading**
  - Produces a 0–100 “Health Score.”
  - Uses shields and sirens for visual clarity.
- **Detailed Feedback**
  - Color-coded cards for **Issues** (red), **Suggestions** (green), and **Structural Data** (blue).
- **100% Local**
  - All AI processing runs on your machine using **Ollama**.  
  - No uploads. No cloud. No privacy concerns.

---

## 🛠️ Prerequisites

Before running the application, install and run **Ollama**, which provides the vision model used by the system.

1. **Download Ollama:**  
   https://ollama.com/download

2. **Pull the Vision Model:**
   ```bash
   ollama pull llava
   ```

3. **Keep Ollama Running:**  
   Make sure the Ollama app is open in the background while using Error Normalizer.

---

## 📦 Installation

### 1. Clone or Download the Project

Place the project folder where you want it on your machine.

### 2. Set Up a Virtual Environment

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> Note: On first run, EasyOCR may download model files automatically.

---

## 🚀 Running the App

Start the Streamlit app with:

```bash
streamlit run Home.py
```

(If your entry file has a different name, update the command accordingly.)

---

## 📂 Project Structure

```
error-normalizer/
├── Home.py              # Main entry page
├── requirements.txt
├── README.md
└── pages/
    ├── upload.py        # File upload & method selection
    └── results.py       # OCR/AI analysis results
```

---

## 🏠 Example Home.py

```python
import streamlit as st

st.set_page_config(
    page_title="Error Normalizer",
    page_icon="🍌",
    layout="centered"
)

st.title("🍌 Error Normalizer")

st.markdown("""
### Welcome to your AI Diagram Validator

This tool analyzes Entity Relationship Diagrams (ERDs) using:
- **Ollama (LLaVA)** for visual reasoning  
- **EasyOCR** for text extraction  
- **LLM analysis** for grading structure, naming, and logic

#### How to Use:
1. Ensure **Ollama** is running in the background.
2. Navigate to the **Upload** page.
3. Drop in your diagram.
4. Review the AI-generated critique.
""")

if st.button("Start Validating"):
    st.switch_page("pages/upload.py")
```

---

## 🐛 Troubleshooting

### 🔌 "Connection Refused" or AI Not Working
- Ensure Ollama is running (`http://localhost:11434` should respond).
- Ensure you pulled the model:
  ```bash
  ollama pull llava
  ```

### 📄 "Missing File" in Streamlit
- This is a Streamlit race condition with `st.file_uploader`.
- Refreshing the page typically resolves it.

### ⚙️ EasyOCR Errors (Windows)
- Install **Visual Studio Build Tools**  
  → Choose **Desktop Development with C++** workload.

---
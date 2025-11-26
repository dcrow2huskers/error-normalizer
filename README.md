# ⚙️ ERror Normalizer

**ERror Normalizer** is an interactive, local-first tool for validating database diagrams. Using OCR and vision-based AI (LLaVA), it grades and scores Entity Relationship Diagrams (ERDs) and identifies structural mistakes, naming issues, and logic problems.

Upload a diagram, and the system behaves like a **Senior Database Engineer** providing detailed feedback.

<img width="3024" height="1674" alt="CleanShot 2025-11-26 at 10 39 35@2x" src="https://github.com/user-attachments/assets/596bff5c-4327-41c9-bf86-df717fea3c1c" />

---

## ✨ Features

- **Multi-Mode Analysis**
  - **OCR + Text LLM:** Ideal for reading variable names, labels, and handwritten text.
  - **Vision (LLaVA):** Understands structural layout, flow, and cardinality.
  - **Extraction Mode:** Generates a strict JSON-style inventory of entities and relationships.
- **Visual Grading**
  - Produces a 0–100 “Diagram Consistency Score.”
  - Provides a text rating of *excellent condition*, *needs improvement*, or *critical issues*.
- **Detailed Feedback**
  - Color-coded cards for **Issues** (red), **Suggestions** (green), and **Structural Data** (blue).
- **100% Local**
  - All AI processing runs on your machine using **Ollama**.  
  - No data collection, cloud, or privacy concerns.

---

## 🛠️ Prerequisites

Before running the application, install and run **Ollama**, which provides the vision model used by the system.

1. **Download Ollama:**  
   https://ollama.com/download
  (macOS users may also install via Homebrew:)
  ```bash
  brew install ollama
  ```
  On MacOS, the Ollama app may launch, but you do not need to use the window. You may close it as the service runs in the background.

3. **Pull the Vision Model:**
  After installing Ollama, in terminal or powershell
   ```bash
   ollama pull llava
   ```

3. **Run LlaVA:**
   ```bash
   ollama run llava
   ```
   Make sure the terminal is open in the background and ollama is running the LLaVA model while using ERror Normalizer.

---

## 📦 Installation

### 1. Clone or Download the Project

Clone or download and unzip the project folder where you want it on your machine. 

### 2. Navigate Into the Project Directory

Before creating your virtual environment, make sure you are inside the project folder:
```bash
cd error-normalizer
```
(You can also open this project in VSCode and skip the virtual environment by using the built-in terminal).

### 3. Set Up a Virtual Environment

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

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

> Note: On first run, EasyOCR may download model files automatically.

---

## 🚀 Running the App

Start the Streamlit app with:

```bash
streamlit run app.py
```

---

## 📂 Project Structure

```
error-normalizer/
├── app.py              # Main home page
├── requirements.txt
├── README.md
├── logos/              # Where brand svgs are stored
├── .streamlit/         # Site config file
└── pages/
    ├── upload.py        # File upload & method selection
    └── results.py       # OCR/AI analysis results
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


---

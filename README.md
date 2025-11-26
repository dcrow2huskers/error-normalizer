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
This project was developed and tested with Python version 3.9.6. Other Python 3.9.x versions should work.
Use newer versions at your own discretion.

1. **Download Ollama:**  
   https://ollama.com/download

   (macOS users may also install via Homebrew:)
   ```bash
   brew install ollama
   ```
> Note: On MacOS, the Ollama app may launch, but you do not need to use the window. You may close it as the service runs in the background.

3. **Pull the Vision Model:**
  After installing Ollama, in terminal or powershell
   ```bash
   ollama pull llava
   ```

4. **Run LlaVA:**
   ```bash
   ollama run llava
   ```
   Make sure the terminal is open in the background and ollama is running the LLaVA model while using ERror Normalizer.

   Don't forget to stop the model after you are done using the app.
   ```bash
   ollama stop llava
   ```

> Note: The app may run LLaVA on your device automatically after initial Ollama setup.


---

## 📦 Installation

### 1. Clone or Download the Project

Clone or download and unzip the project folder where you want it on your machine. 

### 2. Navigate Into the Project Directory

Before creating your virtual environment, make sure you are inside the project folder:
```bash
cd error-normalizer
```
> Note: You can also open this project in VSCode and skip the virtual environment by using the built-in terminal. Using a virtual environment is recommended but optional.

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

> Note: On first run, EasyOCR may download model and engine files automatically.

---

## 🚀 Running the App

Make sure you have carefully completed the prerequisite and installation steps above.

Start the Streamlit app with:

```bash
streamlit run app.py
```

---
---

## 🧪 How to Use ERror Normalizer

Once the Streamlit app is running in your browser, follow these steps:

### 1. Go to the Upload Page
Your browser should automatically open the streamlit app to the home page. 
The home page provides a little information about the app and its usage.
Click the 'Try it' button to navigate to the upload page.

### 2. Upload Your ERD
Supported image formats (200 MB limit):
- PNG  
- JPG / JPEG  

**Recommended input:**  
A clean, high-resolution screenshot or export of your diagram (Lucidchart, Draw.io, Canva, etc.). Sample ERD images online also work. The OCR method works best with very clear text in the image.

### 3. Choose an Analysis Method
You can select from three modes:

- **OCR Pipeline**  
  Extracts text first, then lets the LLM analyze the labels, names, and entity/attribute quality. 

- **Vision (LLaVA)**  
  Looks at the entire diagram as an image. Best for cardinality, relationships, and structural flow.

- **Extraction Mode**  
  Produces a JSON-like inventory of detected entities, attributes, and relationships that is sent to the LLM for analysis.

Explanations for each mode are also available on the site. You can try all three and compare the results.

### 4. View Output & Scoring
The results page displays:

- #### **Diagram Score (0–100)**
  A weighted evaluation of naming consistency, structural correctness, attribute usage, and schema clarity.

- #### **Text Rating**
  - **Excellent Condition**  
  - **Needs Improvement**  
  - **Critical Issues**

- #### **Issue Cards**
  The analysis will provide a variety of cards with different information about the ERD. The first card is a general overview of the diagram and the subsequent cards are color-coded for their appropriate information.
  Red = structural errors  
  Green = suggestions / optimization  
  Blue = extracted metadata (entities, attributes, relationships)

The raw OCR text is also available in the OCR analysis method if you want to see what the engine was able to extract.

### 5. Run Again
The results page provides a button for you to go back to the upload page and re-run with a different analysis mode or different ERD without restarting the app.

### 6. Troubleshooting
The app is designed to have excellent error handling and user experience. Most potential errors are small and can be fixed with a page refresh as it re-runs the script. If there are any critical errors, please reach out to the team.

---

## ✔️ Expected Input Examples

Examples of diagrams that work well:

- Draw.io / Diagrams.net ERDs  
- Lucidchart database schemas  
- Canva ERD templates  
- UML-style diagrams  
- Hand-drawn ERDs (OCR pipeline recommended)
- PNG, JPG, or JPEG format

<img width="3022" height="2686" alt="CleanShot 2025-11-26 at 11 40 11@2x" src="https://github.com/user-attachments/assets/acfb1270-6f03-486e-8b62-c777f71cba2b" />

**Try to include:**
- Entity boxes with clear names  
- Attributes (optional but helpful)  
- Relationship lines  
- Cardinalities (1:1, 1:N, M:N, crow’s foot)  

---

## 📤 Expected Output Examples

Error Normalizer will produce:

- **A numerical diagram quality score**  
- **Extracted entities + attributes**  
- **Detected relationships + cardinality guesses**  
- **Naming issues** (pluralization, inconsistent casing, unclear wording)  
- **Schema structure problems** (missing identifiers, improper M:N linking, etc.)  
- **LLM-interpreted suggestions or summary of improvements**
- **Raw OCR TEXT** (for OCR analysis method)

<img width="3020" height="2654" alt="CleanShot 2025-11-26 at 11 44 15@2x" src="https://github.com/user-attachments/assets/f5d4713c-ff4b-4ae6-9807-5d434863d8f1" />

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

## Acknowledgements

Built with open-source technologies: EasyOCR, Streamlit, and Ollama’s LLaVA vision-language model.

---

# AI Meeting Action-Item Extractor

A Streamlit application that extracts candidate action items from meeting transcripts. Output fields include task, owner, deadline, status, confidence, extraction source, and a human-review flag.

## Features
- Paste transcript text or upload TXT/DOCX
- Rule-based NLP mode works without an API key
- Optional LLM extraction using Groq (your API key required)
- Structured, editable results table
- Review flags for missing owners/deadlines, low confidence, invalid/past dates
- Duplicate removal and CSV/JSON export
- Sample transcript and capstone report

## Run locally (Windows)
Install Python 3.10+, open this folder in VS Code, then run:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Open the local URL printed in the terminal, usually http://localhost:8501.

## Optional LLM mode
Create a Groq API key in your own account. Locally, create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your-key-here"
```
Do not commit this file. On Streamlit Community Cloud, add `GROQ_API_KEY` in the app's Settings → Secrets. The default rule-based mode does not need this key. LLM output must still be reviewed.

## Deploy
1. Upload the project files to a GitHub repository (do not upload `.venv`, `.env`, or secrets).
2. Sign in to Streamlit Community Cloud using GitHub.
3. Create an app and select your repository, branch, and `app.py`.
4. Deploy, then test the app with `data/sample_transcript.txt`.

## Limitations
Rule-based extraction relies on explicit action wording and may miss indirect assignments or context across sentences. Confidence is an estimate, not a calibrated probability. Use anonymized/approved transcripts and verify outputs. Sample transcripts are demonstration data, not evidence of real-world accuracy.

# AI Meeting Action-Item Extractor
## Capstone Project Report

**Domain:** Artificial Intelligence / Natural Language Processing  
**Language:** Python | **Interface:** Streamlit

## Abstract
This project converts meeting transcripts into structured candidate action items containing task, owner, deadline, status, confidence estimate, extraction source, and a review flag. Users can paste text or upload TXT/DOCX files, inspect and edit extracted results, and export them to CSV or JSON. A transparent rule-based NLP method is available by default, with optional LLM extraction through Groq. Human verification remains necessary.

## 1. Introduction
Meetings generate verbal commitments that can be difficult to track. Identifying tasks, owners, and due dates manually may be time-consuming. Natural language processing can help convert unstructured meeting text into organized follow-up records.

## 2. Problem Statement
Meeting transcripts are unstructured and may contain action items in conversational language. Manual tracking can lead to missed tasks, unclear ownership, and inconsistent deadlines. This project identifies explicit commitments and flags incomplete records for review.

## 3. Objectives
- Accept meeting transcripts as pasted text or TXT/DOCX uploads.
- Identify explicit commitments and follow-up actions.
- Extract task, owner, deadline, status, and confidence.
- Validate missing or invalid information and remove duplicates.
- Provide an editable interface and CSV/JSON exports.
- Support human review of uncertain predictions.

## 4. Proposed System
The Streamlit interface accepts a transcript. The application reads and segments transcript lines, applies rule-based NLP or optional LLM extraction, normalizes the result to a shared schema, validates fields, and presents an editable output table.

### Workflow
1. Input transcript.
2. Read text and detect speaker labels.
3. Extract explicit action statements.
4. Structure task, owner, deadline, status, confidence, and source.
5. Flag missing owners, missing/invalid/past deadlines, and low confidence.
6. Review and export results.

## 5. Technology Stack
| Technology | Purpose |
|---|---|
| Python | Core logic |
| Streamlit | Web interface |
| Pandas | Tabular data and exports |
| Regular expressions | Rule-based text and date extraction |
| Groq API (optional) | LLM-based extraction |
| python-docx | DOCX reading |
| Git/GitHub | Version control |
| Streamlit Community Cloud | Deployment |

## 6. Methodology
### Rule-based NLP
The default method identifies explicit commitment terms such as “will,” “need to,” “should,” “must,” and “follow up.” Speaker labels can provide a candidate owner. Date expressions are normalized where supported. A heuristic confidence estimate and review flag are assigned. This method is lightweight and works without an external API, but can miss implied tasks and complex context.

### Optional LLM
When a Groq API key is configured, a language model is prompted to return structured JSON and avoid inventing missing information. The response is normalized and validated. LLM output can contain errors and is not treated as authoritative.

### Output Schema
- **Task:** action description
- **Owner:** responsible person or Unassigned
- **Deadline:** ISO date or Not specified
- **Status:** Open by default
- **Confidence:** estimated score from 0 to 1
- **Source:** extraction method
- **Review:** Yes/No indicator for manual attention

## 7. System Requirements
Python 3.10+, a modern browser, package-installation internet access, and GitHub/Streamlit accounts for deployment. LLM mode additionally requires a Groq API key.

## 8. Testing Plan
Test clear commitments, missing owners, missing dates, no-action transcripts, repeated tasks, supported date formats, TXT/DOCX uploads, and CSV/JSON downloads. For formal evaluation, manually annotate a test set and calculate task/owner/deadline precision, recall, and F1. Demonstration examples alone do not establish real-world accuracy.

## 9. Expected Outcome
The application produces structured candidate action items, highlights incomplete or uncertain records, and supports manual correction and export. It is intended to assist meeting follow-up.

## 10. Limitations
Rule-based extraction depends on explicit language and speaker labels. Relative dates are resolved against the date the app runs. Confidence is not calibrated. LLM results depend on model and API availability. Transcript privacy, permission, and external processing should be considered.

## 11. Future Enhancements
Audio transcription, stronger speaker attribution, cross-sentence context resolution, annotated evaluation datasets, persistent storage, authentication, and approved integrations with task-management platforms.

## 12. Conclusion
The project demonstrates a practical NLP workflow for transforming unstructured meeting transcripts into structured follow-up information. Extraction, validation, review flags, and export are combined in a simple web application. Human verification is essential before using results as official records.

## References
1. Python Documentation: https://docs.python.org/3/
2. Streamlit Documentation: https://docs.streamlit.io/
3. Pandas Documentation: https://pandas.pydata.org/docs/
4. Groq API Documentation: https://console.groq.com/docs

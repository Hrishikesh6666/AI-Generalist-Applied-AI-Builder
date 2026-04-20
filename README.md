# AI-Generalist-Applied-AI-Builder
# DDR Report Generator 🏗️

An AI-powered system that reads raw building inspection documents 
and generates a structured, client-ready Detailed Diagnostic Report (DDR).

## What It Does

Upload two PDFs (Inspection Report + Thermal Report) and the system:
- Extracts text and images from both documents
- Uses GPT-4o-mini to analyze and merge findings
- Generates a professional 7-section DDR Word document
- Includes actual thermal temperature readings per area
- Flags missing or conflicting information automatically

## DDR Output Sections

1. Property Issue Summary
2. Area-wise Observations (with images)
3. Probable Root Cause
4. Severity Assessment (HIGH / MEDIUM / LOW)
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information

## Tech Stack

- Python 3.13
- Streamlit (UI)
- OpenAI GPT-4o-mini (AI analysis)
- PyMuPDF / fitz (PDF extraction)
- python-docx (Word document generation)

## How to Run

1. Install dependencies:

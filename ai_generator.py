from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Fix your environment.")

client = OpenAI(api_key=api_key)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_ddr(inspection_text, thermal_text, report_name="Property"):
    
    insp_summary = _summarize(
        inspection_text[:6000],
        "site inspection report",
        "Extract ALL of these: impacted areas, types of damage (dampness/cracks/seepage), "
        "positive side findings (tile gaps, hollowness, plumbing issues), "
        "bathroom/balcony/terrace/wall issues, recommended treatments. Use bullet points."
    )

    # ── Key fix: explicit instruction to extract temperature numbers ──
    thermal_summary = _summarize(
        thermal_text[:5000],
        "thermal imaging report",
        "Extract ALL temperature readings. For each thermal image, list: "
        "location/area, hotspot temperature, coldspot temperature, date. "
        "Example format: 'Hall skirting - Hotspot 28.8°C, Coldspot 23.4°C (27/09/22)'. "
        "Also note which areas show moisture (blue/cyan in thermal = cold = moisture)."
    )

    prompt = f"""
You are a professional building diagnostics expert at UrbanRoof Pvt Ltd.
Generate a complete, client-ready DDR (Detailed Diagnostic Report) based on:

INSPECTION FINDINGS:
{insp_summary}

THERMAL IMAGING FINDINGS:
{thermal_summary}

Write a professional DDR with EXACTLY these 7 sections:

1. PROPERTY ISSUE SUMMARY
   Brief overview of all major problems.

2. AREA-WISE OBSERVATIONS
   For EACH area found in the documents:
   - Visual damage observed
   - Thermal camera confirmation with actual temperature readings if available
   - Note: [IMAGE PLACEHOLDER: AreaName] once per area

3. PROBABLE ROOT CAUSE
   Simple explanation of what is causing each type of damage.

4. SEVERITY ASSESSMENT
   Rate each area: HIGH / MEDIUM / LOW with one-line reasoning.

5. RECOMMENDED ACTIONS
   Specific repair steps per area in simple language.

6. ADDITIONAL NOTES
   Warnings, precautions, or important observations.

7. MISSING OR UNCLEAR INFORMATION
   List anything Not Available or conflicting between documents.
   Flag if inspection and thermal reports appear to be from different properties/dates.

STRICT RULES:
- Only use facts from documents above
- Write "Not Available" only if truly not in either document
- If dates or properties conflict between documents, say so explicitly
- Use simple, client-friendly language
- Include actual temperature numbers where provided
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2500,
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are a professional building inspector. Be accurate, include all temperature data, never invent facts."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def _summarize(text, doc_type, instruction):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=800,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Extract inspection data precisely. Include all numbers, temperatures, and measurements found in the document."},
            {"role": "user", "content": f"From this {doc_type}, {instruction}\n\nDOCUMENT:\n{text}"}
        ]
    )
    return response.choices[0].message.content
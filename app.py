import streamlit as st
import os
import re
from extractor import extract_from_pdf, get_key_sections
from ai_generator import generate_ddr
from report_builder import create_ddr_word_doc

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="DDR Report Generator",
    page_icon="🏗️",
    layout="centered"
)

st.title("🏗️ DDR Report Generator")
st.caption("AI-powered Detailed Diagnostic Report from inspection documents")
st.markdown("---")

# ── Sidebar: API Key input ─────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("OpenAI API Key", type="password", 
                             help="Your key stays local and is never stored")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.success("API Key set ✓")
    
    property_name = st.text_input("Property Name / Address", 
                                   value="Flat No-8/63, Yamuna CHS, Mulund")

# ── File uploaders ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    inspection_file = st.file_uploader(
        "📋 Inspection Report", type="pdf",
        help="The visual inspection report PDF"
    )
with col2:
    thermal_file = st.file_uploader(
        "🌡️ Thermal Report", type="pdf",
        help="The IR thermography report PDF"
    )
with col3:
    extra_file = st.file_uploader(
        "📎 Additional Doc (optional)", type="pdf",
        help="Any extra document (sample report, etc.)"
    )

# ── Show file status ───────────────────────────────────────────
status_cols = st.columns(3)
with status_cols[0]:
    if inspection_file:
        st.success(f"✓ {inspection_file.name}")
with status_cols[1]:
    if thermal_file:
        st.success(f"✓ {thermal_file.name}")
with status_cols[2]:
    if extra_file:
        st.info(f"+ {extra_file.name}")

st.markdown("---")

# ── Generate button ────────────────────────────────────────────
if st.button("⚡ Generate DDR Report", use_container_width=True, type="primary"):
    
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("Please enter your OpenAI API key in the sidebar first.")
        st.stop()
    
    if not inspection_file or not thermal_file:
        st.warning("Please upload at least the Inspection Report and Thermal Report.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    try:
        # Step 1: Extract
        status.info("📄 Step 1/4: Extracting text and images from documents...")
        progress.progress(10)
        
        insp_text, insp_images = extract_from_pdf(inspection_file, "Inspection Report")
        therm_text, therm_images = extract_from_pdf(thermal_file, "Thermal Report")
        
        extra_images = []
        if extra_file:
            extra_text, extra_images = extract_from_pdf(extra_file, "Additional Document")
            insp_text += "\n\n" + extra_text

        progress.progress(30)
        
        # Step 2: Extract key sections (token saving)
        status.info("🔍 Step 2/4: Identifying key findings...")
        insp_key = get_key_sections(insp_text, max_chars=5500)
        therm_key = get_key_sections(therm_text, max_chars=3500)
        progress.progress(45)

        # Step 3: AI generation
        status.info("🤖 Step 3/4: AI is analyzing documents and writing report...")
        ddr_text = generate_ddr(insp_key, therm_key, property_name)
        progress.progress(75)

        # Step 4: Build Word doc
        status.info("📝 Step 4/4: Building professional Word document...")
        all_images = insp_images + therm_images + extra_images
        clean_name = re.sub(r'[\\/*?:"<>|,]', '', property_name[:20]).strip().replace(' ', '_')
        output_path = f"DDR_{clean_name}.docx"
        
        create_ddr_word_doc(
            ddr_text, 
            insp_images, 
            therm_images + extra_images,
            property_name=property_name,
            filename=output_path
        )
        progress.progress(100)

        # ── Done ───────────────────────────────────────────────
        status.success("✅ DDR Report Generated Successfully!")
        
        st.markdown("### 📋 Report Preview")
        with st.expander("Click to read the generated report text", expanded=True):
            st.text_area("Report Content", ddr_text, height=500, label_visibility="collapsed")

        # Images found summary
        st.info(f"🖼️ Images extracted: {len(insp_images)} from Inspection + "
                f"{len(therm_images)} from Thermal + "
                f"{len(extra_images)} from Additional = "
                f"**{len(all_images)} total**")

        # Download
        with open(output_path, "rb") as f:
            st.download_button(
                label="📥 Download DDR Report (.docx)",
                data=f,
                file_name=output_path,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

    except Exception as e:
        progress.empty()
        status.error(f"❌ Error: {str(e)}")
        st.exception(e)
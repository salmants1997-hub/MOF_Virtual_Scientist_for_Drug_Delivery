import streamlit as st
import PyPDF2
import json
from groq_client import call_groq
from agents import AGENT_1_ROLE, AGENT_2_ROLE, AGENT_3_ROLE, build_prompt

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

def extract_json_from_markdown(text):
    try:
        start = text.index("```")
        end = text.index("```", start + 3)
        json_block = text[start + 3:end].strip()
        if json_block.startswith("json"):
            json_block = json_block[4:].strip()
        return json.loads(json_block)
    except Exception:
        return None

st.set_page_config(page_title="Chemotherapy Drug Delivery", layout="wide")
st.title("🧪 Chemotherapy Drug Delivery")
st.markdown("""
Upload a research paper PDF. The system will scan it, identify MOFs, filter for biocompatibility, and output synthesis recipes.

**Agent Overview:**
- 🧠 **Agent 1: Literature Scanner** — Extracts and infers MOF properties from the uploaded article.
- 🧪 **Agent 2: Biocompatibility Filter** — Filters MOFs for safe, biocompatible candidates.
- 🧬 **Agent 3: Recipe Creator** — Generates synthesis steps and suitability scores for chemotherapy delivery.
""")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    st.success(f"📄 {uploaded_file.name}")
    document_text = extract_text_from_pdf(uploaded_file)

    with st.spinner("🔍 Agent 1 analyzing MOFs from text..."):
        agent1_prompt = build_prompt(AGENT_1_ROLE, "Extract MOFs related to chemotherapy drug delivery:", document_text)
        agent1_output = call_groq(agent1_prompt)
        st.markdown("### ✅ Agent 1 Output: Extracted MOFs")
        st.code(agent1_output, language="json")

    with st.spinner("🧪 Agent 2 filtering for biocompatibility..."):
        agent2_prompt = build_prompt(AGENT_2_ROLE, "Filter for biocompatible MOFs:", agent1_output)
        agent2_output = call_groq(agent2_prompt)
        st.markdown("### ✅ Agent 2 Output: Biocompatible MOFs")
        parsed = extract_json_from_markdown(agent2_output)
        if parsed:
            import pandas as pd
            df = pd.DataFrame(parsed)
            st.dataframe(df)
        else:
            st.warning("Could not parse Agent 2 output into a table. Showing raw output:")
            st.code(agent2_output, language="markdown")

    with st.spinner("⚗️ Agent 3 generating synthesis recipes and suitability scores..."):
        agent3_prompt = build_prompt(AGENT_3_ROLE, "Give synthesis recipe and suitability:", agent2_output)
        agent3_output = call_groq(agent3_prompt)
        st.markdown("### 📄 Agent 3 Output: Synthesis Recipes and Suitability Scores")
        st.markdown(agent3_output, unsafe_allow_html=True)

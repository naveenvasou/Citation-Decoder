import streamlit as st
import os
import pandas as pd
import tempfile
from dotenv import load_dotenv
import re
from src.main import CitationDecoder

# Load environment variables
load_dotenv()

# Set up page
st.set_page_config(
    page_title="Citation Decoder",
    page_icon="🔍",
    layout="wide"
)

# Header
st.title("🔍 Citation Decoder")
st.markdown("### Explains what each citation in a paper actually contributes")
st.markdown("---")

# Initialize the decoder
@st.cache_resource
def get_decoder():
    return CitationDecoder()

citation_decoder = get_decoder()

# Sidebar
st.sidebar.header("About")
st.sidebar.markdown("""
This tool extracts in-text citations from research papers and:
- Summarizes the cited paper in 1-2 lines
- Describes its purpose in context
- Tells you if the authors agree, critique, or extend the cited work
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### How to use")
st.sidebar.markdown("""
1. Upload a PDF file or provide an arXiv link
2. Wait for the analysis (this may take a few minutes)
3. Review the citation analysis
""")

# Main functionality
st.header("Upload Paper")

# Option tabs
tab1, tab2 = st.tabs(["Upload PDF", "arXiv Link"])

with tab1:
    uploaded_file = st.file_uploader("Upload a research paper PDF", type="pdf")
    
    if uploaded_file and st.button("Analyze Citations", key="analyze_pdf"):
        with st.spinner("Extracting and analyzing citations... This may take a few minutes."):
            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # Process the PDF
            results = citation_decoder.process_pdf(file_path=tmp_path)
            
            # Clean up the temporary file
            os.unlink(tmp_path)
            
            if "error" in results:
                st.error(results["error"])
            else:
                # Store results in session state for display
                st.session_state.results = results
                st.success(f"Found {len(results['citations'])} citations!")

with tab2:
    arxiv_input = st.text_input("Enter arXiv ID or URL", placeholder="2106.12423 or https://arxiv.org/abs/2106.12423")
    
    if arxiv_input and st.button("Analyze Citations", key="analyze_arxiv"):
        # Extract arxiv ID from input
        arxiv_id = arxiv_input
        
        # If it's a URL, extract the ID
        if "arxiv.org" in arxiv_input:
            match = re.search(r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)", arxiv_input)
            if match:
                arxiv_id = match.group(1)
        
        with st.spinner(f"Downloading and analyzing paper {arxiv_id}... This may take a few minutes."):
            # Process the arXiv paper
            results = citation_decoder.process_arxiv_paper(arxiv_id)
            
            if "error" in results:
                st.error(results["error"])
            else:
                # Store results in session state for display
                st.session_state.results = results
                st.success(f"Found {len(results['citations'])} citations!")

# Display results if available
if hasattr(st.session_state, "results") and st.session_state.results:
    st.header("Citation Analysis")
    
    results = st.session_state.results
    citations = results.get("citations", [])
    
    # Group citations by the same reference
    citation_groups = {}
    for citation in citations:
        key = citation["citation"]
        if key not in citation_groups:
            citation_groups[key] = []
        citation_groups[key].append(citation)
    
    # Create tabs for different views
    all_tab, purpose_tab, stance_tab = st.tabs(["All Citations", "By Purpose", "By Stance"])
    
    with all_tab:
        for i, (citation_key, citation_list) in enumerate(citation_groups.items()):
            with st.expander(f"{citation_key} ({len(citation_list)} occurrences)"):
                # Use the first occurrence for the main analysis
                main_citation = citation_list[0]
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("#### Summary")
                    st.markdown(f"**Contribution:** {main_citation.get('contribution', 'N/A')}")
                    
                    st.markdown("#### Context")
                    for j, citation in enumerate(citation_list):
                        context = citation.get('context', '').replace(citation.get('citation', ''), f"**{citation.get('citation', '')}**")
                        st.markdown(f"**Occurrence {j+1}:** ...{context}...")
                
                with col2:
                    st.markdown("#### Analysis")
                    st.markdown(f"**Purpose:** {main_citation.get('purpose', 'N/A')}")
                    st.markdown(f"**Stance:** {main_citation.get('stance', 'N/A')}")
    
    with purpose_tab:
        purposes = {}
        for citation in citations:
            purpose = citation.get("purpose", "Unknown")
            if purpose not in purposes:
                purposes[purpose] = []
            purposes[purpose].append(citation)
        
        for purpose, purpose_citations in purposes.items():
            with st.expander(f"{purpose} ({len(purpose_citations)} citations)"):
                for citation in purpose_citations:
                    st.markdown(f"**{citation['citation']}:** {citation.get('contribution', 'N/A')}")
                    st.markdown("---")
    
    with stance_tab:
        stances = {}
        for citation in citations:
            stance = citation.get("stance", "Unknown")
            if stance not in stances:
                stances[stance] = []
            stances[stance].append(citation)
        
        for stance, stance_citations in stances.items():
            with st.expander(f"{stance} ({len(stance_citations)} citations)"):
                for citation in stance_citations:
                    st.markdown(f"**{citation['citation']}:** {citation.get('contribution', 'N/A')}")
                    st.markdown("---")
    
    # References section if available
    if "references" in results and results["references"]:
        with st.expander("References Section"):
            for i, ref in enumerate(results["references"]):
                st.markdown(f"{i+1}. {ref}")
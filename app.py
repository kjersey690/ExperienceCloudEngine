import streamlit as st
import os
from dotenv import load_dotenv
from engine_logic import ResolutionEngine

# --- 1. Load Configuration ---
load_dotenv()

# Fetch from .env or environment
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "experience-cloud-errors") # Default fallback
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")

# --- 2. Professional UI Setup ---
st.set_page_config(page_title="ExBundle Sentinel", page_icon="🛡️")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .res-card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 6px solid #0070d2; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ ExBundle Sentinel")
st.caption(f"Connected to Index: `{INDEX_NAME}` | Model: `{MODEL_NAME}`")
st.divider()

# --- 3. Safety Check ---
if not PINECONE_KEY:
    st.error("Missing API Key! Please check your `.env` file for `PINECONE_API_KEY`.")
    st.stop()

# --- 4. Logic Execution ---
query = st.text_area("Paste Deployment Error Log:", placeholder="e.g. In field: Network - no Network named found...")

if query:
    # Initialize Engine (now with dynamic variables)
    engine = ResolutionEngine(api_key=PINECONE_KEY, index_name=INDEX_NAME)
    
    with st.spinner("Analyzing semantic patterns..."):
        results = engine.search(query)

    if results:
        for match in results:
            score = match['score']
            meta = match['metadata']
            
            # Dynamic Color Coding
            card_color = "#2e7d32" if score >= 0.80 else "#f9a825" if score >= 0.60 else "#d32f2f"
            
            st.markdown(f"""
                <div class="res-card" style="border-color: {card_color};">
                    <p style="color: {card_color}; font-weight: bold; font-size: 0.8rem;">
                        MATCH CONFIDENCE: {score:.1%}
                    </p>
                    <p><strong>Category:</strong> {meta.get('category', 'General')}</p>
                    <p><strong>Resolution:</strong> {meta.get('resolution')}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No high-confidence matches found in the current index.")
import streamlit as st
import os
from dotenv import load_dotenv
from engine_logic import ResolutionEngine
from db_manager import DatabaseManager  # Import the external manager

# --- 1. Load Configuration ---
load_dotenv()

PINECONE_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "experience-cloud-errors")
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")

# --- 2. Professional UI Setup ---
st.set_page_config(page_title="ExBundle Sentinel", page_icon="🛡️", layout="wide")

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
st.caption(f"Index: `{INDEX_NAME}` | Model: `{MODEL_NAME}`")

# --- 3. Initialize Logic ---
# Initialize DB Manager once at the top
db = DatabaseManager()

# Create Tabs for different functionalities
tab1, tab2 = st.tabs(["🔍 Search Resolutions", "📥 Contribute Error"])

# --- TAB 1: SEARCH INTERFACE ---
with tab1:
    if not PINECONE_KEY:
        st.error("Missing PINECONE_API_KEY in .env")
    else:
        query = st.text_area("Paste Deployment Error Log:", height=150, placeholder="e.g. In field: Network - no Network named found...")

        if query:
            engine = ResolutionEngine(api_key=PINECONE_KEY, index_name=INDEX_NAME)
            
            with st.spinner("Analyzing semantic patterns..."):
                results = engine.search(query)

            if results:
                st.subheader(f"Found {len(results)} Potential Fixes")
                for match in results:
                    score = match['score']
                    meta = match['metadata']
                    
                    # Color based on score
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
                st.warning("No high-confidence matches found. Consider contributing this error to the team!")

# --- TAB 2: CONTRIBUTION FORM ---
with tab2:
    st.header("Help the Team")
    st.write("Submit a new error and its fix to the Supabase review queue.")
    
    with st.form("contribution_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            error_name = st.text_input("Deployment Error Name", placeholder="The raw error string")
        with col2:
            category = st.selectbox("Category", ["ExperienceBundle", "Network", "NavigationMenu", "Apex/LWC", "Other"])
            
        replication = st.text_area("How to replicate?", placeholder="Steps to trigger this error...")
        resolution = st.text_area("How to resolve?", placeholder="Step-by-step fix...")
        
        submitted = st.form_submit_button("Submit for Team Review")
        
        if submitted:
            if error_name and resolution:
                with st.spinner("Syncing with Supabase..."):
                    success = db.submit_error(error_name, replication, resolution, category)
                    if success:
                        st.success("✅ Successfully submitted! A team lead will review this for the AI Index.")
                    else:
                        st.error("Submission failed. Check your Supabase connection.")
            else:
                st.warning("Please provide at least the Error Name and the Resolution.")
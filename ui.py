import streamlit as st
import requests
from sparql_engine import run_sparql
from ontology_writer import add_disaster

API = "http://127.0.0.1:5000"

st.set_page_config(page_title="Sri Lanka Disaster Ontology", layout="wide")

st.title("🇱🇰 Ontology-Based Disaster Management System")

tabs = st.tabs([
    "📊 Dashboard",
    "🔍 SPARQL Query",
    "➕ Add Disaster",
    "🧠 Reasoning Info"
])

# ---------------- Dashboard ----------------
with tabs[0]:
    st.header("Active Disasters")
    data = requests.get(f"{API}/disasters").json()
    st.table(data)

# ---------------- SPARQL ----------------
with tabs[1]:
    st.header("SPARQL Query Editor")

    query = st.text_area(
        "Edit and run SPARQL query:",
        height=200,
        value="""PREFIX d: <http://www.example.org/disaster.owl#>
SELECT ?disaster ?severity
WHERE {
  ?disaster a d:Disaster .
  ?disaster d:severityLevel ?severity .
}"""
    )

    if st.button("Run Query"):
        try:
            results = run_sparql(query)
            st.success("Query executed successfully")
            st.table(results)
        except Exception as e:
            st.error(str(e))

# ---------------- Add Disaster ----------------
with tabs[2]:
    st.header("Add New Disaster")

    name = st.text_input("Disaster Name")
    dtype = st.selectbox("Type", ["Flood", "Landslide"])
    severity = st.selectbox("Severity", ["Low", "Medium", "High"])
    location = st.selectbox("Location", ["Kandy", "Ratnapura"])
    resources = st.multiselect("Resources", ["FoodSupply", "MedicalKit"])

    if st.button("Add Disaster"):
        add_disaster(name, dtype, severity, location, resources)
        st.success("Disaster added to ontology!")

# ---------------- Reasoning ----------------
with tabs[3]:
    st.header("Ontology Reasoning")

    st.markdown("""
**Reasoning Engines Used**
- Pellet
- HermiT

**Purpose of Reasoning**
- Infer implicit knowledge
- Validate class consistency
- Detect logical conflicts

**Example**
If a `Flood` is a subclass of `Disaster`, the reasoner can automatically infer
that all flood instances are also disasters.
""")

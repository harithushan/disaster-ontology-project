import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sparql_engine import SPARQLEngine
from owlready2 import *

# Page config
st.set_page_config(
    page_title="🇱🇰 Sri Lanka Disaster Management",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
API_BASE = "http://127.0.0.1:5000"
ONTOLOGY_PATH = "ontology/disaster_ontology.rdf"

# Initialize SPARQL engine
@st.cache_resource
def get_sparql_engine():
    return SPARQLEngine(ONTOLOGY_PATH)

sparql_engine = get_sparql_engine()

# Helper functions
def fetch_api(endpoint):
    """Fetch data from API"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
        return response.json()
    except:
        return []

def create_metric_card(label, value, delta=None):
    """Create a styled metric card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label=label, value=value, delta=delta)

# Main header
st.markdown('<div class="main-header">🚨 Sri Lanka Disaster Management System</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/320px-Flag_of_Sri_Lanka.svg.png", width=250)
    st.title("Navigation")
    st.info("🌟 Advanced Ontology-Based Disaster Response System")
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    stats = fetch_api("/statistics")
    if stats:
        st.metric("Active Disasters", stats.get("active_disasters", 0))
        st.metric("Total Shelters", stats.get("total_shelters", 0))
        st.metric("Volunteers", stats.get("total_volunteers", 0))

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Dashboard",
    "🔍 SPARQL Query",
    "🌪️ Disasters",
    "🏠 Shelters",
    "🤝 Volunteers",
    "➕ Add Data",
    "📚 Documentation"
])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    st.header("📊 Real-time Dashboard")
    
    # Get statistics
    stats = fetch_api("/statistics")
    
    if stats:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Disasters",
                stats.get("total_disasters", 0),
                delta=f"{stats.get('active_disasters', 0)} Active"
            )
        
        with col2:
            capacity = stats.get("total_capacity", 0)
            occupancy = stats.get("total_occupancy", 0)
            st.metric(
                "Shelter Capacity",
                f"{capacity:,}",
                delta=f"{capacity - occupancy:,} Available"
            )
        
        with col3:
            st.metric(
                "Volunteers",
                stats.get("total_volunteers", 0)
            )
        
        with col4:
            st.metric(
                "Resources",
                stats.get("total_resources", 0)
            )
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Disasters by Type")
            if "disasters_by_type" in stats:
                disaster_types = stats["disasters_by_type"]
                fig = px.pie(
                    values=list(disaster_types.values()),
                    names=list(disaster_types.keys()),
                    title="Distribution of Disaster Types",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Disasters by Severity")
            if "disasters_by_severity" in stats:
                severity_data = stats["disasters_by_severity"]
                fig = px.bar(
                    x=list(severity_data.keys()),
                    y=list(severity_data.values()),
                    title="Severity Distribution",
                    labels={"x": "Severity Level", "y": "Count"},
                    color=list(severity_data.keys()),
                    color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Active disasters map
        st.subheader("🗺️ Active Disasters by District")
        districts = fetch_api("/districts")
        if districts:
            df_districts = pd.DataFrame(districts)
            fig = px.bar(
                df_districts,
                x="name",
                y="active_disasters",
                title="Active Disasters per District",
                labels={"name": "District", "active_disasters": "Active Disasters"},
                color="active_disasters",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Shelter occupancy
        st.subheader("🏠 Shelter Occupancy Status")
        shelters = fetch_api("/shelters")
        if shelters:
            df_shelters = pd.DataFrame(shelters)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Occupied',
                x=df_shelters['name'],
                y=df_shelters['current_occupancy'],
                marker_color='indianred'
            ))
            fig.add_trace(go.Bar(
                name='Available',
                x=df_shelters['name'],
                y=df_shelters['available_space'],
                marker_color='lightsalmon'
            ))
            fig.update_layout(
                barmode='stack',
                title='Shelter Capacity vs Occupancy',
                xaxis_title='Shelter',
                yaxis_title='Capacity'
            )
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2: SPARQL QUERY ====================
with tab2:
    st.header("🔍 SPARQL Query Interface")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Predefined Queries")
        predefined_queries = sparql_engine.get_predefined_queries()
        
        selected_query = st.selectbox(
            "Choose a query:",
            options=["Custom Query"] + [q["name"] for q in predefined_queries],
            index=0
        )
        
        if selected_query != "Custom Query":
            query_info = next((q for q in predefined_queries if q["name"] == selected_query), None)
            if query_info:
                st.info(f"**Description:** {query_info['description']}")
                if st.button("🚀 Run This Query"):
                    result = sparql_engine.run_predefined_query(query_info["id"])
                    st.session_state.query_result = result
    
    with col2:
        st.subheader("Query Editor")
        
        # Set default query
        default_query = """PREFIX d: <http://www.srilanka.gov/disaster.owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?disaster ?name ?severity ?location
WHERE {
  ?disaster rdf:type/rdfs:subClassOf* d:Disaster .
  OPTIONAL { ?disaster d:hasName ?name }
  OPTIONAL { ?disaster d:severityLevel ?severity }
  OPTIONAL { ?disaster d:occursIn ?loc .
             ?loc d:hasName ?location }
}
ORDER BY ?severity
LIMIT 10"""
        
        if selected_query != "Custom Query":
            query_info = next((q for q in predefined_queries if q["name"] == selected_query), None)
            if query_info:
                query_id = query_info["id"]
                default_query = sparql_engine.PREDEFINED_QUERIES[query_id]["query"]
        
        query_text = st.text_area(
            "Edit SPARQL Query:",
            value=default_query,
            height=300,
            help="Write your SPARQL query here. Use PREFIX declarations for namespaces."
        )
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            run_btn = st.button("▶️ Execute Query", type="primary")
        with col_btn2:
            if st.button("📋 Copy Query"):
                st.code(query_text, language="sparql")
        
        if run_btn:
            with st.spinner("Executing query..."):
                result = sparql_engine.run_query(query_text)
                st.session_state.query_result = result
    
    # Display results
    if "query_result" in st.session_state:
        result = st.session_state.query_result
        
        st.markdown("---")
        st.subheader("Query Results")
        
        if result["success"]:
            if result["results"]:
                df = pd.DataFrame(result["results"][1:], columns=result["results"][0])
                
                st.success(f"✅ Query executed successfully! Found {result['count']} results.")
                
                # Display options
                col1, col2 = st.columns([3, 1])
                with col2:
                    show_as = st.radio("Display as:", ["Table", "JSON"], horizontal=True)
                
                if show_as == "Table":
                    st.dataframe(df, use_container_width=True)
                else:
                    st.json(result["results"])
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("Query returned no results.")
        else:
            st.error(f"❌ Query Error: {result['error']}")

# ==================== TAB 3: DISASTERS ====================
with tab3:
    st.header("🌪️ Disaster Management")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_type = st.selectbox(
            "Filter by Type:",
            ["All", "Flood", "Landslide", "Cyclone", "Drought", "Tsunami"]
        )
    
    with col2:
        filter_severity = st.selectbox(
            "Filter by Severity:",
            ["All", "High", "Medium", "Low"]
        )
    
    with col3:
        filter_status = st.selectbox(
            "Filter by Status:",
            ["All", "Active", "Resolved", "Monitoring"]
        )

    # Date filter
    date_range = st.date_input("Filter by Date Range", [])
    
    # Fetch disasters
    if filter_type != "All":
        disasters = fetch_api(f"/disasters/type/{filter_type}")
    elif filter_severity != "All":
        disasters = fetch_api(f"/disasters/severity/{filter_severity}")
    else:
        disasters = fetch_api("/disasters")
    
    # Apply additional filters
    if disasters:
        df = pd.DataFrame(disasters)
        
        if filter_severity != "All":
            df = df[df["severity"] == filter_severity]
        
        if filter_status != "All":
            df = df[df["status"] == filter_status]
            
        # Apply date filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            # Ensure date column is datetime
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
            df = df.loc[mask]
        
        st.markdown(f"### Found {len(df)} disasters")
        
        # Display as cards
        for idx, row in df.iterrows():
            with st.expander(f"🔴 {row['name']} - {row['severity']} Severity"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Type:** {row['type']}")
                    st.markdown(f"**Location:** {row['location_name']}")
                    st.markdown(f"**Status:** {row['status']}")
                
                with col2:
                    st.markdown(f"**Severity:** {row['severity']}")
                    st.markdown(f"**Date:** {row['date']}")
                    if row.get('affected_count', 0) > 0:
                        st.markdown(f"**Affected:** {row['affected_count']:,} people")
                
                with col3:
                    st.markdown("**Required Resources:**")
                    for resource in row['resources']:
                        st.markdown(f"- {resource}")

# ==================== TAB 4: SHELTERS ====================
with tab4:
    st.header("🏠 Shelter Information")
    
    # Tabs for different views
    shelter_tab1, shelter_tab2 = st.tabs(["All Shelters", "Available Shelters"])
    
    with shelter_tab1:
        shelters = fetch_api("/shelters")
        if shelters:
            df = pd.DataFrame(shelters)
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Shelters", len(df))
            with col2:
                st.metric("Total Capacity", f"{df['capacity'].sum():,}")
            with col3:
                st.metric("Available Spaces", f"{df['available_space'].sum():,}")
            
            st.markdown("---")
            
            # Display shelters
            for idx, row in df.iterrows():
                status_color = "🟢" if row['status'] == "Available" else "🟡" if row['status'] == "Active" else "🔴"
                
                with st.expander(f"{status_color} {row['name']} - {row['occupancy_rate']}% Occupied"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Capacity:** {row['capacity']}")
                        st.markdown(f"**Current Occupancy:** {row['current_occupancy']}")
                        st.markdown(f"**Available:** {row['available_space']}")
                    
                    with col2:
                        st.markdown(f"**Status:** {row['status']}")
                        st.markdown(f"**Occupancy Rate:** {row['occupancy_rate']}%")
                    
                    with col3:
                        st.markdown(f"**Contact:** {row['contact']}")
                    
                    # Progress bar
                    st.progress(row['occupancy_rate'] / 100)
    
    with shelter_tab2:
        available_shelters = fetch_api("/shelters/available")
        if available_shelters:
            st.success(f"Found {len(available_shelters)} shelters with available space")
            df = pd.DataFrame(available_shelters)
            st.dataframe(df, use_container_width=True)

# ==================== TAB 5: VOLUNTEERS ====================
with tab5:
    st.header("🤝 Volunteer Management")
    
    volunteers = fetch_api("/volunteers")
    if volunteers:
        df_vol = pd.DataFrame(volunteers)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Volunteers", len(df_vol))
        with col2:
            st.metric("Advanced Skills", len(df_vol[df_vol['skill_level'] == "Advanced"]))
        with col3:
            st.metric("Assigned", len(df_vol[df_vol['assigned_shelter'] != "Unassigned"]))
            
        st.markdown("---")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_skill = st.selectbox(
                "Filter by Skill Level:",
                ["All"] + sorted(list(df_vol['skill_level'].unique()))
            )
        with col2:
            filter_shelter = st.selectbox(
                "Filter by Assigned Shelter:",
                ["All"] + sorted(list(df_vol['assigned_shelter'].unique()))
            )
            
        # Apply filters
        if filter_skill != "All":
            df_vol = df_vol[df_vol['skill_level'] == filter_skill]
        if filter_shelter != "All":
            df_vol = df_vol[df_vol['assigned_shelter'] == filter_shelter]
            
        st.dataframe(
            df_vol[['name', 'skill_level', 'assigned_shelter', 'contact']],
            column_config={
                "name": "Name",
                "skill_level": "Skill Level", 
                "assigned_shelter": "Assigned Shelter",
                "contact": "Contact Number"
            },
            use_container_width=True,
            hide_index=True
        )

# ==================== TAB 6: ADD DATA ====================
with tab6:
    st.header("➕ Add New Data to Ontology")
    
    add_tab1, add_tab2, add_tab3, add_tab4, add_tab5 = st.tabs([
        "🌪️ Disaster", "🤝 Volunteer", "📦 Resource", "🏢 Organization", "📍 Location"
    ])
    
    with add_tab1:
        st.subheader("Add New Disaster")
        
        with st.form("add_disaster_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                disaster_name = st.text_input("Disaster Name*", placeholder="e.g., Colombo Flood 2026")
                
                # Dynamic Type Selection
                existing_types = ["Flood", "Landslide", "Cyclone", "Drought", "Tsunami"]
                type_selection = st.selectbox("Type*", existing_types + ["➕ Add New Type..."])
                
                disaster_type = type_selection
                create_new_type = False
                
                if type_selection == "➕ Add New Type...":
                    new_type_name = st.text_input("Enter New Disaster Type Name")
                    if new_type_name:
                        disaster_type = new_type_name
                        create_new_type = True
                
                severity = st.selectbox("Severity*", ["Low", "Medium", "High"])
            
            with col2:
                districts = fetch_api("/districts")
                district_names = [d["id"] for d in districts] if districts else []
                
                # Dynamic Location
                loc_selection = st.selectbox("Location*", district_names + ["➕ Add New Location..."])
                location = loc_selection
                
                if loc_selection == "➕ Add New Location...":
                    st.info("To add a new location, please use the 'Add Location' tab first.")
                    location = None
                
                date_occurred = st.date_input("Date Occurred")
                status = st.selectbox("Status", ["Active", "Monitoring", "Resolved"])
            
            resources = st.multiselect(
                "Required Resources",
                ["FoodSupply", "MedicalKit", "DrinkingWater", "Blankets", "Tents", "ClothingPacks"]
            )
            
            submit_disaster = st.form_submit_button("Add Disaster", type="primary")
            
            if submit_disaster:
                if disaster_name and disaster_type and location:
                    payload = {
                        "name": disaster_name,
                        "type": disaster_type,
                        "severity": severity,
                        "location": location,
                        "date": str(date_occurred),
                        "status": status,
                        "create_new_type": create_new_type
                    }
                    
                    try:
                        requests.post(f"{API_BASE}/disasters/add", json=payload)
                        st.success(f"✅ Disaster '{disaster_name}' added successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please fill all required fields (marked with *)")
    


    
    with add_tab2:
        st.subheader("Add New Volunteer")
        with st.form("add_volunteer_form"):
            v_name = st.text_input("Name*")
            v_contact = st.text_input("Contact Number")
            v_skill = st.selectbox("Skill Level", ["Basic", "Intermediate", "Advanced", "Medical", "Rescue"])
            
            shelters = fetch_api("/shelters")
            shelter_names = [s["id"] for s in shelters] if shelters else []
            v_shelter = st.selectbox("Assign to Shelter (Optional)", ["Unassigned"] + shelter_names)
            
            if st.form_submit_button("Add Volunteer"):
                if v_name:
                    requests.post(f"{API_BASE}/volunteers/add", json={
                        "name": v_name, "contact": v_contact, 
                        "skill_level": v_skill, "assigned_shelter": v_shelter
                    })
                    st.success("Volunteer added!")
                    
    with add_tab3:
        st.subheader("Add New Resource")
        with st.form("add_resource_form"):
            r_name = st.text_input("Resource Name*")
            r_type = st.selectbox("Type", ["FoodResource", "WaterResource", "MedicalResource", "ClothingResource"])
            r_qty = st.number_input("Quantity", min_value=0)
            
            if st.form_submit_button("Add Resource"):
                if r_name:
                    requests.post(f"{API_BASE}/resources/add", json={
                        "name": r_name, "type": r_type, "quantity": r_qty
                    })
                    st.success("Resource added!")

    with add_tab4:
        st.subheader("Add New Organization")
        with st.form("add_org_form"):
            o_name = st.text_input("Organization Name*")
            o_contact = st.text_input("Contact")
            
            if st.form_submit_button("Add Organization"):
                if o_name:
                    requests.post(f"{API_BASE}/organizations/add", json={
                        "name": o_name, "contact": o_contact
                    })
                    st.success("Organization added!")

    with add_tab5:
        st.subheader("Add New Location")
        with st.form("add_loc_form"):
            l_name = st.text_input("Location Name*")
            l_type = st.selectbox("Type", ["District", "Province"])
            
            provinces = fetch_api("/provinces")
            prov_names = [p["id"] for p in provinces] if provinces else []
            l_parent = st.selectbox("Located In (Province)", ["None"] + prov_names)
            
            if st.form_submit_button("Add Location"):
                if l_name:
                    requests.post(f"{API_BASE}/locations/add", json={
                        "name": l_name, "type": l_type, "parent_id": l_parent if l_parent != "None" else None
                    })
                    st.success("Location added!")

# ==================== TAB 7: DOCUMENTATION ====================
with tab7:
    st.header("📚 System Documentation")
    
    doc_tab1, doc_tab2, doc_tab3 = st.tabs(["About", "OWL Classes", "SPARQL Guide"])
    
    with doc_tab1:
        st.markdown("""
        ## 🇱🇰 Sri Lanka Disaster Management Ontology System
        
        ### Overview
        This system uses **OWL (Web Ontology Language)** to create a comprehensive disaster management
        knowledge base for Sri Lanka. The ontology captures:
        
        - 🌪️ **Disasters**: Floods, Landslides, Cyclones, Droughts, Tsunamis
        - 🏠 **Shelters**: Emergency accommodation facilities
        - 👥 **Volunteers**: Response team members
        - 📦 **Resources**: Food, medical supplies, water, clothing
        - 📍 **Locations**: Provinces, Districts
        - 🏢 **Organizations**: DMC, Red Cross, Army Rescue
        
        ### Features
        - ✅ Real-time disaster tracking
        - ✅ SPARQL query interface
        - ✅ Interactive dashboards
        - ✅ Resource management
        - ✅ Shelter capacity monitoring
        - ✅ Volunteer coordination
        
        ### Technology Stack
        - **Ontology**: OWL (Web Ontology Language)
        - **Reasoning**: Pellet, HermiT
        - **Query**: SPARQL
        - **Backend**: Flask, Owlready2
        - **Frontend**: Streamlit
        - **Visualization**: Plotly
        """)
    
    with doc_tab2:
        st.markdown("""
        ## OWL Class Hierarchy
        
        ### Main Classes
        
        #### 🌪️ Disaster (Base Class)
        - **Flood**: Water-related disasters
        - **Landslide**: Ground movement disasters
        - **Cyclone**: Wind-related disasters
        - **Drought**: Water scarcity disasters
        - **Tsunami**: Ocean wave disasters
        
        #### 📍 Location (Base Class)
        - **Province**: Administrative regions
        - **District**: Sub-divisions of provinces
        
        #### 📦 Resource (Base Class)
        - **FoodResource**: Food supplies
        - **MedicalResource**: Medical equipment
        - **WaterResource**: Drinking water
        - **ClothingResource**: Clothing and blankets
        
        #### Other Classes
        - **Shelter**: Emergency accommodation
        - **Volunteer**: Response personnel
        - **Organization**: Response organizations
        - **AffectedPopulation**: Disaster victims
        
        ### Object Properties
        - `occursIn`: Links disaster to location
        - `hasShelter`: Links location to shelters
        - `requiresResource`: Links disaster to needed resources
        - `assignedTo`: Links volunteer to shelter
        - `locatedIn`: Links district to province
        
        ### Data Properties
        - `hasName`: Entity name
        - `capacity`: Shelter capacity
        - `severityLevel`: Disaster severity
        - `dateOccurred`: Disaster date
        - `quantityAvailable`: Resource quantity
        """)
    
    with doc_tab3:
        st.markdown("""
        ## SPARQL Query Guide
        
        ### Basic Query Structure
        ```sparql
        PREFIX d: <http://www.srilanka.gov/disaster.owl#>
        
        SELECT ?variable1 ?variable2
        WHERE {
          ?variable1 rdf:type d:ClassName .
          ?variable1 d:propertyName ?variable2 .
        }
        ```
        
        ### Common Patterns
        
        #### Find All Disasters
        ```sparql
        SELECT ?disaster ?name
        WHERE {
          ?disaster rdf:type/rdfs:subClassOf* d:Disaster .
          ?disaster d:hasName ?name .
        }
        ```
        
        #### Find High Severity Disasters
        ```sparql
        SELECT ?disaster ?name
        WHERE {
          ?disaster d:severityLevel "High" .
          ?disaster d:hasName ?name .
        }
        ```
        
        #### Find Available Shelters
        ```sparql
        SELECT ?shelter ?capacity ?occupancy
        WHERE {
          ?shelter rdf:type d:Shelter .
          ?shelter d:capacity ?capacity .
          ?shelter d:currentOccupancy ?occupancy .
          FILTER(?capacity > ?occupancy)
        }
        ```
        
        #### Count Disasters by Type
        ```sparql
        SELECT ?type (COUNT(?disaster) AS ?count)
        WHERE {
          ?disaster rdf:type ?type .
          ?type rdfs:subClassOf d:Disaster .
        }
        GROUP BY ?type
        ```
        
        ### Useful Filters
        - `FILTER(?severity = "High")`: Filter by value
        - `FILTER(?capacity > 100)`: Numeric comparison
        - `FILTER(YEAR(?date) = 2024)`: Date filtering
        
        ### Tips
        - Use `OPTIONAL` for properties that might not exist
        - Use `ORDER BY` to sort results
        - Use `LIMIT` to restrict result count
        - Use `COUNT`, `SUM`, `AVG` for aggregations
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🇱🇰 Sri Lanka Disaster Management System | Powered by OWL & SPARQL</p>
        <p>Built with ❤️ using Streamlit, Flask, and Owlready2</p>
    </div>
    """,
    unsafe_allow_html=True
)
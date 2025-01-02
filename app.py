import streamlit as st
from streamlit_molstar import st_molstar, st_molstar_rcsb, st_molstar_remote
import pandas as pd
import numpy as np
import json

# Set page config for wide layout
st.set_page_config(layout="wide")

# Custom CSS to set minimal margins and clean up UI
st.markdown("""
<style>
    .block-container {
        padding: 1rem;
    }
    # [data-testid="stToolbar"] {
    #     display: none;
    # }
    .main > div {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    header {
        display: none;
    }
    section[data-testid="stSidebar"] {
        display: none;
    }
    /* Add custom height for rows */
    [data-testid="column"] {
        height: calc(50vh - 2rem);
        overflow: auto;
    }
    /* Make dataframe use full width */
    [data-testid="stDataFrame"] {
        width: 100% !important;
    }
    .stDataFrame > div {
        width: 100% !important;
    }
    .stDataFrame > div > iframe {
        width: 100% !important;
    }
    /* Custom dialog styling */
    .dialog-container {
        max-height: 300px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f8f9fa;
        font-family: monospace;
        white-space: pre;
    }
</style>
""", unsafe_allow_html=True)

# Create two columns with 2:1 ratio
main_content, right_panel = st.columns([2, 1])

# Main content area
with main_content:
    # Container for first row (50% height)
    row1 = st.container()
    with row1:
        st.header("Molecule Viewer")
        st_molstar_remote("https://files.rcsb.org/view/1LOL.cif", key='sds')
    
    # Container for second row (50% height)
    row2 = st.container()
    with row2:
        st.header("Protein Data")
        
        # Create sample protein data
        data = {
            'Residue': [f'RES_{i}' for i in range(1, 11)],
            'Chain': ['A', 'A', 'B', 'B', 'A', 'C', 'C', 'A', 'B', 'C'],
            'Position': np.arange(1, 11),
            'B-factor': np.random.uniform(20, 60, 10).round(2),
            'SASA': np.random.uniform(0, 100, 10).round(2),
            'Secondary Structure': np.random.choice(['Helix', 'Sheet', 'Loop'], 10),
        }
        df = pd.DataFrame(data)
        
        # Add styling to the dataframe
        def highlight_chains(val):
            colors = {'A': 'background-color: #ffcccc',
                     'B': 'background-color: #ccffcc',
                     'C': 'background-color: #cce5ff'}
            return colors.get(val, '')
        
        styled_df = df.style.apply(lambda x: [highlight_chains(v) for v in x], 
                                 subset=['Chain'])
        
        # Display the table with custom styling
        st.dataframe(styled_df, height=300, use_container_width=True)

# Right panel content
with right_panel:
    st.header("Input Elements")
    
    # Search and Filters
    with st.expander("🔍 Search & Filter", expanded=True):
        # Initialize session state
        if 'show_filters' not in st.session_state:
            st.session_state.show_filters = False
            st.session_state.filter_values = {}
            
        residue_search = st.text_input("Search by Residue", placeholder="Enter residue name...")
        chain_filter = st.selectbox("Filter by Chain", ["All Chains", "Chain A", "Chain B", "Chain C"])
        
        # Checkboxes for display options
        st.subheader("Display Options")
        col1, col2 = st.columns(2)
        with col1:
            show_bfactor = st.checkbox("Show B-factor", value=True)
            show_sasa = st.checkbox("Show SASA", value=True)
        with col2:
            show_position = st.checkbox("Show Position", value=True)
            show_chain = st.checkbox("Show Chain", value=True)
        
        st.subheader("Structure Filters")
        sec_structure = st.multiselect("Secondary Structure", ["Helix", "Sheet", "Loop"])
        bfactor_range = st.slider("B-factor Range", min_value=0.0, max_value=100.0, value=(20.0, 60.0))
        
        # Create filter values dictionary
        current_filters = {
            "residue_search": residue_search,
            "chain_filter": chain_filter,
            "display_options": {
                "b_factor": show_bfactor,
                "sasa": show_sasa,
                "position": show_position,
                "chain": show_chain
            },
            "secondary_structure": sec_structure,
            "b_factor_range": {
                "min": float(bfactor_range[0]),
                "max": float(bfactor_range[1])
            }
        }
        
        # Button to show dialog
        if st.button("Apply Filters", key="apply_filters"):
            st.session_state.filter_values = current_filters
            st.session_state.show_filters = True
        
        # Show dialog with filter values
        if st.session_state.show_filters:
            st.markdown("### Selected Filters")
            st.code(json.dumps(st.session_state.filter_values, indent=2), language="json")
            if st.button("Close Dialog", key="close_dialog"):
                st.session_state.show_filters = False
                st.rerun()
    
    # Text inputs
    with st.expander("📝 Text Inputs", expanded=True):
        st.text_input("Simple Text", placeholder="Enter text...", key="simple_text")
        st.text_area("Multi-line Text", placeholder="Enter long text...", height=100)
        st.number_input("Number Input", min_value=0, max_value=100, value=50)
        
    # Selection inputs
    with st.expander("🔍 Selection Inputs", expanded=True):
        st.selectbox("Dropdown", ["Option 1", "Option 2", "Option 3"], key="dropdown")
        st.multiselect("Multi-Select", ["Item 1", "Item 2", "Item 3", "Item 4"])
        st.radio("Radio Buttons", ["Choice 1", "Choice 2", "Choice 3"])
        
    # Range inputs
    with st.expander("📊 Range Inputs", expanded=True):
        st.slider("Simple Slider", 0, 100, 50, key="simple_slider")
        values = st.slider("Range Slider", 0, 100, (25, 75))
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Checkbox 1", key="cb1")
            st.checkbox("Checkbox 2", key="cb2")
        with col2:
            st.checkbox("Checkbox 3", key="cb3")
            st.checkbox("Checkbox 4", key="cb4")
            
    # Date and time
    with st.expander("📅 Date & Time", expanded=True):
        st.date_input("Select Date")
        st.time_input("Select Time")
        
    # Color and file
    with st.expander("🎨 Color & File", expanded=True):
        st.color_picker("Pick a Color", "#00EEFF")
        st.file_uploader("Upload File", type=["txt", "pdf", "png"])
        
    # Buttons and download
    with st.expander("🔘 Buttons & Downloads", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.button("Normal Button", key="normal_btn")
            if st.download_button("Download File", "Sample content", "sample.txt", key="download_btn"):
                st.write("Downloaded!")
        with col2:
            if st.button("Toggle Button", type="primary", key="toggle_btn"):
                st.write("Primary clicked!")
                
    # Progress and status
    with st.expander("📈 Progress & Status", expanded=True):
        st.progress(75)
        st.spinner("Loading...")
        st.success("Success message")
        st.info("Info message")
        st.warning("Warning message")
        st.error("Error message")
        
    # Metrics
    with st.expander("📊 Metrics", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Value 1", 42, 2)
        with col2:
            st.metric("Value 2", 73, -5)
        with col3:
            st.metric("Value 3", 123, 0)

import streamlit as st
from streamlit_molstar import st_molstar, st_molstar_rcsb, st_molstar_remote
import pandas as pd
import numpy as np
import json

# Initialize session state variables
def init_session_state():
    if 'show_filters' not in st.session_state:
        st.session_state.show_filters = False
    if 'filter_values' not in st.session_state:
        st.session_state.filter_values = {}
    if 'display_options' not in st.session_state:
        st.session_state.display_options = {
            'b_factor': True,
            'sasa': True,
            'position': True,
            'chain': True
        }

# Callback functions for actions
def on_filter_apply():
    current_filters = {
        "residue_search": st.session_state.residue_search,
        "chain_filter": st.session_state.chain_filter,
        "display_options": {
            "b_factor": st.session_state.show_bfactor,
            "sasa": st.session_state.show_sasa,
            "position": st.session_state.show_position,
            "chain": st.session_state.show_chain
        },
        "secondary_structure": st.session_state.sec_structure,
        "b_factor_range": {
            "min": float(st.session_state.bfactor_range[0]),
            "max": float(st.session_state.bfactor_range[1])
        }
    }
    st.session_state.filter_values = current_filters
    st.session_state.show_filters = True

def on_dialog_close():
    st.session_state.show_filters = False
    st.rerun()

def on_color_change():
    st.session_state.last_color = st.session_state.color_picker
    # Add any color-related logic here

def on_file_upload():
    if st.session_state.file_uploader is not None:
        # Handle file upload logic here
        st.success(f"Uploaded file: {st.session_state.file_uploader.name}")

# UI Components
def render_search_filters():
    with st.expander("🔍 Search & Filter", expanded=True):
        st.text_input("Search by Residue", 
                     placeholder="Enter residue name...",
                     key="residue_search")
        
        st.selectbox("Filter by Chain", 
                    ["All Chains", "Chain A", "Chain B", "Chain C"],
                    key="chain_filter")
        
        st.subheader("Display Options")
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Show B-factor", value=True, key="show_bfactor")
            st.checkbox("Show SASA", value=True, key="show_sasa")
        with col2:
            st.checkbox("Show Position", value=True, key="show_position")
            st.checkbox("Show Chain", value=True, key="show_chain")
        
        st.subheader("Structure Filters")
        st.multiselect("Secondary Structure", 
                      ["Helix", "Sheet", "Loop"],
                      key="sec_structure")
        
        st.slider("B-factor Range", 
                 min_value=0.0, 
                 max_value=100.0, 
                 value=(20.0, 60.0),
                 key="bfactor_range")
        
        st.button("Apply Filters", 
                 key="apply_filters", 
                 on_click=on_filter_apply)
        
        if st.session_state.show_filters:
            st.markdown("### Selected Filters")
            st.code(json.dumps(st.session_state.filter_values, indent=2), 
                   language="json")
            st.button("Close Dialog", 
                     key="close_dialog", 
                     on_click=on_dialog_close)

def render_input_samples():
    with st.expander("📝 Input Examples", expanded=True):
        # Color picker with callback
        st.color_picker("Pick a Color", 
                       "#00EEFF", 
                       key="color_picker",
                       on_change=on_color_change)
        
        # File uploader with callback
        st.file_uploader("Upload File", 
                        type=["txt", "pdf", "png"],
                        key="file_uploader",
                        on_change=on_file_upload)
        
        # Metrics with dynamic updates
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Value 1", 
                     st.session_state.get('metric1', 42), 
                     st.session_state.get('delta1', 2))
        with col2:
            st.metric("Value 2", 
                     st.session_state.get('metric2', 73), 
                     st.session_state.get('delta2', -5))
        with col3:
            st.metric("Value 3", 
                     st.session_state.get('metric3', 123), 
                     st.session_state.get('delta3', 0))

def render_protein_table():
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
    
    def highlight_chains(val):
        colors = {'A': 'background-color: #ffcccc',
                 'B': 'background-color: #ccffcc',
                 'C': 'background-color: #cce5ff'}
        return colors.get(val, '')
    
    styled_df = df.style.apply(lambda x: [highlight_chains(v) for v in x], 
                             subset=['Chain'])
    st.dataframe(styled_df, height=300, use_container_width=True)

def main():
    st.set_page_config(layout="wide")
    
    # Custom CSS
    st.markdown("""
    <style>
        .block-container {
            padding: 1rem;
        }
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
        [data-testid="column"] {
            height: calc(50vh - 2rem);
            overflow: auto;
        }
        [data-testid="stDataFrame"] {
            width: 100% !important;
        }
        .stDataFrame > div {
            width: 100% !important;
        }
        .stDataFrame > div > iframe {
            width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Create layout
    main_content, right_panel = st.columns([2, 1])
    
    # Main content
    with main_content:
        row1 = st.container()
        with row1:
            st.header("Molecule Viewer")
            st_molstar_remote("https://files.rcsb.org/view/1LOL.cif", key='sds')
        
        row2 = st.container()
        with row2:
            st.header("Protein Data")
            render_protein_table()
    
    # Right panel
    with right_panel:
        st.header("Input Elements")
        render_search_filters()
        render_input_samples()

if __name__ == "__main__":
    main()

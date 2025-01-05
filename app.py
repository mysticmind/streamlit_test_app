import streamlit as st
from ui_loader import UILoader

# Must be the first Streamlit command
st.set_page_config(layout="wide")

def init_session_state():
    """Initialize session state variables"""
    # Only initialize non-widget state variables
    if 'filters_active' not in st.session_state:
        st.session_state.filters_active = False
    if 'filters_applied' not in st.session_state:
        st.session_state.filters_applied = False
    if 'current_filters' not in st.session_state:
        st.session_state.current_filters = {}

def on_filter_apply():
    """Handle filter application"""
    # Get current display options
    display_options = {
        "show_bfactor": st.session_state.get('show_bfactor', True),
        "show_sasa": st.session_state.get('show_sasa', True),
        "show_position": st.session_state.get('show_position', True),
        "show_chain": st.session_state.get('show_chain', True)
    }
    
    # Update current filters in session state
    current_filters = {
        "residue_search": st.session_state.get('residue_search', ''),
        "chain_filter": st.session_state.get('chain_filter', ['A']),
        "b_factor_range": st.session_state.get('b_factor_range', [20, 80]),
        "sec_structure": st.session_state.get('sec_structure', []),
        "sasa_threshold": st.session_state.get('sasa_threshold', 50),
        "display_options": display_options
    }
    
    st.session_state.current_filters = current_filters
    st.session_state.filters_active = True
    st.session_state.filters_applied = True
    
    # Show dialog with current filters
    dialog = ui_loader.component_registry['dialog']
    dialog.show('filter_dialog', {'title': 'Current Filters', 'content': current_filters})

def main():
    init_session_state()
    
    # Add an anchor at the top
    st.markdown('<div id="top"></div>', unsafe_allow_html=True)
    
    # Create UI loader
    global ui_loader
    ui_loader = UILoader('ui_config.json')
    
    # Register action handlers
    ui_loader.register_action('on_filter_apply', on_filter_apply)
    
    # Render UI
    ui_loader.render()

if __name__ == "__main__":
    main()

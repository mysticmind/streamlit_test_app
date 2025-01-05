"""UI Components for Streamlit UI Loader."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import streamlit as st
from streamlit_molstar import st_molstar, st_molstar_rcsb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

class UIComponent(ABC):
    """Abstract base class for UI components."""
    
    @abstractmethod
    def render(self, config: Dict[str, Any]) -> Any:
        """Render the component based on configuration."""
        pass
    
    def _get_session_value(self, key: str, default: Any) -> Any:
        """Get value from session state with fallback to default."""
        if key not in st.session_state:
            st.session_state[key] = default
        return st.session_state[key]

class TextInput(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        key = config['key']
        default = config.get('default', '')
        
        # Initialize session state if needed
        self._get_session_value(key, default)
        
        return st.text_input(
            label=config['label'],
            key=key,
            placeholder=config.get('placeholder', ''),
            value=self._get_session_value(key, default)
        )

class TextArea(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        key = config['key']
        default = config.get('default', '')
        
        # Initialize session state if needed
        self._get_session_value(key, default)
        
        return st.text_area(
            label=config['label'],
            key=key,
            value=self._get_session_value(key, default)
        )

class MultiSelect(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        key = config['key']
        default = config.get('default', [])
        
        # Initialize session state if needed
        self._get_session_value(key, default)
        
        return st.multiselect(
            label=config['label'],
            options=config['options'],
            key=key,
            default=self._get_session_value(key, default)
        )

class Select(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        key = config['key']
        default = config.get('default', config['options'][0])
        
        # Initialize session state if needed
        self._get_session_value(key, default)
        
        return st.selectbox(
            label=config['label'],
            options=config['options'],
            key=key,
            index=config['options'].index(self._get_session_value(key, default))
        )

class Slider(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        key = config['key']
        default = config.get('value', [config['min'], config['max']])
        
        # Initialize session state if needed
        self._get_session_value(key, default)
        
        return st.slider(
            label=config['label'],
            min_value=config['min'],
            max_value=config['max'],
            key=key,
            value=self._get_session_value(key, default)
        )

class NumberInput(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        key = config['key']
        default = config.get('value', 0)
        
        # Initialize session state if needed
        self._get_session_value(key, default)
        
        return st.number_input(
            label=config['label'],
            min_value=config.get('min', 0),
            max_value=config.get('max', 100),
            key=key,
            value=self._get_session_value(key, default)
        )

class Checkbox(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        key = config['key']
        default = config.get('default', False)
        
        # Initialize session state if needed
        self._get_session_value(key, default)
        
        return st.checkbox(
            label=config['label'],
            key=key,
            value=self._get_session_value(key, default)
        )

class CheckboxGroup(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        st.write(config['label'])
        results = []
        for item in config['items']:
            key = item['key']
            default = item.get('default', False)
            
            # Initialize session state if needed
            self._get_session_value(key, default)
            
            result = st.checkbox(
                label=item['label'],
                key=key,
                value=self._get_session_value(key, default)
            )
            results.append(result)
        return results

class Button(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        """Render a button with callback."""
        key = config['key']
        label = config.get('label', '')
        
        # Handle callback through session state
        if 'action' in config:
            action_key = f"action_{config['action']}"
            button_key = f"{key}_{config['action']}"
            if action_key in st.session_state:
                if st.button(label=label, key=button_key):
                    st.session_state[action_key]()
                    return True
            else:
                return st.button(label=label, key=button_key)
        else:
            # Default button without callback
            return st.button(label=label, key=key)

class JsonView(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        data_key = config.get('data_key')
        if data_key and data_key in st.session_state:
            data = st.session_state[data_key]
        else:
            data = config.get('default', {})
            if data_key:
                st.session_state[data_key] = data
        
        st.json(data)
        
        if st.session_state.get('filters_applied', False):
            st.success("Filters applied successfully!")
            st.session_state.filters_applied = False
        return data

class FileUploader(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        return st.file_uploader(
            label=config['label'],
            key=config['key'],
            type=config.get('accept_types'),
            on_change=config.get('on_change')
        )

class Text(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        if config.get('style') == 'info':
            return st.info(config['content'])
        else:
            return st.text(config['content'])

class MolstarViewer(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        if 'sample_data' in config:
            sample = config['sample_data']
            if sample['type'] == 'rcsb':
                return st_molstar_rcsb(sample['pdb_id'], height=config.get('height', 400))
        elif 'file_uploader' in st.session_state and st.session_state.file_uploader is not None:
            return st_molstar(st.session_state.file_uploader, height=config.get('height', 400))
        return None

class Expander(UIComponent):
    def __init__(self, component_registry: Dict[str, UIComponent]):
        self.component_registry = component_registry
        
    def render(self, config: Dict[str, Any]) -> Any:
        with st.expander(label=config['label'], expanded=config.get('expanded', False)):
            results = []
            for child in config.get('components', []):
                component = self.component_registry.get(child['type'])
                if component:
                    result = component.render(child)
                    results.append(result)
            return results

class Tabs(UIComponent):
    def __init__(self, component_registry: Dict[str, UIComponent]):
        self.component_registry = component_registry
        
    def render(self, config: Dict[str, Any]) -> Any:
        tabs = st.tabs([tab['label'] for tab in config['tabs']])
        results = []
        for tab, tab_config in zip(tabs, config['tabs']):
            with tab:
                tab_results = []
                for component in tab_config.get('components', []):
                    comp = self.component_registry.get(component['type'])
                    if comp:
                        result = comp.render(component)
                        tab_results.append(result)
                results.append(tab_results)
        return results

class DataTable(UIComponent):
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample protein data."""
        n_rows = 100
        data = {
            'Chain': np.random.choice(['A', 'B', 'C'], n_rows),
            'Residue': np.random.choice(['ALA', 'GLY', 'SER', 'THR', 'VAL'], n_rows),
            'Position': range(1, n_rows + 1),
            'B-Factor': np.random.uniform(20, 80, n_rows).round(2),
            'SASA': np.random.uniform(0, 100, n_rows).round(2)
        }
        return pd.DataFrame(data)

    def _style_dataframe(self, df: pd.DataFrame, view_mode: str) -> pd.DataFrame:
        """Apply styling based on view mode."""
        if view_mode == 'Detailed':
            def highlight_high_values(val, threshold):
                if isinstance(val, (int, float)):
                    return 'color: red' if val > threshold else 'color: black'
                return 'color: black'
            
            return df.style.applymap(lambda x: highlight_high_values(x, 60), subset=['B-Factor'])\
                         .applymap(lambda x: highlight_high_values(x, 80), subset=['SASA'])
        return df

    def render(self, config: Dict[str, Any]) -> Any:
        if 'data' in config:
            if config['data'].get('sample_data'):
                df = self._generate_sample_data()
            else:
                df = pd.DataFrame(config['data'])
            
            view_mode = st.session_state.get('table_view_mode', 'Simple')
            styled_df = self._style_dataframe(df, view_mode)
            return st.dataframe(styled_df, use_container_width=True)
        elif hasattr(st.session_state, 'protein_data'):
            return st.dataframe(st.session_state.protein_data)
        return None

class Plot(UIComponent):
    def _generate_plot_data(self, plot_type: str) -> pd.DataFrame:
        """Generate sample data for different plot types."""
        if plot_type == 'ramachandran':
            n_points = 1000
            phi = np.random.normal(-60, 30, n_points)
            psi = np.random.normal(-45, 30, n_points)
            return pd.DataFrame({'phi': phi, 'psi': psi})
            
        elif plot_type == 'secondary_structure':
            structures = ['α-Helix', 'β-Sheet', 'Loops', '310-Helix', 'β-Turn']
            percentages = [45, 32, 23, 5, 4]
            return pd.DataFrame({'Structure': structures, 'Percentage': percentages})
            
        elif plot_type == 'bfactor_distribution':
            residues = range(1, 201)
            bfactors = np.random.normal(50, 15, 200)
            bfactors = np.convolve(bfactors, np.ones(5)/5, mode='same')
            return pd.DataFrame({'Residue': residues, 'B-factor': bfactors})
            
        elif plot_type == 'hydropathy':
            residues = range(1, 201)
            hydropathy = np.sin(np.array(residues)/10) * 2 + np.random.normal(0, 0.5, 200)
            return pd.DataFrame({'Residue': residues, 'Hydropathy': hydropathy})
            
        elif plot_type == 'aa_composition':
            aa_list = ['ALA', 'CYS', 'ASP', 'GLU', 'PHE', 'GLY', 'HIS', 'ILE', 'LYS', 'LEU']
            counts = np.random.randint(5, 25, len(aa_list))
            return pd.DataFrame({'Amino Acid': aa_list, 'Count': counts})
            
        return pd.DataFrame()

    def render(self, config: Dict[str, Any]) -> Any:
        plot_type = config['plot_type']
        data_type = config['data']['type']
        
        df = self._generate_plot_data(data_type)
        
        if data_type == 'ramachandran':
            fig = px.scatter(df, x='phi', y='psi', 
                           title='Ramachandran Plot',
                           labels={'phi': 'Phi (°)', 'psi': 'Psi (°)'})
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.add_vline(x=0, line_dash="dash", line_color="gray")
            
        elif data_type == 'secondary_structure':
            fig = px.bar(df, x='Structure', y='Percentage',
                        title='Secondary Structure Distribution')
            
        elif data_type == 'bfactor_distribution':
            fig = px.line(df, x='Residue', y='B-factor',
                         title='B-factor Distribution')
            
        elif data_type == 'hydropathy':
            fig = px.line(df, x='Residue', y='Hydropathy',
                         title='Hydropathy Plot')
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
        elif data_type == 'aa_composition':
            fig = px.bar(df, x='Amino Acid', y='Count',
                        title='Amino Acid Composition')
        else:
            return None
            
        return st.plotly_chart(fig, use_container_width=True)

class Dialog(UIComponent):
    def render(self, config: Dict[str, Any]) -> Any:
        """Render a dialog with content."""
        key = config['key']
        show_key = f"{key}_show"
        content_key = f"{key}_content"
        
        # Initialize dialog state if needed
        if show_key not in st.session_state:
            st.session_state[show_key] = False
        if content_key not in st.session_state:
            st.session_state[content_key] = None
        
        if st.session_state[show_key]:
            # Create a container for the popup
            popup = st.empty()
            
            # Build popup content
            with st.container():
                st.markdown("---")
                st.subheader(config.get('title', ''))
                
                # Handle different content types
                content = st.session_state[content_key]
                if isinstance(content, dict):
                    st.json(content)
                else:
                    st.write(content)
                
                if st.button("Close", key=f"{key}_close", type="primary"):
                    st.session_state[show_key] = False
                    st.rerun()
                st.markdown("---")
    
    def show(self, key: str, content: Any = None):
        """Show the dialog with the given key and content."""
        show_key = f"{key}_show"
        content_key = f"{key}_content"
        st.session_state[show_key] = True
        if content is not None:
            st.session_state[content_key] = content

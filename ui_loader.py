import json
from typing import Any, Dict, Optional, Callable
import streamlit as st
from ui_components import (
    UIComponent, TextInput, MultiSelect, Slider, NumberInput,
    CheckboxGroup, Button, JsonView, Expander, Tabs,
    FileUploader, TextArea, Select, Checkbox, Text,
    MolstarViewer, DataTable, Plot, Dialog
)

class UILoader:
    """UI Loader that uses a component registry to render UI elements."""
    
    def __init__(self, config_path: str):
        """Initialize UI Loader with configuration path."""
        
        # Initialize component registry first
        self.component_registry = {
            'text_input': TextInput(),
            'multiselect': MultiSelect(),
            'slider': Slider(),
            'number_input': NumberInput(),
            'checkboxes': CheckboxGroup(),
            'button': Button(),
            'json_view': JsonView(),
            'file_uploader': FileUploader(),
            'text_area': TextArea(),
            'select': Select(),
            'checkbox': Checkbox(),
            'text': Text(),
            'molstar_viewer': MolstarViewer(),
            'data_table': DataTable(),
            'plot': Plot(),
            'dialog': Dialog(),
        }
        
        # Add components that need registry access
        self.component_registry.update({
            'expander': Expander(self.component_registry),
            'tabs': Tabs(self.component_registry),
        })
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def register_action(self, action_name: str, handler: Callable) -> None:
        """Register an action handler for buttons."""
        action_key = f"action_{action_name}"
        st.session_state[action_key] = handler
    
    def render(self) -> None:
        """Render the UI based on configuration."""
        # Only render title if it exists in config
        if self.config.get('title'):
            st.title(self.config['title'])
            
        # Render sidebar components
        if self.config['layout'].get('sidebar', {}).get('components'):
            with st.sidebar:
                for component in self.config['layout']['sidebar']['components']:
                    self.render_component(component)
        
        # Render main components
        if self.config['layout'].get('main', {}).get('components'):
            for component in self.config['layout']['main']['components']:
                self.render_component(component)
    
    def render_component(self, component_config: Dict[str, Any]) -> Optional[Any]:
        """Render a single component using the component registry."""
        component_type = component_config['type']
        component = self.component_registry.get(component_type)
        
        if component:
            return component.render(component_config)
        else:
            st.warning(f"Unknown component type: {component_type}")
            return None

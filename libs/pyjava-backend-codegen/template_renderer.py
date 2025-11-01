"""
Template rendering engine using Mustache templates.
"""
import pystache
from pathlib import Path
from typing import Dict, Any


class TemplateRenderer:
    """Handles Mustache template rendering with context data."""
    
    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render Mustache template with given context.
        
        Args:
            template_name: Name of the template file
            context: Dictionary containing template variables
            
        Returns:
            Rendered template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Render with HTML escaping disabled
        renderer = pystache.Renderer(escape=lambda u: u)
        rendered = renderer.render(template_content, context)
        
        # Fix HTML entities
        rendered = rendered.replace('&quot;', '"')
        rendered = rendered.replace('&lt;', '<')
        rendered = rendered.replace('&gt;', '>')
        rendered = rendered.replace('&amp;', '&')
        
        return rendered
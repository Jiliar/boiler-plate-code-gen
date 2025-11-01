"""
PyJava Backend Code Generator

A Python library for generating Java Spring Boot applications following 
Hexagonal Architecture principles from Smithy service definitions.
"""

from .config_loader import ConfigLoader
from .openapi_processor import OpenApiProcessor
from .template_renderer import TemplateRenderer
from .code_generator import CodeGenerator
from .file_manager import FileManager

__version__ = "1.0.0"
__author__ = "Jiliar Silgado"

__all__ = [
    "ConfigLoader",
    "OpenApiProcessor", 
    "TemplateRenderer",
    "CodeGenerator",
    "FileManager"
]
#!/usr/bin/env python3
"""
Hexagonal Architecture Spring Boot Code Generator v2

Updated version using the pyjava-backend-codegen library.
This script serves as a bridge to the new modular architecture.
"""

import sys
import subprocess
import shutil
from pathlib import Path

# Add the library to the Python path
lib_path = Path(__file__).parent / "pyjava-backend-codegen"
sys.path.insert(0, str(lib_path))

# Import components directly
from config_loader import ConfigLoader
from code_generator import CodeGenerator


def run_command(cmd: str) -> str:
    """Execute a shell command and return its output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    return result.stdout


def main():
    """Main entry point for the generator."""
    print("📝 Generating OpenAPI from Smithy...")
    run_command("smithy clean")
    run_command("smithy build")
    
    # Clean and create projects directory
    projects_dir = Path("projects")
    if projects_dir.exists():
        shutil.rmtree(projects_dir)
        print("🗑️ Cleaned existing projects directory")
    projects_dir.mkdir(exist_ok=True)
    print("📁 Created projects directory")

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python hexagonal-architecture-generator-v2.py [templates_dir]")
        print("Example: python hexagonal-architecture-generator-v2.py templates/java")
        print("Config: libs/config/params.json (array of project configurations)")
        sys.exit(0)
    
    config_path = "libs/config/params.json"
    templates_dir = sys.argv[1] if len(sys.argv) > 1 else "templates/java"
    
    try:
        # Load all project configurations
        projects_config = ConfigLoader.load_projects_config(config_path)
        
        print(f"Found {len(projects_config)} project(s) to generate...")
        
        # Generate each project
        for i, project_config in enumerate(projects_config, 1):
            project_name = project_config['project']['general']['name']
            print(f"\n[{i}/{len(projects_config)}] Generating project: {project_name}")
            
            generator = CodeGenerator(config_path, templates_dir, project_config)
            generator.generate_complete_project()
            
        print(f"\n✅ Successfully generated {len(projects_config)} project(s)!")
        
    except Exception as e:
        print(f"Error generating projects: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
"""
Main entry point for the PyJava Backend Code Generator.
"""
import sys
import subprocess
import shutil
from pathlib import Path

from .config_loader import ConfigLoader
from .code_generator import CodeGenerator


def run_command(cmd: str) -> str:
    """
    Execute a shell command and return its output.
    
    Args:
        cmd: Shell command to execute
        
    Returns:
        Command output as string
        
    Raises:
        SystemExit: If command fails
    """
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        exit(1)
    return result.stdout


def main():
    """
    Main entry point for the generator.
    
    Handles command line arguments, loads configuration, and orchestrates
    the project generation process for multiple projects.
    """
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
        print("Usage: python -m pyjava-backend-codegen [templates_dir]")
        print("Example: python -m pyjava-backend-codegen templates/java")
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
            
            generator = CodeGenerator(templates_dir, project_config)
            generator.generate_complete_project()
            
        print(f"\n✅ Successfully generated {len(projects_config)} project(s)!")
        
    except Exception as e:
        print(f"Error generating projects: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
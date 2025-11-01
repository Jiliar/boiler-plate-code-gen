#!/bin/bash

# Hexagonal Architecture Spring Boot Generator Runner v2
# This script runs the new modular Python generator

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define paths
CONFIG_PATH="$PROJECT_ROOT/libs/config/params.json"
TEMPLATES_DIR="$PROJECT_ROOT/libs/pyjava-backend-codegen/templates"

# Get first project name from params.json array
if [ -f "$PROJECT_ROOT/libs/config/params.json" ]; then
    PROJECT_NAME=$(python3 -c "import json; config=json.load(open('$PROJECT_ROOT/libs/config/params.json')); print(config[0]['project']['general']['name'] if config else 'generated-project')")
else
    PROJECT_NAME="generated-project"
fi

OUTPUT_DIR="$PROJECT_ROOT"

echo "🚀 Starting Hexagonal Architecture Spring Boot Generator v2"
echo "📋 Projects: Multiple projects from config array"
echo "⚙️  Config: $CONFIG_PATH"
echo "📁 Templates: $TEMPLATES_DIR"
echo "📂 Output: $OUTPUT_DIR"
echo ""

# Check if Python 3 is available
echo "🔍 Checking Python 3 availability..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi
echo "✅ Python 3 found"

# Install pystache if not available
echo "📦 Checking dependencies..."
if ! python3 -c "import pystache" 2>/dev/null; then
    echo "📥 Installing pystache..."
    pip3 install pystache
    echo "✅ Pystache installed"
else
    echo "✅ Dependencies satisfied"
fi

# Remove existing projects if they exist
echo "🗑️  Cleaning up existing projects..."
if [ -d "$PROJECT_ROOT/projects" ]; then
    rm -rf "$PROJECT_ROOT/projects"
fi
echo "✅ Cleanup complete"

echo ""
echo "🏗️  Generating Hexagonal Architecture project with v2 library..."
echo ""

# Run the new modular generator
python3 "$PROJECT_ROOT/libs/hexagonal-architecture-generator-v2.py" "$TEMPLATES_DIR"

echo ""
echo "🎉 Generation complete! Check the generated projects in the project root"
echo "🚀 Ready to run: cd [project-name] && mvn spring-boot:run"
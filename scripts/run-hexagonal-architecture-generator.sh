#!/bin/bash

# Hexagonal Architecture Spring Boot Generator Runner
# This script runs the Python generator with the correct paths

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Define paths
CONFIG_PATH="$PROJECT_ROOT/templates/java/template-config.json"
TEMPLATES_DIR="$PROJECT_ROOT/templates/java"
OUTPUT_DIR="$PROJECT_ROOT/generated-project"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Install pystache if not available
if ! python3 -c "import pystache" 2>/dev/null; then
    echo "Installing pystache..."
    pip3 install pystache
fi

# Remove existing project if it exists
if [ -d "$OUTPUT_DIR" ]; then
    echo "Removing existing project at: $OUTPUT_DIR"
    rm -rf "$OUTPUT_DIR"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Starting Hexagonal Architecture code generation..."
echo "Config: $CONFIG_PATH"
echo "Templates: $TEMPLATES_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Run the generator
python3 "$SCRIPT_DIR/hexagonal-architecture-generator.py" "$CONFIG_PATH" "$TEMPLATES_DIR" "$OUTPUT_DIR"

echo ""
echo "Generation complete! Check the generated project at: $OUTPUT_DIR"
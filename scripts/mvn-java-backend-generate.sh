#!/bin/bash

# chmod +x scripts/mvn-backend-generate.sh
# bash scripts/mvn-backend-generate.sh

echo "🚀 Generating User Service API..."

# Clean previous generations
rm -rf build/
rm -rf target/generated-sources/

# Build Smithy models
echo "📝 Generating OpenAPI from Smithy..."
smithy build

# Generate Spring Boot code
echo "🔄 Generating Spring Boot code from OpenAPI..."
mvn clean install

# Check if any .json file was generated in the OpenAPI output directory
if ! ls build/smithy/user_service/openapi/*.json 1> /dev/null 2>&1; then
    echo "❌ No .json OpenAPI files found in build/smithy/user_service/openapi!"
    exit 1
fi

echo "✅ Generation completed!"
echo "📁 Generated files in: target/generated-sources/openapi/"

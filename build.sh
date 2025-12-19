#!/bin/bash

echo "🔨 Building Docker images for Kubernetes Data Pipeline..."

# Build data-generator
echo "Building data-generator..."
docker build -t data-generator:latest ./data-generator
if [ $? -ne 0 ]; then
    echo "❌ Failed to build data-generator"
    exit 1
fi

# Build data-processor
echo "Building data-processor..."
docker build -t data-processor:latest ./data-processor
if [ $? -ne 0 ]; then
    echo "❌ Failed to build data-processor"
    exit 1
fi

# Build data-aggregator
echo "Building data-aggregator..."
docker build -t data-aggregator:latest ./data-aggregator
if [ $? -ne 0 ]; then
    echo "❌ Failed to build data-aggregator"
    exit 1
fi

echo "✅ All images built successfully!"
echo ""
echo "Built images:"
docker images | grep -E "data-generator|data-processor|data-aggregator"

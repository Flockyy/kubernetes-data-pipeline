#!/bin/bash

# Local Development Setup Script using uv
# This script sets up Python environments for local development

set -e

echo "🚀 Setting up local development environment with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✅ uv is installed: $(uv --version)"

# Setup data-generator
echo ""
echo "📊 Setting up data-generator..."
cd data-generator
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
deactivate
cd ..

# Setup data-processor
echo ""
echo "⚙️  Setting up data-processor..."
cd data-processor
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
deactivate
cd ..

# Setup data-aggregator
echo ""
echo "📈 Setting up data-aggregator..."
cd data-aggregator
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
deactivate
cd ..

echo ""
echo "✨ Local development setup complete!"
echo ""
echo "To activate each environment:"
echo "  cd data-generator && source .venv/bin/activate"
echo "  cd data-processor && source .venv/bin/activate"
echo "  cd data-aggregator && source .venv/bin/activate"
echo ""
echo "To run services locally:"
echo "  # Terminal 1 - Processor (needs to run first)"
echo "  cd data-processor && source .venv/bin/activate && python app.py"
echo ""
echo "  # Terminal 2 - Aggregator"
echo "  cd data-aggregator && source .venv/bin/activate && python app.py"
echo ""
echo "  # Terminal 3 - Generator"
echo "  cd data-generator && source .venv/bin/activate && python app.py"

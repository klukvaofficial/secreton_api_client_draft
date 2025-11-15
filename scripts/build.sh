#!/bin/bash
# Build Docusaurus documentation for production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBSITE_DIR="$PROJECT_ROOT/website"

cd "$PROJECT_ROOT"

# Generate API documentation
echo "Generating API documentation..."
python scripts/generate_api_docs.py

cd "$WEBSITE_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Docusaurus dependencies..."
    npm install
fi

# Build documentation
echo "Building Docusaurus site..."
npm run build

echo "✓ Build complete! Output is in $WEBSITE_DIR/build"


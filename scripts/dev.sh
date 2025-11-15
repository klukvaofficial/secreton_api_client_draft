#!/bin/bash
# Start Docusaurus development server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBSITE_DIR="$PROJECT_ROOT/website"

cd "$WEBSITE_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Docusaurus dependencies..."
    npm install
fi

# Generate API docs if needed
if [ ! -f "$WEBSITE_DIR/docs/api-reference/client.md" ] || [ "$1" == "--regenerate-api" ]; then
    echo "Generating API documentation..."
    cd "$PROJECT_ROOT"
    python scripts/generate_api_docs.py
    cd "$WEBSITE_DIR"
fi

echo "Starting Docusaurus development server..."
npm start


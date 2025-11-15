#!/bin/bash
# Generate API documentation only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "Generating API documentation..."
python scripts/generate_api_docs.py

echo "✓ API documentation generated!"


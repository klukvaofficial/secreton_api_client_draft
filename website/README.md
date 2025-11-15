# SecretOn API Client Documentation

This directory contains the Docusaurus documentation site for the SecretOn API Client Python library.

## Overview

The documentation is built using [Docusaurus](https://docusaurus.io/), a modern static website generator. It includes:

- Getting started guides
- API reference documentation (auto-generated from Python docstrings)
- Code examples
- User guides

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+ (for API doc generation)
- **Documentation dependencies** (install with `pip install -e ".[docs]"` or `uv sync --group docs`)

## Local Development

### Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Generate API documentation:**
   ```bash
   # From project root
   python scripts/generate_api_docs.py
   ```

3. **Start development server:**
   ```bash
   npm start
   ```

   The site will be available at `http://localhost:3000`

### Using Helper Scripts

From the project root, you can use the provided scripts:

```bash
# Start development server (auto-generates API docs if needed)
./scripts/dev.sh

# Build documentation for production
./scripts/build.sh

# Generate API documentation only
./scripts/generate-api-docs.sh
```

## Project Structure

```
website/
├── docs/                    # Documentation markdown files
│   ├── getting-started/     # Getting started guides
│   ├── examples/            # Code examples
│   ├── api-reference/       # API reference (auto-generated)
│   └── user-guide/          # User guides
├── src/
│   ├── css/                 # Custom CSS
│   ├── components/          # React components
│   └── pages/               # Custom pages
├── static/                  # Static assets
├── docusaurus.config.js    # Docusaurus configuration
├── sidebars.js              # Sidebar navigation
└── package.json             # Node.js dependencies
```

## Building for Production

```bash
npm run build
```

The built site will be in the `build/` directory.

## API Documentation Generation

API documentation is automatically generated from Python docstrings using `mkdocstrings`. The generation script (`scripts/generate_api_docs.py`) extracts documentation for:

- Client classes (`SyncSecretOnClient`, `AsyncSecretOnClient`)
- Service classes (`AuthService`, `OrdersService`, `ProfileService`)
- Data models (authentication, orders, profile models)
- Exception classes

To regenerate API docs:

```bash
python scripts/generate_api_docs.py
```

## Deployment

The documentation is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the `main` branch. The workflow:

1. Generates API documentation from Python docstrings
2. Builds the Docusaurus site
3. Deploys to GitHub Pages

## Configuration

### Site Configuration

Edit `docusaurus.config.js` to customize:
- Site title, tagline, and URLs
- Theme colors and appearance
- Navigation bar and footer
- Search configuration

### Sidebar Navigation

Edit `sidebars.js` to customize the documentation sidebar structure.

## Troubleshooting

### API docs not generating

- Ensure the project is installed: `pip install -e .` (or `uv sync`)
- Check that Python source files are accessible from the script
- Verify docstrings are present in the source code
- The script uses Python's built-in `inspect` module, so no extra dependencies are needed

### Build errors

- Clear Docusaurus cache: `npm run clear`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

### Development server not starting

- Check if port 3000 is already in use
- Verify all dependencies are installed: `npm install`
- Check for syntax errors in `docusaurus.config.js`

## Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [Docusaurus API Reference](https://docusaurus.io/docs/api/docusaurus-config)
- [MDX Documentation](https://mdxjs.com/)


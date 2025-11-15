#!/usr/bin/env python3
"""Generate API documentation from Python docstrings for Docusaurus.

This script uses Python's inspect module to extract docstrings and generate
markdown files compatible with Docusaurus.
"""

import inspect
import sys
from pathlib import Path
from typing import Any, get_type_hints

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def format_docstring(doc: str) -> str:
    """Format docstring for markdown."""
    if not doc:
        return ""
    # Clean up docstring indentation
    lines = doc.split("\n")
    if len(lines) > 1:
        # Remove common leading whitespace
        min_indent = min(
            len(line) - len(line.lstrip())
            for line in lines[1:]
            if line.strip()
        )
        if min_indent > 0:
            lines = [lines[0]] + [line[min_indent:] if line.strip() else line for line in lines[1:]]
    return "\n".join(lines).strip()


def format_signature(func: Any) -> str:
    """Format function signature."""
    try:
        sig = inspect.signature(func)
        return str(sig)
    except (ValueError, TypeError):
        return "()"


def format_type_hint(obj: Any, name: str) -> str:
    """Get type hint for an object."""
    try:
        hints = get_type_hints(obj)
        return hints.get(name, "")
    except Exception:
        return ""


def generate_class_docs(cls: type, class_name: str) -> str:
    """Generate markdown documentation for a class."""
    content = f"### {class_name}\n\n"
    
    # Class docstring
    doc = inspect.getdoc(cls)
    if doc:
        content += f"{format_docstring(doc)}\n\n"
    
    # Class signature
    try:
        sig = inspect.signature(cls.__init__)
        params = list(sig.parameters.values())[1:]  # Skip 'self'
        if params:
            content += "**Parameters:**\n\n"
            for param in params:
                param_type = ""
                if param.annotation != inspect.Parameter.empty:
                    param_type = f"`{param.annotation}`" if hasattr(param.annotation, '__name__') else str(param.annotation)
                
                param_desc = ""
                if param.default != inspect.Parameter.empty:
                    default_str = f" (default: `{param.default}`)"
                else:
                    default_str = ""
                
                if param_type:
                    content += f"- `{param.name}` ({param_type}){default_str}: {param_desc}\n"
                else:
                    content += f"- `{param.name}`{default_str}: {param_desc}\n"
            content += "\n"
    except (ValueError, TypeError):
        pass
    
    # Methods
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith("_") or name in ("__init__", "__enter__", "__exit__"):
            methods.append((name, method))
    
    for name, method in inspect.getmembers(cls, predicate=inspect.ismethod):
        if not name.startswith("_"):
            methods.append((name, method))
    
    if methods:
        content += "**Methods:**\n\n"
        for name, method in sorted(set(methods)):
            method_doc = inspect.getdoc(method) or ""
            first_line = method_doc.split("\n")[0] if method_doc else "No description"
            sig = format_signature(method)
            content += f"- `{name}{sig}`: {first_line}\n"
        content += "\n"
    
    # Properties/Attributes
    attrs = []
    for name in dir(cls):
        if not name.startswith("_"):
            obj = getattr(cls, name)
            if isinstance(obj, property) or (not callable(obj) and not inspect.isclass(obj)):
                attrs.append(name)
    
    if attrs:
        content += "**Attributes:**\n\n"
        for attr_name in sorted(attrs):
            try:
                attr_obj = getattr(cls, attr_name)
                attr_type = type(attr_obj).__name__ if not callable(attr_obj) else ""
                content += f"- `{attr_name}`: {attr_type}\n"
            except Exception:
                content += f"- `{attr_name}`\n"
        content += "\n"
    
    return content


def generate_client_docs(output_path: Path):
    """Generate documentation for client classes."""
    content = """# Client Classes

## SyncSecretOnClient

"""
    
    try:
        from secreton_api_client.client import SyncSecretOnClient
        content += generate_class_docs(SyncSecretOnClient, "SyncSecretOnClient")
    except Exception as e:
        content += f"Error generating docs: {e}\n"
    
    content += "\n\n## AsyncSecretOnClient\n\n"
    
    try:
        from secreton_api_client.client import AsyncSecretOnClient
        content += generate_class_docs(AsyncSecretOnClient, "AsyncSecretOnClient")
    except Exception as e:
        content += f"Error generating docs: {e}\n"
    
    output_path.write_text(content, encoding="utf-8")
    print(f"✓ Generated {output_path}")


def generate_services_docs(output_path: Path):
    """Generate documentation for service classes."""
    content = """# Services

"""
    
    # Authentication Service
    content += "## Authentication Service\n\n"
    try:
        from secreton_api_client.services.auth import AuthService
        content += generate_class_docs(AuthService, "AuthService")
    except Exception as e:
        content += f"Error generating docs: {e}\n"
    
    # Orders Service
    content += "\n\n## Orders Service\n\n"
    try:
        from secreton_api_client.services.orders import OrdersService
        content += generate_class_docs(OrdersService, "OrdersService")
    except Exception as e:
        content += f"Error generating docs: {e}\n"
    
    # Profile Service
    content += "\n\n## Profile Service\n\n"
    try:
        from secreton_api_client.services.profile import ProfileService
        content += generate_class_docs(ProfileService, "ProfileService")
    except Exception as e:
        content += f"Error generating docs: {e}\n"
    
    output_path.write_text(content, encoding="utf-8")
    print(f"✓ Generated {output_path}")


def generate_models_docs(output_path: Path):
    """Generate documentation for model classes."""
    content = """# Data Models

## Authentication Models

"""
    
    # Auth models
    try:
        from secreton_api_client.models.auth import LoginResponse, RegisterResponse
        content += generate_class_docs(LoginResponse, "LoginResponse")
        content += "\n\n"
        content += generate_class_docs(RegisterResponse, "RegisterResponse")
    except Exception as e:
        content += f"Error generating docs: {e}\n"
    
    content += "\n\n## Order Models\n\n"
    
    # Order models
    try:
        from secreton_api_client.models.orders import (
            OrderCommentModel,
            OrderTagModel,
            OrderViewModel,
        )
        for model_class in [OrderCommentModel, OrderTagModel, OrderViewModel]:
            content += generate_class_docs(model_class, model_class.__name__)
            content += "\n\n"
    except Exception as e:
        content += f"Error generating docs: {e}\n"
    
    content += "\n\n## Profile Models\n\n"
    
    # Profile models
    try:
        from secreton_api_client.models.profile import UserProfile
        content += generate_class_docs(UserProfile, "UserProfile")
    except Exception as e:
        content += f"Error generating docs: {e}\n"
    
    output_path.write_text(content, encoding="utf-8")
    print(f"✓ Generated {output_path}")


def generate_exceptions_docs(output_path: Path):
    """Generate documentation for exception classes."""
    content = """# Exceptions

"""
    
    exceptions = [
        ("APIClientError", "secreton_api_client.exceptions"),
        ("AuthenticationError", "secreton_api_client.exceptions"),
        ("ValidationError", "secreton_api_client.exceptions"),
        ("FileError", "secreton_api_client.exceptions"),
        ("NotFoundError", "secreton_api_client.exceptions"),
        ("ServerError", "secreton_api_client.exceptions"),
        ("HTTPError", "secreton_api_client.exceptions"),
        ("RateLimitError", "secreton_api_client.exceptions"),
    ]
    
    for exc_name, module_name in exceptions:
        try:
            module = __import__(module_name, fromlist=[exc_name])
            exc_class = getattr(module, exc_name)
            content += generate_class_docs(exc_class, exc_name)
            content += "\n\n"
        except Exception as e:
            content += f"### {exc_name}\n\nError generating docs: {e}\n\n"
    
    output_path.write_text(content, encoding="utf-8")
    print(f"✓ Generated {output_path}")


def main():
    """Main entry point."""
    # Set output directory
    website_dir = project_root / "website"
    docs_dir = website_dir / "docs" / "api-reference"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating API documentation...")
    print(f"Output directory: {docs_dir}")
    
    # Generate documentation files
    generate_client_docs(docs_dir / "client.md")
    generate_services_docs(docs_dir / "services.md")
    generate_models_docs(docs_dir / "models.md")
    generate_exceptions_docs(docs_dir / "exceptions.md")
    
    print("\n✓ API documentation generation complete!")


if __name__ == "__main__":
    main()

# Contributing to PDF Searcher

Thank you for your interest in contributing to PDF Searcher! This document provides guidelines and instructions for contributing.

## Getting Started

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/PDF_Searcher.git
cd PDF_Searcher
```

2. **Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install system dependencies**

**Ubuntu/Debian:**
```bash
sudo apt-get install mupdf-tools python3-tk
```

**macOS:**
```bash
brew install mupdf
```

4. **Install Python dependencies** (if any)
```bash
pip install -r requirements.txt
```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow PEP 8 style guide
- Add docstrings to functions
- Use type hints where applicable
- Keep functions focused and testable

### 3. Test Your Changes
```bash
# Verify syntax
python3 -m py_compile pdf_searcher.py

# Run the application
python3 pdf_searcher.py

# Check all modules compile
python3 -m py_compile src/*.py
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "Add: Brief description of changes"
```

Use conventional commit prefixes:
- `Add:` for new features
- `Fix:` for bug fixes
- `Improve:` for improvements
- `Docs:` for documentation
- `Refactor:` for code refactoring
- `Test:` for testing

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Reason for the changes
- Any testing performed

## Code Style

### Standards
- **Python Version**: 3.7+
- **Style Guide**: PEP 8
- **Documentation**: Docstrings for all functions

### Example Function
```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: Description of error condition
    """
    # Implementation
    return True
```

## Architecture Guidelines

### Threading
- Use `threading.Thread` for background operations
- Always set `daemon=True` for worker threads
- Use `root.after()` for GUI updates from worker threads
- Protect global state with thread-aware design

### GUI Updates
- Never update tkinter widgets from worker threads directly
- Use `root.after(0, callback)` to schedule updates on main thread
- Keep worker threads decoupled from GUI

### Error Handling
- Use try-except blocks for system calls
- Handle missing system tools gracefully
- Provide meaningful error messages to users
- Update status bar with error information

## Testing Guidelines

### Manual Testing
1. Start application and verify GUI loads
2. Test folder browsing on your OS
3. Test all search modes: normal, regex, whole-word
4. Test case sensitivity option
5. Try searching before cache loads (auto re-search)
6. Double-click results to verify PDF opening
7. Test with PDFs in different locations

### Syntax Validation
```bash
python3 -m py_compile pdf_searcher.py src/*.py
```

### Edge Cases to Test
- Empty search term
- Invalid folder path
- Corrupted PDF file
- Missing PDF viewer
- Very large PDF files
- Very long search term
- Special regex characters

## Documentation

### When to Update Docs
- Adding new features → Update README.md
- Changing behavior → Update FEATURES.md
- New architecture → Update PROJECT_STATUS.md
- Added dependencies → Update requirements.txt

### Documentation Standards
- Use clear, concise English
- Include code examples where helpful
- Keep formatting consistent
- Add links to related sections

## Reporting Issues

### Bug Reports
Include:
1. **OS and Python version** (output of `python3 --version` and `uname`)
2. **Exact steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Error messages** or stack traces
5. **Screenshots** if applicable

### Feature Requests
Include:
1. **Motivation** - Why is this feature needed?
2. **Proposed approach** - How should it work?
3. **Examples** - How would users interact with it?
4. **Alternatives** - Other ways to solve the problem

## Review Process

All contributions go through:
1. **Syntax Check** - Code must compile without errors
2. **Style Review** - Must follow PEP 8 and documented patterns
3. **Functionality Test** - Features must work as described
4. **Documentation** - Changes must be documented

## Questions?

- Check [README.md](README.md) for usage
- See [FEATURES.md](FEATURES.md) for detailed feature docs
- Review [PROJECT_STATUS.md](PROJECT_STATUS.md) for architecture
- Open an issue for questions

## Code of Conduct

Be respectful, inclusive, and professional. We welcome contributions from everyone.

---

Thank you for contributing to PDF Searcher!

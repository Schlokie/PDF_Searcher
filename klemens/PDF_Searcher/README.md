# PDF Searcher

A cross-platform desktop tool to search for text in all PDF files within a folder, with click-to-open functionality to view matches at the specific page. Features intelligent background caching for optimized performance.

**Author**: DL1KLF  
**Date**: 2026-04-05

## Features

- **Fast Text Search**: Search across all PDFs in a folder (recursive)
- **Smart Caching**: 
  - Loads all PDF text into memory cache in the background
  - Searches are instant once cache is ready
  - Auto re-searches with cached data for better performance
  - Status bar shows "Caching files in progress..." during load
- **Advanced Search Options**:
  - Case-sensitive matching
  - Regular expression (regex) patterns
  - Whole-word matching
- **Click-to-Open**: Click any result to open the PDF at the matched page
- **Responsive UI**: GUI loads immediately while caching happens in background
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Clean UI**: Built with Python tkinter for simplicity and lightness

## System Requirements

- Python 3.7+
- System dependencies:
  - `mupdf-tools` (provides `mutool` for PDF text extraction)
  - `python3-tk` (tkinter, usually included with Python)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/PDF_Searcher.git
cd PDF_Searcher
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install system dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install mupdf-tools python3-tk
```

**macOS (with Homebrew):**
```bash
brew install mupdf
```

**Windows:**
- Download and install MuPDF from https://mupdf.com/downloads/

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Run the application
```bash
python3 pdf_searcher.py
```

Or use the shell script (Unix-like systems):
```bash
./run_pdf_searcher.sh
```

### Command-line Options

You can specify a default folder to search in via command line:

```bash
python3 pdf_searcher.py --folder /path/to/your/pdf/folder
```

Or with the shell script:
```bash
./run_pdf_searcher.sh --folder /path/to/your/pdf/folder
```

This will pre-populate the folder field and start caching PDFs from that location automatically.

### Using the GUI

1. **Select Folder**: Click "Browse" to choose the folder containing PDFs
   - Caching starts automatically in the background
   - Status bar shows progress: "Caching PDF text: X/Y"
2. **Enter Search Term**: Type your search query in the "Search Term" field
3. **Configure Search Options**:
   - Check "Case Sensitive" for exact case matching
   - Check "Regex Pattern" to use regular expression patterns
   - Check "Whole Words Only" to match complete words only
4. **Click Search**: 
   - Results appear immediately (using fallback search if cache not ready)
   - Once cache loads, search automatically re-runs with cached data for speed
5. **View Result**: Double-click any result to open the PDF at that page

### Search Result Format
Each result displays:
```
filename.pdf - Page X - [matching text snippet]
```

## Project Structure

```
PDF_Searcher/
├── pdf_searcher.py              # Main GUI entry point with tkinter
├── src/
│   ├── __init__.py
│   ├── pdf_handler.py           # PDF search and text extraction logic
│   └── utils.py                 # Cross-platform PDF opener utility
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── PROJECT_STATUS.md            # Implementation progress
├── FEATURES.md                  # Detailed feature documentation
├── run_pdf_searcher.sh          # Convenience launcher script
├── .gitignore
└── venv/                        # Virtual environment (not tracked)
```

## Technical Architecture

### PDF Text Caching (`pdf_searcher.py`)
- Loads all PDF text into memory cache on startup or folder selection
- Caching runs in a background thread to keep UI responsive
- `caching_in_progress` flag tracks cache state
- `pending_search_params` stores search parameters if user searches during caching
- Once cache completes, pending searches automatically re-run with cached data
- Subsequent searches are instant (milliseconds vs seconds)

### PDF Search (`src/pdf_handler.py`)
- Uses system `mutool` (MuPDF) for text extraction with native page tracking
- Supports regex-based search for flexible pattern matching
- Handles errors gracefully (corrupted PDFs, missing files, extraction failures)
- Returns page numbers accurately by tracking page breaks (`\f` character)

### PDF Opener (`src/utils.py`)
- Detects OS (Windows/macOS/Linux)
- Opens PDFs with system default viewer at specific page:
  - **Windows**: Uses `start` command with page parameter
  - **macOS**: Uses `open` command with page-specific URL
  - **Linux**: Uses `xdg-open` with page parameter

### GUI Layer (`pdf_searcher.py`)
- Tkinter for lightweight cross-platform desktop UI
- Background threading prevents UI freeze during searches
- Status bar provides real-time user feedback
- Double-click handler opens PDF at matched page

## Performance

- **Initial Load**: ~5 seconds for 100 PDFs (depends on file sizes and system)
- **Cache Hit Search**: ~100ms (instant to user)
- **Cache Miss Search**: ~2-5 seconds (slower, uses `mutool` each time)

### Memory Usage
- Typical: 50-100 MB for 100 PDFs
- Varies with PDF content size and compression

## Keyboard Shortcuts

- **Enter** in Search Term field: Start search
- **Double-click** result: Open PDF at page
- **Ctrl+Q** (or close button): Exit application

## Troubleshooting

### `mutool: command not found`
Install MuPDF tools:
- Ubuntu/Debian: `sudo apt-get install mupdf-tools`
- macOS: `brew install mupdf`

### PDF doesn't open
- Ensure a PDF viewer is installed
- Check the status bar for error message
- Try manually opening the PDF file

### Cache loading is slow
- Normal for large PDFs or many files
- Can take 5-30 seconds depending on system
- UI remains responsive during caching

## Development

### Running tests
```bash
# Check syntax
python3 -m py_compile pdf_searcher.py

# Run with timeout (for headless testing)
timeout 5 python3 pdf_searcher.py
```

### Code style
- Follow PEP 8 conventions
- Use type hints for better IDE support
- Document functions with docstrings

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

Built with Python, tkinter, and MuPDF

- **Scanned PDFs**: Text extraction requires searchable (OCR'd) PDFs; image-only PDFs are not supported
- **Performance**: Searching 1000+ PDFs may take time; progress feedback is minimal

## Future Enhancements

- Export results to CSV/JSON
- Progress bar during searches
- Search history / saved searches
- OCR support for scanned PDFs
- File filtering (by date, size, etc.)

## License

Open source - use freely for personal or commercial projects.

## Support

For issues or questions about Copilot-supported Python development, use Copilot Chat.

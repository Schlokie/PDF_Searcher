# PDF Searcher - Feature Documentation

## Overview

PDF Searcher provides intelligent text search across multiple PDF files with optimized performance through smart caching and multi-threaded operations.

---

## Feature 1: Background Caching System

### Purpose
Load all PDF text into memory cache in the background to enable instant repeated searches.

### How It Works
1. **Startup**: When the app launches, it automatically starts caching PDFs from the default folder (`/home/klem/Funk/cqdl`)
2. **Folder Selection**: When user selects a new folder via Browse, caching starts for that folder
3. **Status Updates**: Real-time progress shown in status bar:
   - `"Caching files in progress..."` - Initial state
   - `"Caching PDF text: 5/25"` - Progress indicator
   - `"Cache loaded 25 files"` - Completion message
4. **Background Thread**: Caching runs in `threading.Thread` to keep UI responsive

### Technical Implementation
```python
# Global state tracking
caching_in_progress = False  # Flag to check if cache is loading
pdf_text_cache = {}          # Dictionary storing PDF content
cached_folder = None         # Currently cached folder path

# Cache loading function
def load_pdf_text_cache(folder, status_var=None, on_complete=None):
    # Sets caching_in_progress = True
    # Extracts text using mutool
    # Updates status_var with progress
    # Calls on_complete() when finished
    # Sets caching_in_progress = False
```

### Performance
- **Cache Load Time**: 5-30 seconds (depends on PDF count and sizes)
- **Memory Usage**: 50-100 MB for ~100 typical PDFs
- **Search with Cache**: ~100ms (instant to user)
- **Search without Cache**: 2-5 seconds (per-document extraction)

### User Experience
- GUI appears immediately
- Status bar shows "Caching files in progress..."
- User can start typing search terms while caching
- All searches work, but are slower until cache completes

---

## Feature 2: Smart Auto Re-Search

### Purpose
When a user initiates a search during caching, automatically re-execute the search once caching completes to provide optimized (cached) results.

### How It Works
1. **Search During Caching**: User enters search terms and clicks "Search" while `caching_in_progress = True`
2. **Immediate Results**: Fallback search executes using non-cached search (slower, but shows results quickly)
3. **Store Parameters**: Search parameters are stored in `pending_search_params`
4. **Cache Completes**: When caching finishes, `on_complete` callback triggers
5. **Auto Re-Search**: `run_pending_search()` executes using cached data (much faster)
6. **Status Updates**: 
   - During first search: `"Searching..."`
   - After cache completes: `"Re-searching with cache..."`
   - Final: `"✓ Found 125 match(es) in 3 file(s)"`

### Technical Implementation
```python
# Global state
pending_search_params = None  # Stores search if initiated during caching

def search_command():
    # If caching in progress, store search params
    if caching_in_progress:
        pending_search_params = {
            'folder': folder,
            'search_term': search_term,
            'case_sensitive': case_var.get(),
            'use_regex': regex_var.get(),
            'whole_words': wholeword_var.get(),
        }
    
    # Always execute search immediately (cached or non-cached)

def run_pending_search():
    # Execute stored search params with cached data
    # Only called after caching completes if pending_search_params was set

# Called from load_pdf_text_cache() on_complete callback
on_complete=lambda: root.after(0, run_pending_search) if pending_search_params else None
```

### User Experience
- **Scenario 1**: User selects folder, waits for cache, then searches
  - Result: Fast cached search
- **Scenario 2**: User selects folder and immediately starts searching
  - First search: Shows results quickly (non-cached)
  - After cache loads: Automatically shows same results faster (cached)
- **Scenario 3**: User enters multiple searches while caching
  - Each search runs immediately
  - Only the last pending search is saved for re-execution

---

## Feature 3: Advanced Search Modes

### Normal Search
- Literal text matching
- Case-insensitive by default
- Exact substring matching

Example: Searching "PDF" finds "PDF", "PDFs", "download PDF"

### Regex Search
- Full regular expression support
- Case-insensitive by default (unless "Case Sensitive" checked)
- Powerful pattern matching

Examples:
- `\b[Pp]ython\b` - Word boundary matching
- `\d{3}-\d{3}-\d{4}` - Phone number pattern
- `[A-Z][a-z]+` - Capitalized words

### Whole Words Only
- Matches only complete words
- Respects word boundaries
- Case-insensitive by default

Example: Searching "PDF" with "Whole Words Only" finds "PDF" but not in "PDFs"

### Case Sensitive
- When checked, matches exact case
- Works with all search modes
- Forces `re.IGNORECASE` off

---

## Feature 4: Click-to-Open Results

### How It Works
1. User double-clicks a result in the results area
2. Application extracts filename and page number
3. System PDF viewer opens the file at that page
4. Status bar updates: `"Opened: document.pdf at page 5"`

### Cross-Platform Implementation
- **Windows**: `start` command with page specification
- **macOS**: `open` command with file URL and page anchor
- **Linux**: `xdg-open` with page parameter

### Error Handling
- Missing PDF viewers handled gracefully
- Status bar shows error if file not found
- Application doesn't crash on failures

---

## Feature 5: Responsive UI Architecture

### Threading Model
- **Main Thread**: GUI event loop using tkinter
- **Worker Threads**: Background tasks (caching, searching)
- **Thread-Safe Updates**: `root.after()` for GUI updates from worker threads

### Key Benefits
- GUI never freezes
- Long operations happen in background
- Status bar provides real-time feedback
- Users can cancel operations and try others

### Technical Details
```python
# Search in background thread
def search_worker():
    # Long operation
    results = search_from_cache(...)
    # Schedule GUI update on main thread
    root.after(0, lambda: display_results(results))

search_thread = threading.Thread(target=search_worker, daemon=True)
search_thread.start()
```

---

## Feature 6: Status Bar Feedback

### State Indicators

| Status | Meaning |
|--------|---------|
| `"Ready."` | Idle, waiting for user action |
| `"Caching files in progress..."` | Initial caching state |
| `"Caching PDF text: 5/25"` | Progress - caching 5th of 25 files |
| `"Cache loaded 25 files"` | Caching complete |
| `"Searching..."` | Search operation in progress |
| `"Re-searching with cache..."` | Auto re-search after cache complete |
| `"✓ Found 125 match(es) in 3 file(s)"` | Successful search results |
| `"✗ No matches found"` | Search completed with no results |
| `"Opened: document.pdf at page 5"` | PDF successfully opened |
| `"Failed to open PDF"` | Error opening PDF viewer |

### Color Coding
- Status text: Blue (`#0066cc`)
- Provides visual feedback for user actions

---

## Architecture Diagram

```
┌─────────────────────────────────────┐
│   PDF Searcher Application          │
└─────────────────────────────────────┘
          ↓
    ┌─────────────────────┐
    │   tkinter GUI       │  ← Main Thread (event loop)
    ├─────────────────────┤
    │ - Folder selector   │
    │ - Search input      │
    │ - Options checkboxes│
    │ - Results display   │
    │ - Status bar        │
    └─────────────────────┘
          ↓ (spawns threads)
    ┌─────────────────────────────────┐
    │   Background Workers            │
    ├─────────────────────────────────┤
    │ ┌─ Cache Thread ──────┐         │
    │ │ - Read all PDFs      │ ← Load cache in background
    │ │ - Extract text       │
    │ │ - Store in memory    │
    │ └──────────────────────┘         │
    │                                   │
    │ ┌─ Search Thread ──────┐         │
    │ │ - Query cache/disk    │ ← Search in background
    │ │ - Match text          │
    │ │ - Format results      │
    │ └──────────────────────┘         │
    │                                   │
    │ ┌─ Open Thread ────────┐         │
    │ │ - Launch PDF viewer   │ ← Open PDF at page
    │ └──────────────────────┘         │
    └─────────────────────────────────┘
```

---

## Configuration

### Default Folder
Located at: `/home/klem/Funk/cqdl`

To change, modify in `pdf_searcher.py`:
```python
default_folder = "/path/to/your/pdf/folder"
```

### System Dependencies
Required for text extraction:
- `mupdf-tools` (provides `mutool` command)
- `python3-tk` (provides tkinter)

### Requirements
See `requirements.txt` (currently empty - only uses standard library and system tools)

---

## Performance Optimization Tips

1. **Organize PDFs**: Keep PDFs in dedicated folders
2. **Cache Preload**: Application caches on startup (don't interrupt this)
3. **Specific Searches**: Use whole-word or regex for precise results
4. **Keyboard**: Use Enter key to search faster than clicking button

---

## Limitations & Future Improvements

### Current Limitations
- All PDFs cached in RAM (no streaming)
- Single-folder searches (subdirectories included)
- No incremental caching (full reload on folder change)
- No search result pagination

### Planned Improvements
- Incremental PDF caching
- Multi-folder search
- Search history
- Result export/bookmarking
- Dark mode UI
- Custom PDF viewer selection

---

## Troubleshooting

### Issue: "mutool: command not found"
**Solution**: Install MuPDF tools
```bash
# Ubuntu/Debian
sudo apt-get install mupdf-tools

# macOS
brew install mupdf
```

### Issue: Caching takes very long
**Solution**: Normal behavior for large PDF collections
- Typical: 5-30 seconds for 100 files
- Large PDFs take longer
- UI remains responsive during this time

### Issue: Search results appear slowly
**Solution**: Depends on cache state
- Before cache loads: 2-5 seconds (normal)
- After cache loads: ~100ms (cached)
- If still slow, PDFs may be large/complex

### Issue: PDF doesn't open on double-click
**Solution**:
- Check PDF file still exists
- Verify PDF viewer is installed
- Try opening PDF manually to test viewer

---

## Additional Resources

- [MuPDF Documentation](https://mupdf.com/docs/)
- [Python tkinter Docs](https://docs.python.org/3/library/tkinter.html)
- [Regular Expression Guide](https://docs.python.org/3/library/re.html)

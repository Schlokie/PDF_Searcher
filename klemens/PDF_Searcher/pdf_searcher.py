#!/usr/bin/env python3
"""
PDF Searcher - Desktop application to search text in PDF files.

Simple GUI built with tkinter for cross-platform compatibility.
Features:
  - Search all PDFs in a folder
  - Advanced search: regex, case-sensitive, whole-word matching
  - Click-to-open results at specific page in system PDF viewer
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import argparse

from src.pdf_handler import search_all_pdfs_in_folder
from src.utils import open_pdf_at_page


# Global cache to store actual result data
search_results: List[Dict] = []

# Global PDF text cache for fast repeated search
pdf_text_cache: Dict[Path, str] = {}
cached_folder: Optional[str] = None

# Caching state
caching_in_progress = False
pending_search_params = None


def load_pdf_text_cache(folder: str, status_var=None, on_complete=None) -> None:
    """Load all PDF text from given folder into memory cache."""
    global pdf_text_cache, cached_folder, caching_in_progress
    caching_in_progress = True
    pdf_text_cache.clear()
    cached_folder = folder

    if status_var is not None:
        status_var.set("Caching files in progress...")

    pdf_files = list(Path(folder).rglob('*.pdf'))
    for idx, pdf_file in enumerate(sorted(pdf_files), 1):
        try:
            # Use mutool to extract text quickly
            result = subprocess.run(
                ['mutool', 'draw', '-F', 'txt', str(pdf_file)],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                pdf_text_cache[pdf_file] = result.stdout
            else:
                pdf_text_cache[pdf_file] = ''
        except Exception:
            pdf_text_cache[pdf_file] = ''

        if status_var is not None:
            status_var.set(f"Caching PDF text: {idx}/{len(pdf_files)}")

    if status_var is not None:
        status_var.set(f"Cache loaded {len(pdf_text_cache)} files")

    caching_in_progress = False
    if on_complete:
        on_complete()


def _build_regex(pattern: str, search_type: str, case_sensitive: bool):
    if search_type == 'whole_words':
        return re.compile(r"\\b" + re.escape(pattern) + r"\\b", 0 if case_sensitive else re.IGNORECASE)
    elif search_type == 'regex':
        return re.compile(pattern, 0 if case_sensitive else re.IGNORECASE)
    else:
        return re.compile(re.escape(pattern), 0 if case_sensitive else re.IGNORECASE)


def search_from_cache(
    folder: str,
    search_term: str,
    case_sensitive: bool,
    use_regex: bool,
    whole_words: bool,
) -> List[Dict]:
    """Search cached PDF texts instead of running mutool each request."""
    global cached_folder
    if cached_folder != folder or not pdf_text_cache:
        raise RuntimeError('Cache not loaded for folder')

    search_type = 'regex' if use_regex else 'whole_words' if whole_words else 'normal'
    pattern = _build_regex(search_term, search_type, case_sensitive)
    results = []

    for pdf_file, full_text in pdf_text_cache.items():
        pages = full_text.split('\f')
        for page_num, page_text in enumerate(pages, start=1):
            if not page_text.strip():
                continue
            for match in pattern.finditer(page_text):
                context = _get_context_around_match(page_text, match)
                results.append({
                    'page': page_num,
                    'file_path': str(pdf_file),
                    'match_text': match.group(),
                    'context': context,
                })
    return results


def _get_context_around_match(text: str, match, context_chars: int = 60) -> str:
    start = max(0, match.start() - context_chars)
    end = min(len(text), match.end() + context_chars)
    before = text[start:match.start()].replace("\n", " ")
    match_text = match.group()
    after = text[match.end():end].replace("\n", " ")
    return f"...{before}{match_text}{after}..."


def create_gui(default_folder=None):
    """Create the main tkinter GUI."""
    root = tk.Tk()
    root.title("PDF Searcher")
    root.geometry("900x700")
    root.configure(bg="#f0f0f0")

    # Title
    title_label = tk.Label(root, text="PDF Search Tool", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
    title_label.pack(pady=(10, 0))
    
    # Author note
    author_label = tk.Label(root, text="by DL1KLF, 2026-04-05", font=("Helvetica", 10), bg="#f0f0f0")
    author_label.pack(pady=(0, 10))

    # Folder selection frame
    folder_frame = tk.Frame(root, bg="#f0f0f0")
    folder_frame.pack(pady=5)
    
    tk.Label(folder_frame, text="Folder:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
    folder_var = tk.StringVar()
    folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=50)
    folder_entry.grid(row=0, column=1, padx=5)
    
    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            folder_var.set(folder)
            # Start caching in background thread
            def cache_worker():
                try:
                    load_pdf_text_cache(folder, status_var=status_var, on_complete=lambda: root.after(0, run_pending_search) if pending_search_params else None)
                except Exception as e:
                    status_var.set(f"Cache load failed: {e}")
                    global caching_in_progress
                    caching_in_progress = False
            
            cache_thread = threading.Thread(target=cache_worker, daemon=True)
            cache_thread.start()

    tk.Button(folder_frame, text="Browse", command=browse_folder).grid(row=0, column=2, padx=5)

    # Search term frame
    search_frame = tk.Frame(root, bg="#f0f0f0")
    search_frame.pack(pady=5)
    
    tk.Label(search_frame, text="Search Term:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=50)
    search_entry.grid(row=0, column=1, padx=5)
    search_entry.focus()

    # Enter key starts search
    search_entry.bind("<Return>", lambda event: search_command())

    # Options frame
    options_frame = tk.Frame(root, bg="#f0f0f0")
    options_frame.pack(pady=5)
    
    case_var = tk.BooleanVar()
    tk.Checkbutton(options_frame, text="Case Sensitive", variable=case_var, bg="#f0f0f0").grid(row=0, column=0, padx=10)
    
    regex_var = tk.BooleanVar()
    tk.Checkbutton(options_frame, text="Regex Pattern", variable=regex_var, bg="#f0f0f0").grid(row=0, column=1, padx=10)
    
    wholeword_var = tk.BooleanVar()
    tk.Checkbutton(options_frame, text="Whole Words Only", variable=wholeword_var, bg="#f0f0f0").grid(row=0, column=2, padx=10)

    # Buttons frame
    buttons_frame = tk.Frame(root, bg="#f0f0f0")
    buttons_frame.pack(pady=10)
    
    def search_command():
        global pending_search_params
        folder = folder_var.get()
        search_term = search_var.get()
        
        if not folder:
            messagebox.showerror("Error", "Please select a folder first")
            return
        
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term")
            return
        
        # If caching in progress, store params for re-run after caching
        if caching_in_progress:
            pending_search_params = {
                'folder': folder,
                'search_term': search_term,
                'case_sensitive': case_var.get(),
                'use_regex': regex_var.get(),
                'whole_words': wholeword_var.get(),
            }
        
        # Update status
        status_var.set("Searching...")
        root.update()
        
        # Run search in background thread
        def search_worker():
            # If cache is ready for this folder use it, otherwise fallback to search_all_pdfs_in_folder
            try:
                results = search_from_cache(
                    folder,
                    search_term,
                    case_sensitive=case_var.get(),
                    use_regex=regex_var.get(),
                    whole_words=wholeword_var.get(),
                )
            except Exception:
                results = perform_search(
                    folder,
                    search_term,
                    case_sensitive=case_var.get(),
                    use_regex=regex_var.get(),
                    whole_words=wholeword_var.get(),
                )

            # Store results for clicked event handling
            search_results.clear()
            search_results.extend(results)

            # Format for display
            display_items = [format_result_for_display(r) for r in results]
            results_text.delete(1.0, tk.END)
            results_text.insert(tk.END, "\n".join(display_items))

            if results:
                status_var.set(f"✓ Found {len(results)} match(es) in {len(set(r['file_path'] for r in results))} file(s)")
            else:
                status_var.set("✗ No matches found")

        search_thread = threading.Thread(target=search_worker, daemon=True)
        search_thread.start()
    
    def clear_command():
        global pending_search_params
        folder_var.set("")
        search_var.set("")
        case_var.set(False)
        regex_var.set(False)
        wholeword_var.set(False)
        results_text.delete(1.0, tk.END)
        status_var.set("Ready.")
        search_results.clear()
        pending_search_params = None
    
    def run_pending_search():
        global pending_search_params
        if not pending_search_params:
            return
        
        params = pending_search_params
        pending_search_params = None
        
        # Simulate search with stored params
        folder = params['folder']
        search_term = params['search_term']
        case_sensitive = params['case_sensitive']
        use_regex = params['use_regex']
        whole_words = params['whole_words']
        
        # Update status
        status_var.set("Re-searching with cache...")
        root.update()
        
        # Run search in background thread
        def search_worker():
            try:
                results = search_from_cache(
                    folder,
                    search_term,
                    case_sensitive=case_sensitive,
                    use_regex=use_regex,
                    whole_words=whole_words,
                )
            except Exception:
                # If cache still not ready, shouldn't happen
                results = perform_search(
                    folder,
                    search_term,
                    case_sensitive=case_sensitive,
                    use_regex=use_regex,
                    whole_words=whole_words,
                )

            # Store results for clicked event handling
            search_results.clear()
            search_results.extend(results)

            # Format for display
            display_items = [format_result_for_display(r) for r in results]
            results_text.delete(1.0, tk.END)
            results_text.insert(tk.END, "\n".join(display_items))

            if results:
                status_var.set(f"✓ Found {len(results)} match(es) in {len(set(r['file_path'] for r in results))} file(s)")
            else:
                status_var.set("✗ No matches found")

        search_thread = threading.Thread(target=search_worker, daemon=True)
        search_thread.start()
    
    tk.Button(buttons_frame, text="Search", command=search_command, width=10).grid(row=0, column=0, padx=5)
    tk.Button(buttons_frame, text="Clear", command=clear_command, width=10).grid(row=0, column=1, padx=5)
    tk.Button(buttons_frame, text="Exit", command=root.quit, width=10).grid(row=0, column=2, padx=5)

    # Results frame
    results_frame = tk.Frame(root, bg="#f0f0f0")
    results_frame.pack(pady=5, fill=tk.BOTH, expand=True)
    
    tk.Label(results_frame, text="Results (double-click to open PDF):", font=("Helvetica", 10, "bold"), bg="#f0f0f0").pack()
    
    results_text = scrolledtext.ScrolledText(results_frame, width=90, height=20, font=("Courier", 10))
    results_text.pack(fill=tk.BOTH, expand=True)
    
    def on_result_double_click(event):
        try:
            # Get the current line
            line_start = results_text.index("insert linestart")
            line_end = results_text.index("insert lineend")
            selected_line = results_text.get(line_start, line_end).strip()
            
            if selected_line and search_results:
                # Find the corresponding result
                for i, result in enumerate(search_results):
                    if format_result_for_display(result) == selected_line:
                        # Open PDF at page
                        success = open_pdf_at_page(result["file_path"], result["page"])
                        
                        if success:
                            status_var.set(f"Opened: {Path(result['file_path']).name} at page {result['page']}")
                        else:
                            status_var.set("Failed to open PDF")
                        break
        except Exception as e:
            status_var.set(f"Error: {str(e)}")
    
    results_text.bind("<Double-Button-1>", on_result_double_click)

    # Status bar
    status_frame = tk.Frame(root, bg="#f0f0f0")
    status_frame.pack(fill=tk.X, pady=5)
    
    status_var = tk.StringVar()
    status_var.set("Ready.")
    status_label = tk.Label(status_frame, textvariable=status_var, bg="#f0f0f0", fg="#0066cc", anchor="w")
    status_label.pack(fill=tk.X, padx=10)

    # Set default folder and preload cache in background
    if default_folder is None:
        default_folder = "/home/klem/Funk/cqdl"
    if Path(default_folder).exists():
        folder_var.set(default_folder)
        # Start caching in background thread
        def cache_worker():
            try:
                load_pdf_text_cache(default_folder, status_var=status_var, on_complete=lambda: root.after(0, run_pending_search) if pending_search_params else None)
            except Exception as e:
                status_var.set(f"Cache load failed: {e}")
                global caching_in_progress
                caching_in_progress = False
        
        cache_thread = threading.Thread(target=cache_worker, daemon=True)
        cache_thread.start()

    return root


def format_result_for_display(result: Dict) -> str:
    """
    Format a search result for display in the listbox.
    
    Format: "filename.pdf - Page 5 - ...context..."
    """
    filename = Path(result["file_path"]).name
    page = result["page"]
    match_text = result["match_text"][:30]  # First 30 chars of match
    
    return f"{filename} - Page {page} - [{match_text}]"


def perform_search(
    folder: str,
    search_term: str,
    case_sensitive: bool,
    use_regex: bool,
    whole_words: bool,
    status_callback=None
):
    """
    Perform search in background thread.
    
    Args:
        folder: Folder to search in
        search_term: Search query
        case_sensitive: Case-sensitive matching
        use_regex: Use regex pattern
        whole_words: Match whole words only
        status_callback: Function to update status (not used yet, for future progress bar)
    
    Returns:
        List of result dicts
    """
    if not folder or not search_term:
        return []
    
    # Determine search type
    if use_regex:
        search_type = "regex"
    elif whole_words:
        search_type = "whole_words"
    else:
        search_type = "normal"
    
    # Perform the search
    results = search_all_pdfs_in_folder(
        folder,
        search_term,
        search_type=search_type,
        case_sensitive=case_sensitive,
        recursive=True
    )
    
    return results


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="PDF Searcher")
    parser.add_argument('--folder', type=str, help='Default folder to search in')
    args = parser.parse_args()
    
    root = create_gui(default_folder=args.folder)
    root.mainloop()


if __name__ == "__main__":
    main()

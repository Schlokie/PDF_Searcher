"""
PDF text extraction and search logic.

Uses system mupdf-tools (mutool) for PDF processing with page tracking.
Supports advanced search: regex patterns, case-sensitive matching, whole-word search.
"""

import subprocess
import re
import os
from pathlib import Path
from typing import List, Dict, Optional


def search_pdf_advanced(
    pdf_path: str,
    pattern: str,
    search_type: str = "normal",
    case_sensitive: bool = False
) -> List[Dict]:
    """
    Search for text in a single PDF file using mutool.
    
    Args:
        pdf_path: Path to the PDF file
        pattern: Search query (text or regex pattern)
        search_type: 'normal' (literal), 'regex' (pattern), 'whole_words'
        case_sensitive: If True, match case-sensitively
    
    Returns:
        List of result dicts with keys:
            - page: Page number (1-indexed)
            - file_path: Path to PDF file
            - match_text: Matched text
            - context: Snippet around match (60 chars before/after)
    
    Raises:
        Exception: If PDF cannot be opened or read
    """
    results = []
    
    try:
        # Extract text from PDF using mutool
        result = subprocess.run(
            ['mutool', 'draw', '-F', 'txt', pdf_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return [{"error": f"Failed to extract text from {pdf_path}: {result.stderr}"}]
        
        text = result.stdout
        
        # Split text by pages (mutool outputs pages separated by form feed)
        pages = text.split('\f')
        
        for page_num, page_text in enumerate(pages, 1):
            if not page_text.strip():
                continue
                
            # Build regex pattern based on search type
            if search_type == "whole_words":
                # Match whole words only (word boundaries)
                regex_pattern = r"\b" + re.escape(pattern) + r"\b"
            elif search_type == "regex":
                # User provides regex pattern directly
                regex_pattern = pattern
            else:
                # Normal: escape special chars for literal matching
                regex_pattern = re.escape(pattern)
            
            # Set flags for case sensitivity
            flags = 0 if case_sensitive else re.IGNORECASE
            
            # Find all matches in this page
            for match in re.finditer(regex_pattern, page_text, flags):
                context = _get_context_around_match(page_text, match, context_chars=60)
                
                results.append({
                    "page": page_num,
                    "file_path": pdf_path,
                    "match_text": match.group(),
                    "context": context
                })
    
    except subprocess.TimeoutExpired:
        return [{"error": f"Timeout extracting text from {pdf_path}"}]
    except FileNotFoundError:
        return [{"error": "mutool not found. Please install mupdf-tools"}]
    except Exception as e:
        return [{"error": f"Failed to process {pdf_path}: {str(e)}"}]
    
    return results


def search_all_pdfs_in_folder(
    folder_path: str,
    pattern: str,
    search_type: str = "normal",
    case_sensitive: bool = False,
    recursive: bool = True
) -> List[Dict]:
    """
    Search all PDF files in a folder (and optionally subfolders).
    
    Args:
        folder_path: Path to folder containing PDFs
        pattern: Search query
        search_type: 'normal', 'regex', or 'whole_words'
        case_sensitive: Case-sensitive matching
        recursive: If True, search subdirectories recursively
    
    Returns:
        List of all results from all PDFs, sorted by (filename, page)
    """
    all_results = []
    
    if not os.path.isdir(folder_path):
        return [{"error": f"Folder not found: {folder_path}"}]
    
    # Find all PDF files
    folder = Path(folder_path)
    if recursive:
        pdf_files = list(folder.rglob("*.pdf"))
    else:
        pdf_files = list(folder.glob("*.pdf"))
    
    if not pdf_files:
        return []
    
    # Search each PDF
    for pdf_file in sorted(pdf_files):
        results = search_pdf_advanced(
            str(pdf_file),
            pattern,
            search_type=search_type,
            case_sensitive=case_sensitive
        )
        
        # Skip error entries for now (or handle separately)
        all_results.extend([r for r in results if "error" not in r])
    
    # Sort by filename, then page number
    all_results.sort(key=lambda r: (os.path.basename(r["file_path"]), r["page"]))
    
    return all_results


def _get_context_around_match(text: str, match, context_chars: int = 60) -> str:
    """
    Extract context snippet around a regex match.
    
    Args:
        text: Full text containing the match
        match: Regex match object
        context_chars: Characters to include before/after match
    
    Returns:
        Context string: "...before MATCH after..."
    """
    start = max(0, match.start() - context_chars)
    end = min(len(text), match.end() + context_chars)
    
    before = text[start:match.start()].replace("\n", " ")
    match_text = match.group()
    after = text[match.end():end].replace("\n", " ")
    
    return f"...{before}{match_text}{after}..."

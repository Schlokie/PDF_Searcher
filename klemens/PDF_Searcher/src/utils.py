"""
Cross-platform PDF opening utility.

Handles opening PDF files with system default viewer at a specific page.
Supports Windows, macOS, and Linux with fallback mechanisms.
"""

import subprocess
import platform
import os
import sys
from typing import Optional


def open_pdf_at_page(pdf_path: str, page_number: int = 1) -> bool:
    """
    Open a PDF file at a specific page using the system default viewer.
    
    Args:
        pdf_path: Full path to the PDF file
        page_number: Page number to open at (1-indexed)
    
    Returns:
        True if successful, False otherwise
    
    Examples:
        >>> open_pdf_at_page("/home/user/docs/report.pdf", 5)
        True
    """
    if not os.path.isfile(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return False
    
    if page_number < 1:
        page_number = 1
    
    system = platform.system()
    
    try:
        if system == "Windows":
            return _open_pdf_windows(pdf_path, page_number)
        elif system == "Darwin":  # macOS
            return _open_pdf_macos(pdf_path, page_number)
        elif system == "Linux":
            return _open_pdf_linux(pdf_path, page_number)
        else:
            print(f"Unsupported operating system: {system}")
            return False
    
    except Exception as e:
        print(f"Error opening PDF: {str(e)}")
        return False


def _open_pdf_windows(pdf_path: str, page_number: int) -> bool:
    """
    Open PDF on Windows using Adobe Reader or system default.
    
    Adobe Reader command line syntax: AcroRd32.exe /A page=X=filepath
    """
    # Normalize path for Windows
    pdf_path = os.path.abspath(pdf_path)
    
    # Try Adobe Reader first (most reliable for page targeting)
    adobe_paths = [
        r"C:\Program Files (x86)\Adobe\Acrobat Reader\Reader\AcroRd32.exe",
        r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
        r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
    ]
    
    for adobe_path in adobe_paths:
        if os.path.exists(adobe_path):
            try:
                subprocess.Popen([
                    adobe_path,
                    "/A", f"page={page_number}={pdf_path}"
                ])
                return True
            except Exception as e:
                print(f"Failed to open with Adobe Reader: {str(e)}")
                continue
    
    # Fallback: Use system default viewer (won't open at specific page)
    try:
        os.startfile(pdf_path)
        print(f"Opened with system default viewer (page targeting not supported)")
        return True
    except Exception as e:
        print(f"Failed to open with system default: {str(e)}")
        return False


def _open_pdf_macos(pdf_path: str, page_number: int) -> bool:
    """
    Open PDF on macOS using Preview or system default.
    
    Preview can accept file URI with page anchor: file://path#page=X
    """
    pdf_path = os.path.abspath(pdf_path)
    
    # Try Preview app with page targeting via file URI
    try:
        file_uri = f"file://{pdf_path}"
        # Preview app can use anchors: file://path#page=X
        subprocess.run([
            "open", "-a", "Preview",
            file_uri + f"#page={page_number}"
        ], check=False)
        return True
    except Exception as e:
        print(f"Failed to open with Preview: {str(e)}")
    
    # Fallback: Use system default viewer
    try:
        subprocess.run(["open", pdf_path], check=False)
        print(f"Opened with system default viewer (page targeting may not work)")
        return True
    except Exception as e:
        print(f"Failed to open with system default: {str(e)}")
        return False


def _open_pdf_linux(pdf_path: str, page_number: int) -> bool:
    """
    Open PDF on Linux using evince, okular, or system default.
    
    Most Linux PDF viewers support page targeting via URI anchor: path#page=X
    """
    pdf_path = os.path.abspath(pdf_path)
    pdf_uri = f"{pdf_path}#page={page_number}"
    
    # List of PDF viewers to try, in order of preference
    viewers = [
        ("evince", pdf_uri),           # GNOME default
        ("okular", pdf_uri),           # KDE default
        ("xpdf", [pdf_path, str(page_number)]),  # xpdf with page arg
    ]
    
    for viewer, args in viewers:
        # Check if viewer is available
        if _command_exists(viewer):
            try:
                if isinstance(args, str):
                    subprocess.Popen([viewer, args], start_new_session=True)
                else:
                    subprocess.Popen([viewer] + args, start_new_session=True)
                return True
            except Exception as e:
                print(f"Failed to open with {viewer}: {str(e)}")
                continue
    
    # Fallback: Use xdg-open (system default)
    try:
        subprocess.Popen(["xdg-open", pdf_path], start_new_session=True)
        print(f"Opened with xdg-open/system default (page targeting not supported)")
        return True
    except Exception as e:
        print(f"Failed to open with xdg-open: {str(e)}")
        return False


def _command_exists(command: str) -> bool:
    """
    Check if a command is available in the system PATH (Linux/macOS).
    """
    try:
        subprocess.run(
            ["which", command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

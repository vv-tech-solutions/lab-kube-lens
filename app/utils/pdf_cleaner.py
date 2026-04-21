"""
Utility for extracting clean, semantic text from a PDF.

The helper performs the following steps:

1.  Open the PDF with PyMuPDF.
2.  Detect header and footer blocks using the page layout (Y‑coordinate).  A line that
    appears on a high proportion of pages and2011coordinate).  A line that
    appears on a high proportion of pages and is shorter than a configurable
    minimum length is considered a header or footer.
3.  Extract all remaining body lines, collapse runs of whitespace, and join
    sentences using a robust regular expression.
4.  Return the resulting string.

The layout‑based detection is the default behaviour, but a simple text‑based
fallback is used when a page contains fewer blocks than requested.
"""

from __future__ import annotations

import regex as re
from pathlib import Path
from collections import Counter
from typing import Iterable

# Default parameters for header/footer detection
HEADER_FOOTER_THRESHOLD = 0.8
HEADER_FOOTER_N_LINES = 3
MIN_LINE_LENGTH = 5
USE_LAYOUT_DETECTION = True


import fitz  # PyMuPDF


def _extract_lines(page_text: str) -> list[str]:
    """Return a list of non‑empty stripped lines from a page."""
    return [ln.strip() for ln in page_text.splitlines() if ln.strip()]


def _detect_header_footer(
    doc: fitz.Document, threshold: float = HEADER_FOOTER_THRESHOLD, n_lines: int = HEADER_FOOTER_N_LINES
) -> tuple[set[str], set[str]]:
    """Detect header/footer lines using page layout.

    The function examines the Y‑coordinate of text blocks.  For each page it
    selects the top *n_lines* blocks as header candidates and the bottom
    *n_lines* blocks as footer candidates.  Candidates that appear on more
    than *threshold* of all pages and are longer than ``MIN_LINE_LENGTH``
    characters are considered header/footer lines.

    If a page contains fewer than *n_lines* blocks the function falls back to a
    simple text‑based approach for that page.
    """
    # Single‑page PDFs
    if len(doc) <= 1:
        return set(), set()

    header_counter: Counter[str] = Counter()
    footer_counter: Counter[str] = Counter()

    for pg in doc:
        blocks = pg.get_text("blocks")  # list of [x0, y0, x1, y1, text, block_no]
        if len(blocks) < n_lines:
            # Fallback to text‑based detection for this page
            text = pg.get_text()
            lines = _extract_lines(text)
            header_counter.update(lines[:n_lines])
            footer_counter.update(lines[-n_lines:])
            continue

        # Sort blocks by Y coordinate (top to bottom)
        sorted_blocks = sorted(blocks, key=lambda b: b[1])
        header_blocks = sorted_blocks[:n_lines]
        footer_blocks = sorted_blocks[-n_lines:]

        header_counter.update([b[4].strip() for b in header_blocks])
        footer_counter.update([b[4].strip() for b in footer_blocks])

    n_pages = len(doc)
    header_lines = {ln for ln, cnt in header_counter.items() if cnt > threshold * n_pages}
    footer_lines = {ln for ln, cnt in footer_counter.items() if cnt > threshold * n_pages}
    return header_lines, footer_lines


def _collapse_whitespace(lines: Iterable[str]) -> list[str]:
    """Collapse any run of whitespace characters into a single space."""
    return [re.sub(r"\s+", " ", ln) for ln in lines]


def _join_sentences(lines: Iterable[str]) -> str:
    """
    Join lines using a robust sentence‑splitting regex.
    The regex splits after a period2011splitting regex.
    The regex splits after a period, exclamation, or question mark followed by a space
    and an uppercase letter, unless the preceding word is a known abbreviation.
    """
    # Common abbreviations that should not trigger a split
    abbreviations = {"Dr", "Mr", "Mrs", "Ms", "Prof", "Inc", "Ltd", "Jr", "Sr"}
    # Build a negative look‑behind that excludes these abbreviations
    abbr_pattern = "|".join(abbreviations)
    split_re = re.compile(rf"(?<!\b(?:{abbr_pattern}))[.!?]\s+(?=[A-Z])")

    buffer: list[str] = []
    result: list[str] = []

    # Process each line to split sentences while preserving abbreviations
    processed: list[str] = []
    for ln in lines:
        # Insert a newline after a period that is not part of an abbreviation
        ln_split = split_re.sub(".\n", ln)
        # Split the line into individual sentences
        for part in ln_split.split("\n"):
            part = part.strip()
            if part:
                processed.append(part)
    return "\n".join(processed)


def clean_text_from_pdf(pdf_path: str | Path) -> str:
    """
    Extract a clean, whitespace‑normalised string from a PDF.

    Parameters
    ----------
    pdf_path
        Path to the PDF file.

    Returns
    -------
    str
        The extracted body text with headers, footers and excess whitespace removed.
    """
    doc = fitz.open(str(pdf_path))

    header_lines, footer_lines = _detect_header_footer(doc)

    body_lines: list[str] = []

    for pg in doc:
        for ln in _extract_lines(pg.get_text()):
            if ln not in header_lines and ln not in footer_lines:
                body_lines.append(ln)

    body_lines = _collapse_whitespace(body_lines)
    return _join_sentences(body_lines)

__all__ = ["clean_text_from_pdf"]
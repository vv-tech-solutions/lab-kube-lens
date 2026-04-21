"""
Test the PDF cleaning helper.

The test creates small PDFs on‑the‑fly with headers, footers, and body text,
then verifies that the helper strips headers/footers and normalises whitespace.
"""

import io
from pathlib import Path

import pytest
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from app.utils.pdf_cleaner import clean_text_from_pdf


@pytest.fixture
def single_page_pdf(tmp_path: Path) -> Path:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    c.setFont("Helvetica", 12)
    # On met volontairement des espaces multiples
    c.drawString(50, 600, "First   body   line.") 
    c.drawString(50, 580, "Second  body  line.")
    c.showPage()
    c.save()
    pdf_file = tmp_path / "single.pdf"
    pdf_file.write_bytes(buf.getvalue())
    return pdf_file


@pytest.fixture
def multi_page_pdf(tmp_path: Path) -> Path:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)

    # Page 1
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(300, 800, "Header")
    c.setFont("Helvetica", 12)
    c.drawString(50, 600, "Body line 1.")
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(300, 30, "Footer")
    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(300, 800, "Header")
    c.setFont("Helvetica", 12)
    c.drawString(50, 600, "Body line 2.")
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(300, 30, "Footer")
    c.showPage()

    c.save()
    buf.seek(0)
    pdf_file = tmp_path / "multi.pdf"
    pdf_file.write_bytes(buf.read())
    return pdf_file


def test_clean_text_single_page_whitespace(single_page_pdf: Path):
    """
    Vérifie que sur une page unique :
    1. Le texte est conservé (car len(doc) <= 1 donc pas de suppression).
    2. Les espaces multiples sont nettoyés par _join_sentences.
    """
    text = clean_text_from_pdf(single_page_pdf)
    
    # On vérifie que le texte est là
    assert "First body line." in text
    assert "Second body line." in text
    
    # On vérifie la normalisation des espaces (plus de doubles espaces)
    assert "  " not in text
    # On vérifie qu'on n'a pas supprimé de lignes indûment
    lines = [l for l in text.split("\n") if l.strip()]
    assert len(lines) == 2

def test_clean_text_multi_page_header_footer(multi_page_pdf: Path):
    """
    Vérifie que sur plusieurs pages, les éléments répétés 
    (Header/Footer) sont bien supprimés.
    """
    text = clean_text_from_pdf(multi_page_pdf)
    
    assert "Header" not in text
    assert "Footer" not in text
    assert "Body line 1." in text
    assert "Body line 2." in text
    
    # Vérifie que le résultat final est bien découpé en lignes propres
    expected = ["Body line 1.", "Body line 2."]
    assert [l.strip() for l in text.strip().split("\n")] == expected

def test_abbreviation_handling_with_regex(tmp_path: Path):
    """
    Vérifie que le nouveau module 'regex' gère bien le look-behind 
    et ne coupe pas la phrase après 'Dr.'.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    c.setFont("Helvetica", 12)
    # On met une phrase avec abréviation suivie d'une Majuscule
    c.drawString(50, 600, "Contact Dr. Smith for details. He is home.")
    c.showPage()
    c.save()
    
    pdf_file = tmp_path / "abbr.pdf"
    pdf_file.write_bytes(buf.getvalue())
    
    text = clean_text_from_pdf(pdf_file)
    
    # On s'attend à ce que "Dr. Smith" ne soit PAS coupé, 
    # mais que le split se fasse après "details." car il y a "He" après.
    lines = [l.strip() for l in text.strip().split("\n")]
    
    assert any("Dr. Smith" in l for l in lines)
    assert len(lines) >= 2 
    assert lines[0].startswith("Contact Dr. Smith")


def test_short_header_footer_detection_multi_page(tmp_path: Path):
    """Vérifie que les headers courts sont supprimés s'ils sont répétés."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=LETTER)
    for i in range(2): # On crée 2 pages
        c.drawCentredString(300, 800, "H") # Header répété
        c.drawString(50, 600, f"Unique body line {i}.")
        c.drawCentredString(300, 30, "F") # Footer répété
        c.showPage()
    c.save()
    
    pdf_file = tmp_path / "short_rep.pdf"
    pdf_file.write_bytes(buf.getvalue())
    
    text = clean_text_from_pdf(pdf_file)
    assert "H" not in text
    assert "F" not in text
    assert "Unique body line" in text

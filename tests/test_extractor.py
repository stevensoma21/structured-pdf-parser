from pathlib import Path
import sys

from fpdf import FPDF

# Ensure repository root is on the import path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.nlp.extractor import extract_from_pdf


def create_sample_pdf(path: Path) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "MODULE ONE\nInstall the engine\nTighten the bolts\nMODULE TWO\nCheck the fuel lines")
    pdf.output(str(path))


def test_extract_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    create_sample_pdf(pdf_path)
    document = extract_from_pdf(pdf_path)
    assert [m.heading for m in document.modules] == ["MODULE ONE", "MODULE TWO"]
    assert [s.text for s in document.modules[0].steps] == ["Install the engine", "Tighten the bolts"]
    assert [s.text for s in document.modules[1].steps] == ["Check the fuel lines"]

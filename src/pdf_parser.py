from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List

from pdfminer.high_level import extract_text

HEADING_RE = re.compile(r'^([A-Z0-9][A-Z0-9\s\-]{2,})$')
STEP_RE = re.compile(r'^(?:\d+\.|[a-zA-Z]\.\s|[-\*\u2022])\s+')


def is_heading(line: str) -> bool:
    """Return True if the line looks like a section heading."""
    if line.endswith(':'):
        return True
    if HEADING_RE.match(line):
        return True
    return False


def parse_pdf(path: str) -> Dict[str, List[Dict[str, object]]]:
    """Parse a PDF file into structured sections and steps.

    Parameters
    ----------
    path: str
        Path to the PDF file.

    Returns
    -------
    dict
        Parsed representation with sections and procedural steps.
    """
    raw_text = extract_text(path)
    lines = [re.sub(r'\s+', ' ', line).strip() for line in raw_text.splitlines()]
    lines = [line for line in lines if line]

    sections: List[Dict[str, object]] = []
    current = {"heading": "Document", "text": [], "steps": []}

    for line in lines:
        if is_heading(line):
            if current["text"] or current["steps"]:
                current["text"] = " ".join(current["text"]).strip()
                sections.append(current)
            current = {"heading": line, "text": [], "steps": []}
        else:
            current["text"].append(line)
            if STEP_RE.match(line):
                step_text = STEP_RE.sub('', line).strip()
                current["steps"].append(step_text)

    if current["text"] or current["steps"]:
        current["text"] = " ".join(current["text"]).strip()
        sections.append(current)

    return {"file": os.path.basename(path), "sections": sections}


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse PDF into structured sections")
    parser.add_argument("pdf_path", help="Path to a PDF file")
    args = parser.parse_args()

    parsed = parse_pdf(args.pdf_path)

    out_dir = Path("data/parsed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / (Path(args.pdf_path).stem + ".json")
    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(parsed, fh, indent=2)
    print(f"Saved parsed data to {out_file}")


if __name__ == "__main__":
    main()

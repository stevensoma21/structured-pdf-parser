from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import json
import re
from pathlib import Path

try:
    import spacy
except ImportError as exc:  # pragma: no cover - handled in tests
    raise RuntimeError("spaCy is required for the extractor module") from exc

try:
    nlp_default = spacy.load("en_core_web_sm")
except Exception:  # pragma: no cover - handled in tests
    # Fall back to a blank model if the small model is unavailable.
    nlp_default = spacy.blank("en")


@dataclass
class Step:
    """A procedural step extracted from text."""

    text: str
    substeps: List["Step"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"text": self.text, "substeps": [s.to_dict() for s in self.substeps]}


@dataclass
class Module:
    """A module delimited by a heading in the source document."""

    heading: str
    steps: List[Step] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"heading": self.heading, "steps": [s.to_dict() for s in self.steps]}


@dataclass
class Document:
    """Structured representation of a PDF document."""

    modules: List[Module] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps({"modules": [m.to_dict() for m in self.modules]}, indent=2)


HEADING_PATTERN = re.compile(r"^[A-Z0-9\s]+$")


def is_heading(line: str) -> bool:
    """Determine if a line of text looks like a heading.

    A very small heuristic that considers a line to be a heading if it contains
    only capital letters, numbers, and whitespace.
    """

    return bool(HEADING_PATTERN.match(line.strip()))


def extract_steps(text: str, nlp) -> List[Step]:
    """Extract imperative verb phrases from the given text.

    A sentence is considered a step if the first token is a verb in base form
    (tag_ == "VB"). Substeps are naively split by semicolons.
    """

    doc = nlp(text)
    steps: List[Step] = []
    for sent in doc.sents:
        if not sent:  # pragma: no cover - defensive
            continue
        first = sent[0]
        if first.tag_ == "VB":
            substeps = [Step(text=sub.strip()) for sub in sent.text.split(";") if sub.strip()]
            steps.append(Step(text=substeps[0].text, substeps=substeps[1:]))
    return steps


def extract_modules(text: str, nlp=nlp_default) -> Document:
    """Split text into modules and extract steps for each module."""

    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    modules: List[Module] = []
    current: Optional[Module] = None

    for line in lines:
        if is_heading(line):
            if current:
                modules.append(current)
            current = Module(heading=line)
        else:
            if not current:
                current = Module(heading="INTRO")
            current.steps.extend(extract_steps(line, nlp))
    if current:
        modules.append(current)
    return Document(modules=modules)


def extract_from_pdf(path: Path | str, nlp=nlp_default) -> Document:
    """Read a PDF and return its structured representation."""

    from pypdf import PdfReader

    reader = PdfReader(str(path))
    text_parts: List[str] = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        text_parts.append(extracted)
    text = "\n".join(text_parts)
    return extract_modules(text, nlp)


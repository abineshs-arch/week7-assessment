"""Parsers and chunker for the knowledge assistant corpus."""
import csv
import re
from pathlib import Path

from docx import Document
from pypdf import PdfReader

CHUNK_SIZE, OVERLAP = 256, 32
SUPPORTED = {".pdf", ".docx", ".txt", ".csv"}
HEADING = re.compile(r"^(section\s+\d+|\d+\.\s+\S)", re.I)


def split_sections(text):
    blocks, section, buf = [], "Introduction", []
    for line in text.splitlines():
        s = line.strip()
        if s and len(s) < 70 and HEADING.match(s):
            if buf:
                blocks.append((section, " ".join(buf)))
            section, buf = s, []
        elif s:
            buf.append(s)
    if buf:
        blocks.append((section, " ".join(buf)))
    return blocks


def parse(path: Path):
    """Return a list of (page, section, text) units."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return [(n, s, t) for n, page in enumerate(PdfReader(path).pages, 1)
                for s, t in split_sections(page.extract_text() or "")]
    if ext == ".txt":
        return [(1, s, t) for s, t in split_sections(path.read_text(encoding="utf-8"))]
    if ext == ".docx":
        units, section, buf = [], "Introduction", []
        for para in Document(path).paragraphs:
            if para.style.name.startswith("Heading") or para.style.name == "Title":
                if buf:
                    units.append((1, section, " ".join(buf)))
                section, buf = para.text.strip(), []
            elif para.text.strip():
                buf.append(para.text.strip())
        if buf:
            units.append((1, section, " ".join(buf)))
        return units
    if ext == ".csv":
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        title = path.stem.replace("_", " ")
        return [(i, f"row {i}", f"{title} ({path.name}, row {i}): "
                 + "; ".join(f"{k}: {v}" for k, v in r.items())) for i, r in enumerate(rows, 1)]
    raise ValueError(f"unsupported file type {ext}")


def chunk_text(text, size=CHUNK_SIZE, overlap=OVERLAP):
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            space = text.rfind(" ", start + size // 2, end)
            if space != -1:
                end = space
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]
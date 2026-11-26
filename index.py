"""Indexing pipeline: load -> parse -> chunk -> embed -> store (Qdrant 'policy_docs').
Stable uuid5 ids + file hash: running twice re-indexes nothing."""
import hashlib
import time
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (Distance, FieldCondition, Filter, FilterSelector, MatchValue,
                                  PointStruct, VectorParams)
from sentence_transformers import SentenceTransformer

from parsers import SUPPORTED, chunk_text, parse

COLLECTION = "policy_docs"
VERSION = "v1"
NS = uuid.UUID("6f1c2a52-7b7e-4a55-9a51-1b6c0a7d7e05")
client = QdrantClient(url="http://localhost:6333")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

DEPT = [("leave", "HR"), ("onboarding", "HR"), ("performance", "HR"), ("learning", "HR"), ("remote", "HR"),
        ("holiday", "HR"), ("training", "HR"), ("it_", "IT"), ("security", "IT"), ("travel", "Finance"),
        ("expense", "Finance"), ("procurement", "Finance"), ("sales", "Sales"), ("supplier", "Finance"),
        ("quality", "Quality"), ("sop_", "Quality"), ("product", "Quality"), ("health", "Operations"),
        ("customer", "Operations"), ("office", "Operations"), ("code_of", "Legal"), ("privacy", "Legal"),
        ("whistle", "Legal")]
YEAR = {"leave_policy_2023.txt": 2023, "handbook.pdf": 2024}


def meta(name):
    dept = next((d for k, d in DEPT if k in name), "General")
    return dict(department=dept, year=YEAR.get(name, 2026))


def by_source(name):
    return Filter(must=[FieldCondition(key="source", match=MatchValue(value=name))])


def stored_hash(name):
    pts = client.scroll(COLLECTION, scroll_filter=by_source(name), limit=1, with_payload=["file_hash"])[0]
    return pts[0].payload["file_hash"] if pts else None


def index_documents(folder="corpus"):
    T = time.perf_counter
    if not client.collection_exists(COLLECTION):
        client.create_collection(COLLECTION, vectors_config=VectorParams(size=384, distance=Distance.COSINE))

    t = T(); files = [p for p in sorted(Path(folder).iterdir()) if p.suffix.lower() in SUPPORTED]
    todo = [(p, h) for p in files
            if (h := hashlib.sha256(VERSION.encode() + p.read_bytes()).hexdigest()) != stored_hash(p.name)]
    print(f"[LOAD ] {len(files)} files, {len(files) - len(todo)} unchanged, {len(todo)} to index ({T() - t:.2f}s)")

    t = T(); units = [(p, h, u) for p, h in todo for u in parse(p)]
    print(f"[PARSE] {len(units)} sections/pages ({T() - t:.2f}s)")

    t = T(); chunks = []
    for p, h, (page, section, text) in units:
        for i, c in enumerate(chunk_text(text)):
            chunks.append(dict(source=p.name, doc_type=p.suffix[1:], page=page, section=section, chunk_index=i,
                               text=c, file_hash=h, **meta(p.name), uid=f"{p.name}|{page}|{section}|{i}"))
    print(f"[CHUNK] {len(chunks)} chunks (256 chars / 32 overlap) ({T() - t:.2f}s)")

    t = T(); vecs = model.encode([c["text"] for c in chunks], normalize_embeddings=True) if chunks else []
    print(f"[EMBED] {len(vecs)} embeddings ({T() - t:.2f}s)")

    t = T()
    for p, _ in todo:
        client.delete(COLLECTION, points_selector=FilterSelector(filter=by_source(p.name)))
    if chunks:
        client.upsert(COLLECTION, points=[PointStruct(id=str(uuid.uuid5(NS, c["uid"])), vector=v.tolist(), payload=c)
                                          for c, v in zip(chunks, vecs)])
    total = client.count(COLLECTION, exact=True).count
    print(f"[STORE] upserted {len(chunks)} -> '{COLLECTION}' has {total} points ({T() - t:.2f}s)")


if __name__ == "__main__":
    index_documents()
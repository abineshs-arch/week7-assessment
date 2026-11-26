"""Task 2: BM25 vs vector vs hybrid (RRF, k=60) vs hybrid+rerank (top 50 -> top 5) on 12 questions."""
import re
import time
from pathlib import Path

from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from rag_config import rrf

COLLECTION = "policy_docs"
client = QdrantClient(url="http://localhost:6333")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
CHUNKS = {str(p.id): p.payload for p in client.scroll(COLLECTION, limit=100_000, with_payload=True)[0]}
IDS = list(CHUNKS)
STOP = set("a an the is are was were be of to in on for at by with and or what when where who how which "
           "do does can i my me we you your it this that from as if per".split())
tok = lambda t: [w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP]
bm25 = BM25Okapi([tok(CHUNKS[i]["text"]) for i in IDS])


def bm25_search(q, n=50):
    s = bm25.get_scores(tok(q))
    return [IDS[i] for i in sorted(range(len(IDS)), key=lambda i: -s[i])[:n]]


def vector_search(q, n=50, flt=None):
    v = embedder.encode(q, normalize_embeddings=True).tolist()
    return [str(h.id) for h in client.query_points(COLLECTION, query=v, limit=n, query_filter=flt).points]


def hybrid_search(q, n=50):
    return [d for d, _ in rrf([bm25_search(q, n), vector_search(q, n)], k=60)][:n]


def rerank(q, ids, top=5):
    scores = reranker.predict([(q, CHUNKS[i]["text"]) for i in ids])
    return [i for _, i in sorted(zip(scores, ids), key=lambda x: -x[0])][:top]


def rank_of(ids, phrase):
    return next((r for r, i in enumerate(ids, 1) if phrase.lower() in CHUNKS[i]["text"].lower()), None)


QUESTIONS = [  # (question, type, phrase the right chunk contains)
    ("Which supplier is SUP-04?", "exact", "Deccan Alloys"),
    ("What is course TR-203?", "exact", "Building RAG Applications"),
    ("What is expense code EX-05 for?", "exact", "Client entertainment"),
    ("What is extension 7777 used for?", "exact", "7777"),
    ("Which office has security extension 4107?", "exact", "4107"),
    ("What is part YT-1006?", "exact", "YT-1006"),
    ("Can I keep unused vacation days for next year?", "meaning", "carried forward"),
    ("What should I do if my work computer goes missing?", "meaning", "Lost or stolen"),
    ("How fast must a data leak be reported?", "meaning", "6 hours"),
    ("How quickly do urgent customer tickets get a reply?", "meaning", "30 minutes"),
    ("Is there money for my home internet when working remotely?", "meaning", "internet reimbursement of Rs. 1,000"),
    ("How long before my job becomes permanent?", "meaning", "probation period is 6 months"),
]

if __name__ == "__main__":
    for q, _, p in QUESTIONS:
        if not any(p.lower() in c["text"].lower() for c in CHUNKS.values()):
            print("WARNING phrase not in corpus:", p)
    reranker.predict([("warm", "up")])
    methods = {"BM25": bm25_search, "Vector": vector_search, "Hybrid (RRF)": hybrid_search}
    rows, ms = [], {m: 0.0 for m in list(methods) + ["Hybrid + rerank"]}
    for q, kind, p in QUESTIONS:
        r = {}
        for m, fn in methods.items():
            t = time.perf_counter(); ids = fn(q); ms[m] += time.perf_counter() - t
            r[m] = ids
        t = time.perf_counter(); r["Hybrid + rerank"] = rerank(q, r["Hybrid (RRF)"]); ms["Hybrid + rerank"] += time.perf_counter() - t
        rows.append((q, kind, {m: rank_of(ids, p) for m, ids in r.items()}))

    hit = lambda m: sum(1 for *_, rk in rows if rk[m] and rk[m] <= 3) / len(rows)
    show = lambda x: str(x) if x else "-"
    md = ["# Task 2 - Retrieval comparison (hit@3, 12 questions)", "",
          "| # | Question | Type | BM25 | Vector | Hybrid | Rank before rerank | Rank after rerank |", "|---|---|---|---|---|---|---|---|"]
    for n, (q, kind, rk) in enumerate(rows, 1):
        y = lambda m: "Y" if rk[m] and rk[m] <= 3 else "N"
        md.append(f"| {n} | {q} | {kind} | {y('BM25')} | {y('Vector')} | {y('Hybrid (RRF)')} | "
                  f"{show(rk['Hybrid (RRF)'])} | {show(rk['Hybrid + rerank'])} |")
        print(f"{n:<3}{kind:8} BM25 {show(rk['BM25']):3} Vec {show(rk['Vector']):3} Hyb {show(rk['Hybrid (RRF)']):3} "
              f"Rerank {show(rk['Hybrid + rerank']):3} | {q}")
    md += ["", "| Method | Hit@3 | Avg latency |", "|---|---|---|"]
    md += [f"| {m} | {hit(m):.2f} | {ms[m] / len(rows) * 1000:.0f} ms |" for m in ms]
    summary = " | ".join(f"{m} {hit(m):.2f}" for m in ms)
    print("\nHit@3:", summary)
    Path("task2_retrieval.md").write_text("\n".join(md), encoding="utf-8")
    print("Saved task2_retrieval.md")
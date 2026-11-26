"""Task 1 query side: answer(question, k=4), score fallback, fit_context token budget."""
from pathlib import Path

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from llm_utils import call_llm

COLLECTION, THRESHOLD = "policy_docs", 0.35
FALLBACK = "I don't have information on that."
TEMPLATE = "Answer ONLY using the context below.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
MODEL_LIMIT, RESERVED_OUTPUT = 4000, 500
client = QdrantClient(url="http://localhost:6333")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
tok = embedder.tokenizer
ntok = lambda s: len(tok.encode(s, add_special_tokens=False))


def retrieve(question, k=4):
    v = embedder.encode(question, normalize_embeddings=True).tolist()
    return [dict(score=h.score, **h.payload) for h in client.query_points(COLLECTION, query=v, limit=k).points]


def block(c):
    return f"[Source: {c['source']}, Page {c['page']}] {c['text']}"


def fit_context(chunks, budget):
    """Add chunks in rank order until the next one would exceed the token budget."""
    kept, used = [], 0
    for c in chunks:
        t = ntok(block(c)) + 2
        if used + t > budget:
            break
        kept.append(c)
        used += t
    return kept, used


def answer(question, k=4):
    chunks = retrieve(question, k)
    best = chunks[0]["score"] if chunks else 0.0
    if not chunks or best < THRESHOLD:
        return dict(answer=FALLBACK, best=best, llm=False, chunks=chunks, ctx_tokens=0)
    budget = MODEL_LIMIT - RESERVED_OUTPUT - ntok(TEMPLATE) - ntok(question)
    kept, used = fit_context(chunks, budget)
    prompt = TEMPLATE.format(context="\n\n".join(block(c) for c in kept), question=question)
    return dict(answer=call_llm(prompt).replace("\n", " "), best=best, llm=True, chunks=kept, ctx_tokens=used)


ANSWERABLE = [("How many days of paid annual leave do employees get?", "18"),
              ("What is the minimum password length?", "12"),
              ("How long is the probation period?", "6 months"),
              ("How many vendor quotations are needed for purchases above Rs. 50,000?", "3"),
              ("How often are company laptops replaced?", "4 years"),
              ("How much internet reimbursement do remote workers get?", "1,000")]
UNANSWERABLE = ["Who won the world cup?", "What is the capital of France?",
                "How much is the gym membership reimbursement?", "What is the dental insurance coverage limit?"]

if __name__ == "__main__":
    md = ["# Task 1 - Query pipeline results", "", f"Template: `{TEMPLATE.splitlines()[0]}` | threshold {THRESHOLD}", "",
          "| Type | Question | Answer | Best score | LLM called | Correct |", "|---|---|---|---|---|---|"]
    for q, exp in ANSWERABLE:
        r = answer(q)
        ok = exp.lower() in r["answer"].lower()
        print(f"[answerable]   {r['best']:.2f} llm={r['llm']} ok={ok} | {q} -> {r['answer'][:90]}")
        md.append(f"| answerable | {q} | {r['answer'][:150]} | {r['best']:.2f} | {r['llm']} | {'Y' if ok else 'N'} |")
    for q in UNANSWERABLE:
        r = answer(q)
        ok = "don't have information" in r["answer"].lower()
        print(f"[unanswerable] {r['best']:.2f} llm={r['llm']} ok={ok} | {q} -> {r['answer'][:90]}")
        md.append(f"| unanswerable | {q} | {r['answer'][:150]} | {r['best']:.2f} | {r['llm']} | {'Y' if ok else 'N'} |")

    md += ["", f"## fit_context: simulated {MODEL_LIMIT}-token model, {RESERVED_OUTPUT} reserved for output", "",
           "| k | Chunks kept | Context tokens | Correct |", "|---|---|---|---|"]
    q, exp = ANSWERABLE[2]
    for k in (2, 5, 10):
        r = answer(q, k)
        ok = exp.lower() in r["answer"].lower()
        print(f"k={k:<2} kept={len(r['chunks'])} ctx_tokens={r['ctx_tokens']} ok={ok}")
        md.append(f"| {k} | {len(r['chunks'])} | {r['ctx_tokens']} | {'Y' if ok else 'N'} |")
    kept, used = fit_context(retrieve(q, 10), 150)
    print(f"fit_context demo: budget 150 -> kept {len(kept)} of 10 chunks ({used} tokens)")
    md += ["", f"Budget demo: budget 150 tokens -> kept {len(kept)} of 10 chunks ({used} tokens)."]
    Path("task1_results.md").write_text("\n".join(md), encoding="utf-8")
    print("Saved task1_results.md")
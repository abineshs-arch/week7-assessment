"""Task 2: HyDE vs raw question (vector search) - hit@3 and latency on the same 12 questions."""
import time
from pathlib import Path

from llm_utils import call_llm
from retrieval import QUESTIONS, rank_of, vector_search

HYDE_PROMPT = ("Write a short hypothetical answer (2 sentences) to the question below, written like a paragraph "
               "from a company policy document. Do not say it is hypothetical.\n\nQuestion: {q}")

rows = []
for q, kind, p in QUESTIONS:
    t = time.perf_counter(); raw_rank = rank_of(vector_search(q, 10), p); raw_s = time.perf_counter() - t
    t = time.perf_counter(); fake = call_llm(HYDE_PROMPT.format(q=q)).replace("\n", " ")
    hyde_rank = rank_of(vector_search(fake, 10), p); hyde_s = time.perf_counter() - t
    rows.append((q, kind, raw_rank, hyde_rank, raw_s, hyde_s, fake))
    tag = "HELPS" if (hyde_rank or 99) <= 3 < (raw_rank or 99) else ("HURTS" if (raw_rank or 99) <= 3 < (hyde_rank or 99) else "")
    print(f"raw {str(raw_rank or '-'):3} hyde {str(hyde_rank or '-'):3} {tag:6}| {q}")

hit = lambda col: sum(1 for r in rows if r[col] and r[col] <= 3) / len(rows)
lat = lambda col: sum(r[col] for r in rows) / len(rows) * 1000
print(f"\nHit@3: raw {hit(2):.2f} | HyDE {hit(3):.2f}   Latency: raw {lat(4):.0f} ms | HyDE {lat(5):.0f} ms")

md = ["# Task 2 - HyDE vs raw question (vector search)", "",
      "| Question | Type | Raw rank | HyDE rank | Hypothetical answer |", "|---|---|---|---|---|"]
md += [f"| {q} | {k} | {r or '-'} | {h or '-'} | {f[:120]} |" for q, k, r, h, _, _, f in rows]
md += ["", "| Strategy | Hit@3 | Avg latency |", "|---|---|---|",
       f"| Raw question | {hit(2):.2f} | {lat(4):.0f} ms |", f"| HyDE | {hit(3):.2f} | {lat(5):.0f} ms |",
       "", "Latency of HyDE includes one LLM call; re-runs read from the cache, so only the first run shows the real cost."]
Path("task2_hyde.md").write_text("\n".join(md), encoding="utf-8")
print("Saved task2_hyde.md")
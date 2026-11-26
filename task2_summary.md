# Task 2 - Advanced Retrieval: Summary

Corpus: 53 files, 363 chunks in Qdrant `policy_docs`. 12 questions: 6 exact-term (codes, numbers), 6 meaning-based (paraphrases). Details: `task2_retrieval.md`, `task2_hyde.md`, `task2_filters.md`.

## Hit@3 comparison

| Method | Hit@3 |
|---|---|
| BM25 (rank_bm25) | 0.83 |
| Vector (MiniLM) | 0.75 |
| Hybrid (RRF, 1 / (60 + rank)) | 0.75 |
| **Hybrid + cross-encoder rerank (top 50 -> top 5)** | **0.92** |

- BM25 wins on exact codes (SUP-04, TR-203, EX-05) that embeddings blur.
- Vector wins on paraphrases ("work computer goes missing" -> "lost or stolen devices").
- Plain RRF with k = 60 gives both lists equal say, so it did not beat the better single retriever here.
- The cross-encoder reranker reads question and chunk together and gave the best result. Example: "money for home internet" moved from rank 3 to rank 1.
- Hardest question: "How long before my job becomes permanent?" (no shared words with "probation"): hybrid rank 19, not fixed by reranking.

## HyDE vs raw question (vector search)

| Strategy | Hit@3 | Avg latency |
|---|---|---|
| Raw question | 0.75 | 29 ms |
| HyDE | 0.67 | 2,859 ms |

- **Helps:** "How long before my job becomes permanent?" rank 6 -> 1 (the fake answer mentions probation).
- **Hurts:** "Which supplier is SUP-04?" and "What is expense code EX-05 for?" - the fake answer drops the exact code.
- Decision: keep raw/hybrid search as default; use HyDE only as a fallback when retrieval confidence is low. It adds ~100x latency.

## Metadata filtering

Question: "How many days of paid annual leave do employees get?"

| | Sources | Answer |
|---|---|---|
| Before (no filter) | includes `leave_policy_2023.txt` (HR, 2023) | mentions 15 days (outdated) |
| After (department = HR, year >= 2025) | only `leave_policy.txt` (HR, 2026) | **18 days** (correct) |

The year filter removes the outdated document from the context, so the answer uses only the current policy.
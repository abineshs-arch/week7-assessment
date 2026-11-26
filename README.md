# Week 7 Assessment - Policy Q&A Assistant

A RAG system that answers company policy questions **only from the documents**, cites every fact, and refuses when it does not know.

## Architecture

```
corpus/ (53 files: PDF, DOCX, TXT, CSV)
  -> index.py: load -> parse -> chunk (256/32) -> "title - section:" header -> embed (MiniLM) -> Qdrant "policy_docs"
     stable uuid5 ids + SHA-256 file hash (2nd run: 53 unchanged, 0 re-indexed); metadata: source, page, department, year
  -> answer: retrieve top-4 -> best score < 0.35 ? "I don't have information on that" (no LLM call)
             : Gemini with "answer ONLY from context, cite [file, p.N], refuse if missing"
  -> citation validator (regex) removes citations not in the retrieved chunks
  -> app.py: POST /ask (X-API-Key) -> {answer, sources[file, page, snippet], confidence}; 404 no results, 401, 503
```

## Setup

1. `docker start qdrant`
2. `.env` (never committed): `GEMINI_API_KEY=...`, `KA_API_KEY=...`, `GEMINI_MODEL=gemini-3.5-flash-lite`
3. `py index.py` - build the index
4. `py -m uvicorn app:app --port 8000` - API, Swagger demo at http://localhost:8000/docs
5. `py -m pytest -v test_api.py` - 5 API tests

## Results by task

| Task | File | Key result |
|---|---|---|
| 1 Pipeline + fallback + context budget | `task1_results.md` | 6/6 answerable correct, 4/4 unanswerable refused; fit_context with k = 2, 5, 10 |
| 2 Advanced retrieval | `task2_summary.md` | Hit@3: BM25 0.83, vector 0.75, hybrid RRF 0.75, hybrid + rerank 0.92; HyDE helps on paraphrases, hurts on codes; year filter removes the outdated 2023 policy |
| 3 Citations + hallucination control | `task3_faithfulness.md` | 3 prompt versions: 0 hallucinations each, only v3 cites (0 fake citations); manual faithfulness 1.00 on 5 answers; POST /ask with 5 passing tests |
| 4 Golden dataset + RAGAS | `task4_results.md` | Faithfulness 0.75 -> **0.92** after contextual chunk headers; hit 0.83 -> 1.00; refusals 3/3 |

## Decisions

- **v3 prompt** (cite + refuse) chosen for the API: same accuracy as the others, but every fact is traceable.
- **Score fallback 0.35**: blocks clearly off-topic questions before the LLM, saving cost; the prompt still refuses borderline ones.
- **Contextual chunk headers**: near-identical documents (15 SOPs) were indistinguishable without their titles.
- **Lite Gemini model first**: free-tier quota; `llm_utils.py` caches answers and falls back between models.

## Limitations

- Questions that need arithmetic across two facts (G11, total leave) are still refused - next fix is the prompt.
- 15-question golden set; RAGAS judge scores were spot-checked by hand (G05 judged wrongly).
- Synthetic corpus for a fictional company (see Week 7 Day 5 `sources.md`).
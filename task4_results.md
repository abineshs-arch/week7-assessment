# Task 4 - Golden Dataset and RAGAS

`golden.jsonl`: 15 questions (8 simple, 4 multi-chunk, 3 unanswerable), each with answer, source document, page and an evidence phrase. All 15 verified against the indexed corpus (`eval_golden.py`: "Verified 15 questions, 0 problems").

Pipeline: MiniLM top-4 retrieval from Qdrant `policy_docs` (53 files, 363 chunks) -> v3 prompt (answer only from context, cite every fact, refuse when missing) -> score fallback 0.35. RAGAS 0.4.4 on the 12 answerable questions; judge: gemini-3.5-flash-lite; embeddings: local MiniLM.

## Before / after

| Metric | Before (baseline) | After (exp1 context headers) |
|---|---|---|
| Hit@4 (all needed sources retrieved) | 0.83 | **1.00** |
| Faithfulness (target > 0.85) | 0.75 | **0.92** |
| Answer relevancy | 0.57 | **0.80** |
| Context precision | 0.67 | **0.71** |
| Context recall | 0.88 | **1.00** |
| Refusal accuracy (unanswerable) | 3/3 | 3/3 |
| False refusals (answerable) | 3/12 | **1/12** |

Full history: `experiment_log.md`. Per-question scores: `ragas_baseline.csv`, `ragas_exp1_context_headers.csv`.

## The 3 worst questions (baseline)

| ID | Question | Failure type | Cause |
|---|---|---|---|
| G07 | Critical dimension of the Brake Caliper | Retrieval | The answer chunk ("flange thickness...") never names the product; the name is only in the PDF title, and the 15 SOPs look identical to the search. All metrics 0. |
| G10 | Valve Body torque and pieces per lot | Retrieval | The torque chunk (page 2) was found, the sampling chunk (page 1) was not, because it does not name the Valve Body. Recall 0.5. |
| G11 | Annual + sick leave in total | Generation | Both facts (18 and 10 days) were retrieved, but the strict prompt refused instead of adding them. |

## Fix applied: contextual chunk headers

Two of the three failures had the same root cause - chunks lost their document title. Every chunk is now stored as "document title - section: text" (`index.py`, `VERSION = "v2-context-headers"`, which changes every file hash and forces a full re-index). G07 and G10 are now answered correctly with citations. G11 remains a generation failure; the next fix is a prompt that allows combining facts and simple arithmetic.

Note: G05 scored faithfulness 0.0 in the baseline although its answer ("within 1 hour", cited) is correct - a RAGAS judge error, checked by hand.

## Summary in business terms

The Policy Q&A Assistant answers employee questions only from company documents and shows the source for every fact. On a 15-question test set built from the real policies, it now gives a grounded, cited answer to 11 of 12 answerable questions, and it correctly says "I don't have information on that" for all 3 questions the documents do not cover, so it does not invent benefits such as gym or dental allowances.

Faithfulness - how much of each answer is backed by the documents - rose from 0.75 to 0.92 after one change: labelling every text chunk with its document title. Before, questions about one product could be answered from another product's procedure, because the procedures look almost identical. That is the kind of error that leads to wrong torque values or inspection plans on the shop floor.

The search now finds every needed source (hit rate 1.00), so employees get complete answers with page references they can check themselves. The remaining gap is questions that need a small calculation across two facts (for example, total paid leave); the assistant currently refuses these rather than guess, which is the safer failure. The next improvement is to let it combine facts it has already retrieved, followed by a re-run of the same test set before release.
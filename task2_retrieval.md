# Task 2 - Retrieval comparison (hit@3, 12 questions)

| # | Question | Type | BM25 | Vector | Hybrid | Rank before rerank | Rank after rerank |
|---|---|---|---|---|---|---|---|
| 1 | Which supplier is SUP-04? | exact | Y | Y | Y | 1 | 1 |
| 2 | What is course TR-203? | exact | Y | Y | Y | 1 | 1 |
| 3 | What is expense code EX-05 for? | exact | Y | Y | Y | 1 | 1 |
| 4 | What is extension 7777 used for? | exact | Y | Y | Y | 1 | 1 |
| 5 | Which office has security extension 4107? | exact | Y | N | Y | 1 | 1 |
| 6 | What is part YT-1006? | exact | Y | N | N | 9 | 1 |
| 7 | Can I keep unused vacation days for next year? | meaning | Y | Y | Y | 1 | 1 |
| 8 | What should I do if my work computer goes missing? | meaning | N | Y | N | 6 | 1 |
| 9 | How fast must a data leak be reported? | meaning | Y | Y | Y | 1 | 1 |
| 10 | How quickly do urgent customer tickets get a reply? | meaning | Y | Y | Y | 1 | 1 |
| 11 | Is there money for my home internet when working remotely? | meaning | Y | Y | Y | 1 | 1 |
| 12 | How long before my job becomes permanent? | meaning | N | N | N | 19 | - |

| Method | Hit@3 | Avg latency |
|---|---|---|
| BM25 | 0.83 | 1 ms |
| Vector | 0.75 | 28 ms |
| Hybrid (RRF) | 0.75 | 27 ms |
| Hybrid + rerank | 0.92 | 586 ms |
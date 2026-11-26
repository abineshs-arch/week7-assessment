# Experiment log

| Experiment | Change | Hit@4 | Faithfulness | Answer relevancy | Context precision | Context recall | Refusal accuracy | False refusals |
|---|---|---|---|---|---|---|---|---|
| baseline | top-4 vector retrieval, v3 cite+refuse prompt, score fallback 0.35 | 0.83 | 0.75 | 0.57 | 0.67 | 0.88 | 3/3 | 3/12 |
| exp1_context_headers | Contextual chunk headers: document title + section prefixed to every chunk | 1.00 | 0.92 | 0.80 | 0.71 | 1.00 | 3/3 | 1/12 |

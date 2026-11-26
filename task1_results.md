# Task 1 - Query pipeline results

Template: `Answer ONLY using the context below.` | threshold 0.35

| Type | Question | Answer | Best score | LLM called | Correct |
|---|---|---|---|---|---|
| answerable | How many days of paid annual leave do employees get? | Based on the context provided, there are two different statements regarding paid annual leave:  * According to `leave_policy_2023.txt`, full-time empl | 0.83 | True | Y |
| answerable | What is the minimum password length? | Based on the context provided, the minimum password length is at least 12 characters. | 0.65 | True | Y |
| answerable | How long is the probation period? | The probation period is 6 months. | 0.80 | True | Y |
| answerable | How many vendor quotations are needed for purchases above Rs. 50,000? | Based on the provided context, purchases above Rs. 50,000 need **at least 3** vendor quotations. | 0.92 | True | Y |
| answerable | How often are company laptops replaced? | Laptops are replaced every 4 years. | 0.84 | True | Y |
| answerable | How much internet reimbursement do remote workers get? | An internet reimbursement of Rs. 1,000 per month. | 0.64 | True | Y |
| unanswerable | Who won the world cup? | I don't have information on that. | 0.12 | False | Y |
| unanswerable | What is the capital of France? | I don't have information on that. | 0.21 | False | Y |
| unanswerable | How much is the gym membership reimbursement? | Based on the provided context, there is no information about a gym membership reimbursement. | 0.43 | True | N |
| unanswerable | What is the dental insurance coverage limit? | I don't have information on that. | 0.31 | False | Y |

## fit_context: simulated 4000-token model, 500 reserved for output

| k | Chunks kept | Context tokens | Correct |
|---|---|---|---|
| 2 | 2 | 79 | Y |
| 5 | 5 | 193 | Y |
| 10 | 10 | 460 | Y |

Budget demo: budget 150 tokens -> kept 3 of 10 chunks (143 tokens).
**Manual check:** the gym question scored 0.43 (above the 0.35 threshold), so the LLM was called, but it refused correctly ('no information about a gym membership reimbursement'). The automatic check only matched the exact fallback sentence. Result: 6/6 answerable correct, 4/4 unanswerable refused (3 by the score fallback without an LLM call, 1 by the model).

**Note:** the annual-leave answer mixed the current policy (18 days) with leave_policy_2023.txt (15 days). Task 2 fixes this with a year filter.

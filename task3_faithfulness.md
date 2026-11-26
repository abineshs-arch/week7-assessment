# Task 3 - Manual faithfulness (5 answers, prompt v3)

Each answer was split into claims; each claim was checked by hand against the retrieved context (`task3_faithfulness_input.txt`).

| Answer | Claim | Supported? | Evidence in retrieved context |
|---|---|---|---|
| A1 Minimum password length | The minimum password length is 12 characters | Yes | it_security_policy.docx p.1 "at least 12 characters"; handbook.pdf p.6 "at least 12 characters" |
| A2 Probation period | The probation period is 6 months | Yes | onboarding_guide.txt p.1 "The probation period is 6 months" |
| A3 Vendor quotations | At least 3 vendor quotations are needed | Yes | procurement_policy.docx p.1 "need at least 3 vendor quotations" |
| A3 Vendor quotations | This applies to purchases above Rs. 50,000 | Yes | procurement_policy.docx p.1 "Purchases above Rs. 50,000" |
| A4 Laptop refresh | Laptops are replaced every 4 years | Yes | it_asset_policy.docx p.1 "Laptops are replaced every 4 years" |
| A5 Internet reimbursement | Remote workers get Rs. 1,000 per month for internet | Yes | remote_work_policy.docx p.1 "internet reimbursement of Rs. 1,000 per month" |
| A5 Internet reimbursement | It is paid with salary | Yes | remote_work_policy.docx p.1 "is paid with salary" |

| Answer | Supported / total | Faithfulness |
|---|---|---|
| A1 | 1/1 | 1.00 |
| A2 | 1/1 | 1.00 |
| A3 | 2/2 | 1.00 |
| A4 | 1/1 | 1.00 |
| A5 | 2/2 | 1.00 |
| **Average** | **7/7** | **1.00** |

All citations in these answers point to chunks that were actually retrieved (0 fake citations).

## Prompt comparison (10 questions, 3 unanswerable)

| Prompt version | Hallucinated answers | Refusals correct | Answers with citations | Fake citations |
|---|---|---|---|---|
| v1 basic | 0 | 3/3 | 0/10 | 0 |
| v2 ONLY-from-context | 0 | 3/3 | 0/10 | 0 |
| v3 ONLY + cite + refuse | 0 | 3/3 | 6/10 | 0 |

No version hallucinated on this set: the model refused when the facts were missing, and retrieval covered every answerable question. The difference is traceability: only v3 cites sources (6 of 7 answerable answers), and the regex validator found 0 fake citations. v3 is chosen for the API because every fact can be checked against its source.
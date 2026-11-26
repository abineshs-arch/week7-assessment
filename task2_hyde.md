# Task 2 - HyDE vs raw question (vector search)

| Question | Type | Raw rank | HyDE rank | Hypothetical answer |
|---|---|---|---|---|
| Which supplier is SUP-04? | exact | 1 | - | Vendor code SUP-04 designates Apex Logistics Solutions, which serves as the primary contractor for all regional freight  |
| What is course TR-203? | exact | 3 | 3 | Course TR-203, titled "Information Security and Data Privacy Governance," is a mandatory compliance module designed to i |
| What is expense code EX-05 for? | exact | 3 | 7 | Expense code EX-05 is designated exclusively for corporate travel bookings, including flights, lodging, and ground trans |
| What is extension 7777 used for? | exact | 1 | 1 | Extension 7777 is designated exclusively as the emergency crisis hotline for reporting critical security breaches and li |
| Which office has security extension 4107? | exact | 5 | 9 | Security extension 4107 is assigned to the main reception desk located in the headquarters building. Personnel stationed |
| What is part YT-1006? | exact | - | - | Part YT-1006 is designated as a standard-issue replacement assembly for automated conveyor systems within the primary fu |
| Can I keep unused vacation days for next year? | meaning | 2 | 1 | Unused vacation days cannot be carried over into the following calendar year and will be permanently forfeited as of Dec |
| What should I do if my work computer goes missing? | meaning | 2 | 2 | In the event that a company-issued computer goes missing, employees must immediately report the loss to the Information  |
| How fast must a data leak be reported? | meaning | 1 | 1 | All identified or suspected data leaks must be reported to the Information Security Department within two hours of disco |
| How quickly do urgent customer tickets get a reply? | meaning | 1 | 1 | Urgent customer tickets are systematically prioritized and assigned an initial response within fifteen minutes of submis |
| Is there money for my home internet when working remotely? | meaning | 3 | 1 | Employees working remotely are eligible for a monthly stipend to offset home internet expenses, provided they maintain a |
| How long before my job becomes permanent? | meaning | 6 | 1 | The probationary period for all newly appointed personnel shall extend for a duration of ninety calendar days from the o |

| Strategy | Hit@3 | Avg latency |
|---|---|---|
| Raw question | 0.75 | 29 ms |
| HyDE | 0.67 | 2859 ms |

Latency of HyDE includes one LLM call; re-runs read from the cache, so only the first run shows the real cost.
# Task 3 - Citations and prompt comparison

Context format: `[Source: file, Page n] text`. Citations parsed with a regex; a citation whose (file, page) is not in the retrieved chunks is flagged FAKE.

## v1 basic

| Question | Verdict | Citations | Fake | Answer |
|---|---|---|---|---|
| What is the minimum password length? | correct | 0 | - | Based on the provided context, the minimum password length is **12 characters**. |
| How long is the probation period? | correct | 0 | - | Based on the provided context, the probation period is 6 months. |
| How many vendor quotations are needed for purchases above Rs. 50,000? | correct | 0 | - | Based on the provided context, purchases above Rs. 50,000 need at least 3 vendor quotations. |
| How often are company laptops replaced? | correct | 0 | - | Company laptops are replaced every 4 years. |
| How much internet reimbursement do remote workers get? | correct | 0 | - | Based on the provided context, remote workers get an internet reimbursement of Rs. 1,000 per month. |
| Within how many hours must a data breach be reported? | correct | 0 | - | Based on the provided context, a data breach must be reported to the Data Protection Officer within 6 hours. |
| How many days of paternity leave do employees get? | correct | 0 | - | Based on the provided context, the duration of paternity leave varies by source:  * According to the **handbook.pdf** (Page 3), male employees get **5 days** of |
| How much is the gym membership reimbursement? | correct refusal | 0 | - | Based on the provided context, there is no mention of a gym membership reimbursement. |
| What is the dental insurance coverage limit? | correct refusal | 0 | - | Based on the provided context, there is no mention of the dental insurance coverage limit. |
| What is the referral bonus for hiring a friend? | correct refusal | 0 | - | Based on the provided context, there is no mention of a referral bonus for hiring a friend. |

## v2 ONLY-from-context

| Question | Verdict | Citations | Fake | Answer |
|---|---|---|---|---|
| What is the minimum password length? | correct | 0 | - | 12 characters |
| How long is the probation period? | correct | 0 | - | 6 months |
| How many vendor quotations are needed for purchases above Rs. 50,000? | correct | 0 | - | At least 3 vendor quotations. |
| How often are company laptops replaced? | correct | 0 | - | Every 4 years. |
| How much internet reimbursement do remote workers get? | correct | 0 | - | Rs. 1,000 per month |
| Within how many hours must a data breach be reported? | correct | 0 | - | 6 hours |
| How many days of paternity leave do employees get? | correct | 0 | - | Based on the provided context, male employees get 5 days of paid paternity leave (according to handbook.pdf, Page 3), and paternity leave is 12 working days (ac |
| How much is the gym membership reimbursement? | correct refusal | 0 | - | Based on the provided context, there is no mention of gym membership reimbursement. |
| What is the dental insurance coverage limit? | correct refusal | 0 | - | Based on the provided context, there is no mention of a dental insurance coverage limit. |
| What is the referral bonus for hiring a friend? | correct refusal | 0 | - | I am sorry, but the provided context does not contain information about a referral bonus for hiring a friend. |

## v3 ONLY + cite + refuse

| Question | Verdict | Citations | Fake | Answer |
|---|---|---|---|---|
| What is the minimum password length? | correct | 0 | - | The minimum password length is 12 characters [it_security_policy.docx, p. 1; handbook.pdf, p. 6]. |
| How long is the probation period? | correct | 1 | - | The probation period is 6 months [onboarding_guide.txt, p. 1]. |
| How many vendor quotations are needed for purchases above Rs. 50,000? | correct | 1 | - | At least 3 vendor quotations are needed for purchases above Rs. 50,000 [procurement_policy.docx, p. 1]. |
| How often are company laptops replaced? | correct | 1 | - | Laptops are replaced every 4 years [it_asset_policy.docx, p. 1]. |
| How much internet reimbursement do remote workers get? | correct | 1 | - | An internet reimbursement of Rs. 1,000 per month is paid with salary [remote_work_policy.docx, p. 1]. |
| Within how many hours must a data breach be reported? | correct | 1 | - | A data breach must be reported to the Data Protection Officer within 6 hours [data_privacy_policy.docx, p. 1]. |
| How many days of paternity leave do employees get? | correct | 2 | - | Male employees get 5 days of paid paternity leave [handbook.pdf, p. 3]. Paternity leave is 12 working days, to be used within 3 months of the child's birth [lea |
| How much is the gym membership reimbursement? | correct refusal | 0 | - | I don't have information on that. |
| What is the dental insurance coverage limit? | correct refusal | 0 | - | I don't have information on that. |
| What is the referral bonus for hiring a friend? | correct refusal | 0 | - | I don't have information on that. |

## Summary

| Prompt version | Hallucinated answers | Refusals correct | Answers with citations | Fake citations |
|---|---|---|---|---|
| v1 basic | 0 | 3/3 | 0/10 | 0 |
| v2 ONLY-from-context | 0 | 3/3 | 0/10 | 0 |
| v3 ONLY + cite + refuse | 0 | 3/3 | 6/10 | 0 |
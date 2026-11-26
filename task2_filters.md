# Task 2 - Metadata filtering

Question: **How many days of paid annual leave do employees get?**

Filter: `department = HR` AND `year >= 2025`

## BEFORE (no filter)

Sources: leave_policy_2023.txt (HR, 2023); leave_policy.txt (HR, 2026); leave_policy.txt (HR, 2026); leave_policy.txt (HR, 2026)

Answer: Based on the context provided, there are two different statements regarding paid annual leave:  * According to `leave_policy_2023.txt`, full-time employees get **15 days** of paid annual leave per year. * According to `leave_policy.txt`, full-time employees get **18 days** of paid annual leave per year.

## AFTER (department=HR, year>=2025)

Sources: leave_policy.txt (HR, 2026); leave_policy.txt (HR, 2026); leave_policy.txt (HR, 2026); leave_policy.txt (HR, 2026)

Answer: 18 days

**Outdated leave_policy_2023.txt in context: before=True, after=False**
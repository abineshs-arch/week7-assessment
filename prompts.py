"""Task 3: [Source: file, Page n] context, citation regex validator, 3 prompt versions on 10 questions."""
import json
import re
from pathlib import Path

from llm_utils import call_llm
from rag_basic import block, retrieve

V1 = "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
V2 = "Answer ONLY from the context below.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
V3 = ("Answer ONLY from the context below. Do not use outside knowledge.\n"
      "Cite the source after each fact in the format [filename, p.N], exactly as shown in the context.\n"
      "If the context does not contain the answer, reply exactly: I don't have information on that.\n\n"
      "Context:\n{context}\n\nQuestion: {question}\nAnswer:")
VERSIONS = {"v1 basic": V1, "v2 ONLY-from-context": V2, "v3 ONLY + cite + refuse": V3}
CITE = re.compile(r"\[(?:Source:\s*)?([\w\-. ]+?\.(?:pdf|docx|txt|csv)),\s*(?:p\.?|Page)\s*(\d+)\]", re.I)
REFUSE = re.compile(r"don.t have information|no information|not (mentioned|provided|specified|available|contain)|"
                    r"does not (contain|mention|provide|specify|include)|no mention", re.I)

QUESTIONS = [  # (question, expected text; None = not in the documents)
    ("What is the minimum password length?", "12"),
    ("How long is the probation period?", "6 months"),
    ("How many vendor quotations are needed for purchases above Rs. 50,000?", "3"),
    ("How often are company laptops replaced?", "4 years"),
    ("How much internet reimbursement do remote workers get?", "1,000"),
    ("Within how many hours must a data breach be reported?", "6 hours"),
    ("How many days of paternity leave do employees get?", "12 working days"),
    ("How much is the gym membership reimbursement?", None),
    ("What is the dental insurance coverage limit?", None),
    ("What is the referral bonus for hiring a friend?", None),
]


def validate(answer, chunks):
    allowed = {(c["source"].lower(), int(c["page"])) for c in chunks}
    cites = [(f.strip(), int(p)) for f, p in CITE.findall(answer)]
    return cites, [c for c in cites if (c[0].lower(), c[1]) not in allowed]


def judge(ans, exp):
    if exp is None:
        return "correct refusal" if REFUSE.search(ans) else "HALLUCINATED"
    if exp.lower() in ans.lower():
        return "correct"
    return "wrong refusal" if REFUSE.search(ans) else "HALLUCINATED"


saved, summary = [], []
md = ["# Task 3 - Citations and prompt comparison", "",
      "Context format: `[Source: file, Page n] text`. Citations parsed with a regex; a citation whose "
      "(file, page) is not in the retrieved chunks is flagged FAKE.", ""]
for name, tpl in VERSIONS.items():
    md += [f"## {name}", "", "| Question | Verdict | Citations | Fake | Answer |", "|---|---|---|---|---|"]
    h = ref = fake_n = cited = 0
    for q, exp in QUESTIONS:
        chunks = retrieve(q, 4)
        ans = call_llm(tpl.format(context="\n\n".join(block(c) for c in chunks), question=q)).replace("\n", " ")
        cites, fake = validate(ans, chunks)
        v = judge(ans, exp)
        h += v == "HALLUCINATED"; ref += (exp is None and v == "correct refusal")
        fake_n += len(fake); cited += bool(cites)
        print(f"[{name:24}] {v:15} cites={len(cites)} fake={len(fake)} | {q}")
        md.append(f"| {q} | {v} | {len(cites)} | {fake or '-'} | {ans[:160].replace('|', '/')} |")
        saved.append(dict(version=name, question=q, expected=exp, answer=ans, verdict=v,
                          contexts=[block(c) for c in chunks], fake=fake))
    summary.append((name, h, ref, cited, fake_n))
    md.append("")

print("\nVersion                    Hallucinated  Refusals ok  Answers with citations  Fake citations")
md += ["## Summary", "", "| Prompt version | Hallucinated answers | Refusals correct | Answers with citations | Fake citations |",
       "|---|---|---|---|---|"]
for name, h, ref, cited, fake_n in summary:
    print(f"{name:27}{h:<14}{ref}/3{'':10}{cited}/10{'':20}{fake_n}")
    md.append(f"| {name} | {h} | {ref}/3 | {cited}/10 | {fake_n} |")

Path("task3_prompts.md").write_text("\n".join(md), encoding="utf-8")
Path("task3_answers.json").write_text(json.dumps(saved, indent=1, ensure_ascii=False), encoding="utf-8")
print("Saved task3_prompts.md and task3_answers.json")
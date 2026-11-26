"""Task 2: metadata filtering (department, year) removes the outdated 2023 leave policy from an answer."""
from pathlib import Path

from qdrant_client.models import FieldCondition, Filter, MatchValue, Range

from llm_utils import call_llm
from rag_basic import TEMPLATE, block, client, embedder

Q = "How many days of paid annual leave do employees get?"


def search(q, flt=None, k=4):
    v = embedder.encode(q, normalize_embeddings=True).tolist()
    return [h.payload for h in client.query_points("policy_docs", query=v, limit=k, query_filter=flt).points]


def ask(q, flt=None):
    chunks = search(q, flt)
    prompt = TEMPLATE.format(context="\n\n".join(block(c) for c in chunks), question=q)
    return call_llm(prompt).replace("\n", " "), chunks


HR_CURRENT = Filter(must=[FieldCondition(key="department", match=MatchValue(value="HR")),
                          FieldCondition(key="year", range=Range(gte=2025))])

md = ["# Task 2 - Metadata filtering", "", f"Question: **{Q}**", "",
      "Filter: `department = HR` AND `year >= 2025`", ""]
for name, flt in [("BEFORE (no filter)", None), ("AFTER (department=HR, year>=2025)", HR_CURRENT)]:
    ans, chunks = ask(Q, flt)
    srcs = [f"{c['source']} ({c['department']}, {c['year']})" for c in chunks]
    print(f"\n{name}\n  sources: {srcs}\n  answer : {ans[:220]}")
    md += [f"## {name}", "", "Sources: " + "; ".join(srcs), "", f"Answer: {ans}", ""]
    if flt is None:
        before_has_old = any(c["source"] == "leave_policy_2023.txt" for c in chunks)
    else:
        after_has_old = any(c["source"] == "leave_policy_2023.txt" for c in chunks)

result = f"Outdated leave_policy_2023.txt in context: before={before_has_old}, after={after_has_old}"
print("\n" + result)
md.append(f"**{result}**")
Path("task2_filters.md").write_text("\n".join(md), encoding="utf-8")
print("Saved task2_filters.md")
"""Print 5 v3 answers with their retrieved context, for manual faithfulness checking."""
import json
from pathlib import Path

data = json.loads(Path("task3_answers.json").read_text(encoding="utf-8"))
picked = [x for x in data if x["version"].startswith("v3") and x["expected"]][:5]
lines = []
for i, x in enumerate(picked, 1):
    lines += [f"=== A{i}: {x['question']}", f"ANSWER: {x['answer']}", "CONTEXT:"]
    lines += [c[:230] for c in x["contexts"]]
    lines.append("")
text = "\n".join(lines)
print(text)
Path("task3_faithfulness_input.txt").write_text(text, encoding="utf-8")
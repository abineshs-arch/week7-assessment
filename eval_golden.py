"""Task 4: verify golden.jsonl, run pipeline on 15 questions, RAGAS 4 metrics, log the experiment.
Usage: py eval_golden.py <experiment_name> "<what changed>" """
import json, re, sys, warnings
from pathlib import Path

warnings.filterwarnings("ignore")
from dotenv import dotenv_values
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from ragas import EvaluationDataset, RunConfig, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

from llm_utils import call_llm
from rag_basic import FALLBACK, THRESHOLD, block, client, retrieve

EXP = sys.argv[1] if len(sys.argv) > 1 else "baseline"
NOTE = sys.argv[2] if len(sys.argv) > 2 else ""
M = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
V3 = ("Answer ONLY from the context below. Do not use outside knowledge.\n"
      "Cite the source after each fact in the format [filename, p.N], exactly as shown in the context.\n"
      "If the context does not contain the answer, reply exactly: I don't have information on that.\n\n"
      "Context:\n{context}\n\nQuestion: {question}\nAnswer:")
gold = [json.loads(l) for l in Path("golden.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

# 1. verify every answer exists in the indexed corpus
norm = lambda s: re.sub(r"\s+", " ", s).lower()
all_chunks = [(p.payload["source"], int(p.payload["page"]), norm(p.payload["text"]))
              for p in client.scroll("policy_docs", limit=100_000, with_payload=True)[0]]
bad = 0
for g in gold:
    for s in g["sources"]:
        where = {(src, pg) for src, pg, t in all_chunks if norm(s["evidence"]) in t}
        ok = not where if g["category"] == "unanswerable" else (s["doc"], s["page"]) in where
        if not ok:
            bad += 1
            print(f"VERIFY FAIL {g['id']}: '{s['evidence']}' in {s['doc']} p{s['page']} -> found {sorted(where)}")
print(f"Verified {len(gold)} questions, {bad} problems\n")

# 2. run the pipeline
rows = []
for g in gold:
    chunks = retrieve(g["question"], 4)
    best = chunks[0]["score"] if chunks else 0.0
    ans = FALLBACK if best < THRESHOLD else call_llm(V3.format(context="\n\n".join(block(c) for c in chunks),
                                                                question=g["question"]))
    got = {(c["source"], int(c["page"])) for c in chunks}
    need = [(s["doc"], s["page"]) for s in g["sources"] if s["doc"] != "none"]
    rows.append(dict(id=g["id"], category=g["category"], question=g["question"], reference=g["answer"],
                     answer=ans.replace("\n", " "), best=round(best, 2), contexts=[block(c) for c in chunks],
                     hit=all(n in got for n in need) if need else None,
                     refused="don't have information" in ans.lower()))
    print(f"{g['id']} {g['category']:12} hit={rows[-1]['hit']} best={best:.2f} | {ans[:80]}")
Path(f"eval_{EXP}.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")

# 3. RAGAS on the 12 answerable questions
ans_rows = [r for r in rows if r["category"] != "unanswerable"]
una = [r for r in rows if r["category"] == "unanswerable"]
judge = LangchainLLMWrapper(ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0,
                            google_api_key=dotenv_values(".env")["GEMINI_API_KEY"]))
emb = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
answer_relevancy.strictness = 1
data = [dict(user_input=r["question"], response=r["answer"], retrieved_contexts=r["contexts"],
             reference=r["reference"]) for r in ans_rows]
df = evaluate(EvaluationDataset.from_list(data), metrics=[faithfulness, answer_relevancy, context_precision,
              context_recall], llm=judge, embeddings=emb,
              run_config=RunConfig(max_workers=2, timeout=180, max_retries=10, max_wait=90)).to_pandas()
df.insert(0, "id", [r["id"] for r in ans_rows])
df.to_csv(f"ragas_{EXP}.csv", index=False)
print("\n" + df[["id"] + M].round(2).to_string())

mean = df[M].mean()
hit = sum(r["hit"] for r in ans_rows) / len(ans_rows)
ref = f"{sum(r['refused'] for r in una)}/{len(una)}"
false_ref = f"{sum(r['refused'] for r in ans_rows)}/{len(ans_rows)}"
print(f"\nSUMMARY {EXP}: hit@4 {hit:.2f} | " + " | ".join(f"{k} {mean[k]:.2f}" for k in M)
      + f" | refusal accuracy {ref} | false refusals {false_ref}")

log = Path("experiment_log.md")
if not log.exists():
    log.write_text("# Experiment log\n\n| Experiment | Change | Hit@4 | Faithfulness | Answer relevancy | "
                   "Context precision | Context recall | Refusal accuracy | False refusals |\n"
                   "|---|---|---|---|---|---|---|---|---|\n", encoding="utf-8")
with log.open("a", encoding="utf-8") as f:
    f.write(f"| {EXP} | {NOTE} | {hit:.2f} | " + " | ".join(f"{mean[k]:.2f}" for k in M) + f" | {ref} | {false_ref} |\n")
print("Appended to experiment_log.md")
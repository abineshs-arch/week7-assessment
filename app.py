"""Task 3: POST /ask (API key protected) -> answer + sources + confidence; clear errors."""
import re
import secrets
from pathlib import Path

from dotenv import dotenv_values
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from llm_utils import call_llm
from prompts import V3
from rag_basic import THRESHOLD, block, retrieve

API_KEY = (dotenv_values(Path(__file__).parent / ".env").get("KA_API_KEY") or "").strip()
# Finds every "file.ext, p. N" pair, also when several are inside one bracket: [a.docx, p. 1; b.pdf, p. 6]
CITE = re.compile(r"([\w\-.]+\.(?:pdf|docx|txt|csv)),?\s*(?:p\.?|page)\s*(\d+)", re.I)

app = FastAPI(title="Yoho Policy Q&A Assistant", version="1.0",
              description="Answers only from company policy documents, with citations.")
api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


def check_key(key: str | None = Security(api_key)):
    if not key or not API_KEY or not secrets.compare_digest(key.strip(), API_KEY):
        raise HTTPException(401, "Missing or invalid API key (send it in the X-API-Key header)")


def validate(answer, chunks):
    """Return (valid, fake) citation lists. Fake = (file, page) not in the retrieved chunks."""
    allowed = {(c["source"].lower(), int(c["page"])) for c in chunks}
    cites = [(f, int(p)) for f, p in CITE.findall(answer)]
    valid = [c for c in cites if (c[0].lower(), c[1]) in allowed]
    fake = [c for c in cites if (c[0].lower(), c[1]) not in allowed]
    return valid, fake


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500, examples=["What is the minimum password length?"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", dependencies=[Depends(check_key)])
def ask(req: AskRequest):
    chunks = retrieve(req.question, 4)
    best = round(chunks[0]["score"], 2) if chunks else 0.0
    if not chunks or best < THRESHOLD:
        raise HTTPException(404, f"No relevant documents found for this question (best score {best}). "
                                 "I don't have information on that.")
    try:
        answer = call_llm(V3.format(context="\n\n".join(block(c) for c in chunks), question=req.question))
    except Exception:
        raise HTTPException(503, "The language model is unavailable right now. Please try again later.")
    valid, fake = validate(answer, chunks)
    keys = {(f.lower(), p) for f, p in valid}
    sources, seen = [], set()
    for c in chunks:
        k = (c["source"].lower(), int(c["page"]))
        if k in keys and k not in seen:
            seen.add(k)
            sources.append(dict(file=c["source"], page=int(c["page"]), snippet=c["text"][:200]))
    return {"answer": answer.strip(), "sources": sources, "confidence": best,
            "fake_citations": [f"{f}, p.{p}" for f, p in fake]}
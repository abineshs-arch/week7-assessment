"""API tests (FastAPI TestClient, no running server needed)."""
from dotenv import dotenv_values
from fastapi.testclient import TestClient

import app

KEY = dotenv_values(".env")["KA_API_KEY"]
client = TestClient(app.app)
Q = {"question": "What is the minimum password length?"}


def test_answer_has_sources_and_confidence():
    r = client.post("/ask", json=Q, headers={"X-API-Key": KEY})
    body = r.json()
    print("\n200 ->", body["answer"][:100], "| sources:", [(s["file"], s["page"]) for s in body["sources"]],
          "| confidence:", body["confidence"])
    assert r.status_code == 200 and "12" in body["answer"] and body["sources"] and body["confidence"] > 0.35


def test_off_topic_gives_clear_404():
    r = client.post("/ask", json={"question": "Who won the world cup?"}, headers={"X-API-Key": KEY})
    print("\n404 ->", r.json()["detail"])
    assert r.status_code == 404 and "No relevant documents" in r.json()["detail"]


def test_missing_key_401():
    assert client.post("/ask", json=Q).status_code == 401


def test_wrong_key_401():
    assert client.post("/ask", json=Q, headers={"X-API-Key": "wrong"}).status_code == 401


def test_validator_flags_fake_citation():
    chunks = [{"source": "it_security_policy.docx", "page": 1}]
    valid, fake = app.validate("12 characters [it_security_policy.docx, p. 1; hr_manual.pdf, p. 9]", chunks)
    assert valid == [("it_security_policy.docx", 1)] and fake == [("hr_manual.pdf", 9)]
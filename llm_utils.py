"""Shared Gemini helper: answer cache, model fallback on daily quota, retries on busy/network errors."""
import hashlib
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

CACHE = Path(__file__).parent / "llm_cache.json"

load_dotenv()
llm = genai.Client(http_options=types.HttpOptions(timeout=60_000))


def is_net_error(e):
    """True for connection drops/timeouts from httpx, httpx2, httpcore, httpcore2 or the OS."""
    mod = type(e).__module__ or ""
    return mod.startswith(("httpx", "httpcore")) or isinstance(e, (ConnectionError, TimeoutError))


def _retry(fn, tries=6):
    wait = 5
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            if not is_net_error(e) or i == tries - 1:
                raise
            print(f"   (network error {type(e).__name__}, retry in {wait}s)")
            time.sleep(wait)
            wait *= 2


SKIP = ["tts", "audio", "live", "image", "embedding", "gemma", "gemini-1"]
_rank = lambda n: 0 if ("flash" in n and "lite" not in n) else (1 if "flash-lite" in n else 2)
MODELS = sorted((m.name for m in _retry(lambda: list(llm.models.list())) if "gemini" in m.name
                 and "generateContent" in (m.supported_actions or [])
                 and not any(s in m.name for s in SKIP)), key=_rank)
_dead = set()
_cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def call_llm(prompt):
    key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if key in _cache:
        return _cache[key]
    for model in MODELS:
        if model in _dead:
            continue
        wait = 10
        for _ in range(6):
            try:
                text = llm.models.generate_content(model=model, contents=prompt).text.strip()
                _cache[key] = text
                CACHE.write_text(json.dumps(_cache, indent=1, ensure_ascii=False), encoding="utf-8")
                time.sleep(2)
                return text
            except (errors.ServerError, errors.ClientError) as e:
                code = getattr(e, "code", None)
                if code == 404 or (code == 429 and "PerDay" in str(e)):
                    print(f"   ({model} unavailable / daily quota used -> next model)")
                    _dead.add(model)
                    break
                if not (isinstance(e, errors.ServerError) or code == 429):
                    raise
                print(f"   ({model} busy, retry in {wait}s)")
            except Exception as e:
                if not is_net_error(e):
                    raise
                print(f"   (network error {type(e).__name__}, retry in {wait}s)")
            time.sleep(wait)
            wait *= 2
        else:
            _dead.add(model)
    raise RuntimeError("All Gemini models are busy, out of quota, or the network is down")
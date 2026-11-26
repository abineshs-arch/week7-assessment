"""Pipeline configuration and Reciprocal Rank Fusion (pure Python, no models)."""
import json
from collections import defaultdict
from dataclasses import dataclass, fields
from pathlib import Path


@dataclass
class Config:
    use_bm25: bool = True
    use_reranker: bool = True
    top_k: int = 5
    candidates: int = 50
    rrf_k: int = 60
    w_bm25: float = 0.5

    def __post_init__(self):
        if not isinstance(self.use_bm25, bool) or not isinstance(self.use_reranker, bool):
            raise ValueError("use_bm25 and use_reranker must be true or false")
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        if self.candidates < self.top_k:
            raise ValueError("candidates must be >= top_k")
        if self.rrf_k < 1:
            raise ValueError("rrf_k must be at least 1")
        if not 0 <= self.w_bm25 <= 1:
            raise ValueError("w_bm25 must be between 0 and 1")

    @classmethod
    def from_dict(cls, d):
        unknown = set(d) - {f.name for f in fields(cls)}
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        return cls(**d)

    @classmethod
    def load(cls, path="config.json"):
        p = Path(path)
        return cls.from_dict(json.loads(p.read_text(encoding="utf-8"))) if p.exists() else cls()

    def name(self):
        parts = ["hybrid" if self.use_bm25 else "vector"]
        if self.use_reranker:
            parts.append(f"rerank{self.candidates}")
        return "+".join(parts)


def rrf(rankings, k=60, weights=None):
    """score(doc) = sum over lists of weight / (k + rank), rank starting at 1."""
    weights = weights or [1.0] * len(rankings)
    if len(weights) != len(rankings):
        raise ValueError("one weight per ranking list")
    scores = defaultdict(float)
    for ranking, w in zip(rankings, weights):
        for rank, doc in enumerate(ranking, 1):
            scores[doc] += w / (k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])
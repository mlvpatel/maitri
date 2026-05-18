"""Lightweight keyword retriever over the local evidence corpus.

For the hackathon we keep retrieval deterministic and offline. The corpus is
small enough that a token overlap score is sufficient to drive the demo while
keeping the audit log trivially reproducible.
"""

from __future__ import annotations

import re
from collections import Counter

from ..schemas import EvidenceChunk, EvidencePack
from .corpus import all_chunks


_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def retrieve(case_id: str, query: str, top_k: int = 5) -> EvidencePack:
    q = Counter(_tokens(query))
    scored: list[tuple[float, EvidenceChunk]] = []
    for chunk in all_chunks():
        toks = _tokens(chunk.text + " " + chunk.title)
        overlap = sum(min(q[t], toks.count(t)) for t in q)
        if overlap == 0:
            continue
        score = overlap / (1 + 0.01 * len(toks))
        scored.append((score, chunk))
    scored.sort(key=lambda x: -x[0])
    selected = [c for _, c in scored[:top_k]]
    if not selected:
        selected = all_chunks()[:top_k]
    return EvidencePack(case_id=case_id, query=query, chunks=selected)

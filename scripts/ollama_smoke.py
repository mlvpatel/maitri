"""Single call smoke test against a local Ollama hosted Gemma 4 weight.

Proves the provider switch in the shared client works without paying the cost
of running the full seven agent pipeline on CPU.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

os.environ["MAITRI_PROVIDER"] = "ollama"

from maitri.gemma_client import GemmaClient  # noqa: E402


def main() -> int:
    t0 = time.perf_counter()
    with GemmaClient() as client:
        resp = client.chat(
            messages=[{"role": "user", "content": "Reply with exactly the two characters: OK"}],
            agent="smoke",
            temperature=0.0,
            max_tokens=8,
        )
    elapsed = time.perf_counter() - t0
    print(f"provider=ollama model={resp.model} content={resp.content!r} latency_ms={int(elapsed*1000)}")
    return 0 if resp.content.strip() else 1


if __name__ == "__main__":
    sys.exit(main())

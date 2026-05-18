"""Append only audit log backed by SQLite and mirrored to JSONL.

The SQLite table has no UPDATE or DELETE entry points exposed. The JSONL mirror
exists so that a judge can inspect the immutable artifact directly without a
SQLite client.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from .config import get_settings


_DDL = """
CREATE TABLE IF NOT EXISTS audit (
    ts_unix REAL NOT NULL,
    case_id TEXT NOT NULL,
    call_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    latency_ms INTEGER NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS audit_case ON audit(case_id);
"""


class AuditLog:
    """Thread safe append only writer."""

    def __init__(self, sqlite_path: Path | None = None, jsonl_path: Path | None = None) -> None:
        s = get_settings()
        self._sqlite_path = Path(sqlite_path or s.audit_sqlite)
        self._jsonl_path = Path(jsonl_path or s.audit_jsonl)
        self._lock = threading.Lock()
        self._sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self._jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._sqlite_path) as cx:
            cx.executescript(_DDL)

    def record(self, case_id: str, entry: dict[str, Any]) -> None:
        row = {
            "ts_unix": time.time(),
            "case_id": case_id,
            "call_id": entry.get("call_id", ""),
            "agent": entry.get("agent", ""),
            "model": entry.get("model", ""),
            "prompt_tokens": int(entry.get("prompt_tokens", 0)),
            "completion_tokens": int(entry.get("completion_tokens", 0)),
            "cost_usd": float(entry.get("cost_usd", 0.0)),
            "latency_ms": int(entry.get("latency_ms", 0)),
            "payload_json": json.dumps(entry, ensure_ascii=False),
        }
        with self._lock:
            with sqlite3.connect(self._sqlite_path) as cx:
                cx.execute(
                    "INSERT INTO audit("
                    "ts_unix, case_id, call_id, agent, model,"
                    " prompt_tokens, completion_tokens, cost_usd, latency_ms, payload_json"
                    ") VALUES(?,?,?,?,?,?,?,?,?,?)",
                    tuple(row[k] for k in (
                        "ts_unix", "case_id", "call_id", "agent", "model",
                        "prompt_tokens", "completion_tokens", "cost_usd", "latency_ms",
                        "payload_json",
                    )),
                )
            with self._jsonl_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    def case_rows(self, case_id: str) -> list[dict[str, Any]]:
        with sqlite3.connect(self._sqlite_path) as cx:
            cx.row_factory = sqlite3.Row
            rows = cx.execute(
                "SELECT * FROM audit WHERE case_id = ? ORDER BY ts_unix ASC",
                (case_id,),
            ).fetchall()
        out: list[dict[str, Any]] = []
        for r in rows:
            d = dict(r)
            d["payload"] = json.loads(d.pop("payload_json"))
            out.append(d)
        return out

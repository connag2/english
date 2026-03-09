from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models import AppStats, WordEntry

DEFAULT_DATA = {
    "words": [],
    "meta": {"version": 1},
    "stats": {"today_studied": 0, "recent_wrong_words": []},
}


class Storage:
    def __init__(self, path: str = "data/words.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def ensure_file(self) -> None:
        if not self.path.exists():
            self._write_raw(DEFAULT_DATA)

    def load_raw(self) -> dict[str, Any]:
        self.ensure_file()
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or "words" not in data:
                raise ValueError("invalid schema")
            data.setdefault("meta", {"version": 1})
            data.setdefault("stats", {"today_studied": 0, "recent_wrong_words": []})
            return data
        except Exception:
            backup = self.path.with_suffix(".broken.json")
            try:
                self.path.replace(backup)
            except Exception:
                pass
            self._write_raw(DEFAULT_DATA)
            return json.loads(json.dumps(DEFAULT_DATA))

    def load_words(self) -> list[WordEntry]:
        data = self.load_raw()
        words = [WordEntry.from_dict(w) for w in data.get("words", [])]
        return [w for w in words if w.word and w.meanings]

    def load_stats(self) -> AppStats:
        data = self.load_raw()
        return AppStats.from_dict(data.get("stats"))

    def save_words(self, words: list[WordEntry], stats: AppStats | None = None) -> None:
        current = self.load_raw()
        payload = {
            "words": [w.to_dict() for w in words],
            "meta": current.get("meta", {"version": 1}),
            "stats": (stats.to_dict() if stats is not None else current.get("stats", DEFAULT_DATA["stats"])),
        }
        self._write_raw(payload)

    def save_stats(self, stats: AppStats, words: list[WordEntry] | None = None) -> None:
        current = self.load_raw()
        payload = {
            "words": [w.to_dict() for w in (words if words is not None else [WordEntry.from_dict(w) for w in current.get("words", [])])],
            "meta": current.get("meta", {"version": 1}),
            "stats": stats.to_dict(),
        }
        self._write_raw(payload)

    def _write_raw(self, payload: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

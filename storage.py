from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models import WordEntry

DEFAULT_DATA = {"words": [], "meta": {"version": 1}}


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
            return data
        except Exception:
            backup = self.path.with_suffix(".broken.json")
            try:
                self.path.replace(backup)
            except Exception:
                pass
            self._write_raw(DEFAULT_DATA)
            return DEFAULT_DATA.copy()

    def load_words(self) -> list[WordEntry]:
        data = self.load_raw()
        words = [WordEntry.from_dict(w) for w in data.get("words", [])]
        return [w for w in words if w.word and w.meanings]

    def save_words(self, words: list[WordEntry]) -> None:
        payload = {
            "words": [w.to_dict() for w in words],
            "meta": {"version": 1},
        }
        self._write_raw(payload)

    def _write_raw(self, payload: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

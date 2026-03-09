from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class WordEntry:
    word: str
    meanings: list[str]
    level: int = 0
    correct: int = 0
    wrong: int = 0
    last_review: str | None = None
    next_review: str | None = None
    favorite: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "word": self.word,
            "meanings": self.meanings,
            "level": self.level,
            "correct": self.correct,
            "wrong": self.wrong,
            "last_review": self.last_review,
            "next_review": self.next_review,
            "favorite": self.favorite,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WordEntry":
        return cls(
            word=str(data.get("word", "")).strip().lower(),
            meanings=[str(m).strip() for m in data.get("meanings", []) if str(m).strip()],
            level=int(data.get("level", 0)),
            correct=int(data.get("correct", 0)),
            wrong=int(data.get("wrong", 0)),
            last_review=data.get("last_review"),
            next_review=data.get("next_review"),
            favorite=bool(data.get("favorite", False)),
            created_at=str(data.get("created_at") or datetime.now().isoformat(timespec="seconds")),
        )


@dataclass
class AppStats:
    today_studied: int = 0
    recent_wrong_words: list[str] = field(default_factory=list)

    def mark_wrong(self, word: str) -> None:
        if word in self.recent_wrong_words:
            self.recent_wrong_words.remove(word)
        self.recent_wrong_words.insert(0, word)
        self.recent_wrong_words = self.recent_wrong_words[:5]

    def mark_studied(self) -> None:
        self.today_studied += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "today_studied": self.today_studied,
            "recent_wrong_words": self.recent_wrong_words,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AppStats":
        if not isinstance(data, dict):
            return cls()
        return cls(
            today_studied=int(data.get("today_studied", 0)),
            recent_wrong_words=[str(x) for x in data.get("recent_wrong_words", [])][:5],
        )


def today_iso() -> str:
    return date.today().isoformat()

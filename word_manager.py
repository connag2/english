from __future__ import annotations

from dataclasses import dataclass, field

from models import WordEntry
from storage import Storage


@dataclass
class ParseResult:
    merged: dict[str, set[str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class WordManager:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.words: dict[str, WordEntry] = {}
        self.reload()

    def reload(self) -> None:
        self.words = {w.word: w for w in self.storage.load_words()}

    def all_words(self) -> list[WordEntry]:
        return list(self.words.values())

    def parse_bulk(self, text: str) -> ParseResult:
        result = ParseResult()
        lines = text.splitlines()
        for idx, line in enumerate(lines, start=1):
            s = line.strip()
            if not s:
                continue
            if "=" not in s:
                result.errors.append(f"{idx}: '=' 없음 -> {line}")
                continue
            left, right = s.split("=", 1)
            word = left.strip().lower()
            if not word:
                result.errors.append(f"{idx}: 단어 비어 있음")
                continue
            meanings = {m.strip() for m in right.split("|") if m.strip()}
            if not meanings:
                result.errors.append(f"{idx}: 뜻 비어 있음")
                continue
            result.merged.setdefault(word, set()).update(meanings)
        return result

    def apply_parse_result(self, parsed: ParseResult) -> None:
        for word, meanings in parsed.merged.items():
            if word in self.words:
                merged = set(self.words[word].meanings)
                merged.update(meanings)
                self.words[word].meanings = sorted(merged)
            else:
                self.words[word] = WordEntry(word=word, meanings=sorted(meanings))
        self._save()

    def add_single(self, word: str, meanings_text: str) -> str | None:
        text = f"{word}={meanings_text}"
        parsed = self.parse_bulk(text)
        if parsed.errors:
            return parsed.errors[0]
        self.apply_parse_result(parsed)
        return None

    def delete_word(self, word: str) -> None:
        self.words.pop(word, None)
        self._save()

    def upsert_word(self, old_word: str, new_word: str, meanings: list[str]) -> str | None:
        cleaned_word = new_word.strip().lower()
        cleaned_meanings = sorted({m.strip() for m in meanings if m.strip()})
        if not cleaned_word or not cleaned_meanings:
            return "단어/뜻이 비어 있습니다."

        existing = self.words.get(old_word)
        created_at = existing.created_at if existing else None

        if old_word != cleaned_word and old_word in self.words:
            self.words.pop(old_word)

        entry = self.words.get(cleaned_word, WordEntry(word=cleaned_word, meanings=[]))
        entry.meanings = cleaned_meanings
        if created_at:
            entry.created_at = created_at
        self.words[cleaned_word] = entry
        self._save()
        return None

    def _save(self) -> None:
        self.storage.save_words(list(self.words.values()))

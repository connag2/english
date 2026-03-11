from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date

from models import WordEntry
from review_scheduler import due_today, next_review_date


@dataclass
class Question:
    word: WordEntry
    prompt: str
    answer: str
    choices: list[str] | None = None


class StudyEngine:
    def __init__(self, words: list[WordEntry]) -> None:
        self.words = words
        self.wrong_words: list[str] = []

    def select_words(self, review_only: bool = False, limit: int = 30) -> list[WordEntry]:
        if review_only:
            due = [w for w in self.words if due_today(w.next_review)]
            random.shuffle(due)
            return due[:limit]
        items = self.words[:]
        random.shuffle(items)
        return items[:limit]

    def build_question(self, target: WordEntry, mode: str, pool: list[WordEntry]) -> Question:
        if mode == "mcq":
            answer = target.meanings[0]
            distractors: list[str] = []
            seen_meanings = {answer}
            for w in pool:
                if w.word == target.word:
                    continue
                if w.meanings and w.meanings[0] not in seen_meanings:
                    distractors.append(w.meanings[0])
                    seen_meanings.add(w.meanings[0])
            random.shuffle(distractors)
            choices = [answer] + distractors[:3]
            random.shuffle(choices)
            return Question(word=target, prompt=target.word, answer=answer, choices=choices)
        return Question(word=target, prompt=target.word, answer=", ".join(target.meanings))

    def mark_result(self, word: WordEntry, correct: bool) -> None:
        word.last_review = date.today().isoformat()
        if correct:
            word.correct += 1
            word.level = min(5, word.level + 1)
            word.next_review = next_review_date(word.level)
        else:
            word.wrong += 1
            word.level = max(0, word.level - 1)
            word.next_review = date.today().isoformat()
            self.wrong_words.append(word.word)

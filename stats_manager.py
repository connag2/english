from __future__ import annotations

from models import AppStats


class StatsManager:
    def __init__(self) -> None:
        self.stats = AppStats()

    def mark_studied(self) -> None:
        self.stats.mark_studied()

    def mark_wrong(self, word: str) -> None:
        self.stats.mark_wrong(word)

    @property
    def today_studied(self) -> int:
        return self.stats.today_studied

    @property
    def recent_wrong_words(self) -> list[str]:
        return self.stats.recent_wrong_words

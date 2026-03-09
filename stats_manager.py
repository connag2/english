from __future__ import annotations

from models import AppStats
from storage import Storage


class StatsManager:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.stats = self.storage.load_stats()

    def mark_studied(self) -> None:
        self.stats.mark_studied()
        self._save()

    def mark_wrong(self, word: str) -> None:
        self.stats.mark_wrong(word)
        self._save()

    def _save(self) -> None:
        self.storage.save_stats(self.stats)

    @property
    def today_studied(self) -> int:
        return self.stats.today_studied

    @property
    def recent_wrong_words(self) -> list[str]:
        return self.stats.recent_wrong_words

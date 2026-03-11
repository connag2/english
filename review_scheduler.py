from __future__ import annotations

from datetime import date, timedelta

LEVEL_INTERVALS = {
    0: 1,
    1: 3,
    2: 7,
    3: 14,
}


def interval_for_level(level: int) -> int:
    if level >= 4:
        return 30
    return LEVEL_INTERVALS.get(max(0, level), 1)


def next_review_date(level: int, base: date | None = None) -> str:
    base = base or date.today()
    return (base + timedelta(days=interval_for_level(level))).isoformat()


def due_today(next_review: str | None, today: date | None = None) -> bool:
    if not next_review:
        return True
    today = today or date.today()
    try:
        d = date.fromisoformat(next_review)
    except ValueError:
        return True
    return d <= today

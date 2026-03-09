from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from stats_manager import StatsManager
from storage import Storage
from word_manager import WordManager
from ui.add_words_view import AddWordsView
from ui.result_view import ResultView
from ui.study_view import StudyView
from ui.wordbook_view import WordbookView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VocaFlow")
        self.resize(920, 680)

        self.storage = Storage()
        self.manager = WordManager(self.storage)
        self.stats = StatsManager(self.storage)
        self.last_wrong_words: list[str] = []

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self.dashboard = QLabel()
        root.addWidget(self.dashboard)

        nav = QHBoxLayout()
        self.btn_study = QPushButton("학습 시작")
        self.btn_review = QPushButton("복습 시작")
        self.btn_add = QPushButton("단어 추가")
        self.btn_book = QPushButton("단어장 보기")
        nav.addWidget(self.btn_study)
        nav.addWidget(self.btn_review)
        nav.addWidget(self.btn_add)
        nav.addWidget(self.btn_book)
        root.addLayout(nav)

        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        self.home = QWidget()
        self.home.setLayout(QVBoxLayout())
        self.home.layout().addWidget(QLabel("상단 버튼으로 메뉴를 선택하세요."))

        self.add_view = AddWordsView(self.manager, self._refresh_all)
        self.book_view = WordbookView(self.manager, self._refresh_all)
        self.study_view = StudyView(self._on_study_finished, self._on_study_progress)
        self.result_view = ResultView(self._retry_wrong, self._go_home)

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.add_view)
        self.stack.addWidget(self.book_view)
        self.stack.addWidget(self.study_view)
        self.stack.addWidget(self.result_view)

        self.btn_add.clicked.connect(lambda: self.stack.setCurrentWidget(self.add_view))
        self.btn_book.clicked.connect(self._open_wordbook)
        self.btn_study.clicked.connect(self._start_study)
        self.btn_review.clicked.connect(self._start_review)

        self._refresh_all()

    def _refresh_all(self) -> None:
        self.manager.reload()
        self.book_view.refresh()
        total = len(self.manager.all_words())
        today = date.today().isoformat()
        due = len([w for w in self.manager.all_words() if not w.next_review or w.next_review <= today])
        wrong = ", ".join(self.stats.recent_wrong_words) if self.stats.recent_wrong_words else "없음"
        self.dashboard.setText(
            f"전체 단어: {total} | 오늘 복습 필요: {due} | 오늘 학습: {self.stats.today_studied} | 최근 오답: {wrong}"
        )

    def _open_wordbook(self) -> None:
        self.book_view.refresh()
        self.stack.setCurrentWidget(self.book_view)

    def _start_study(self) -> None:
        self.stack.setCurrentWidget(self.study_view)
        self.study_view.start(self.manager.all_words(), mode="meaning", review_only=False)

    def _start_review(self) -> None:
        self.stack.setCurrentWidget(self.study_view)
        self.study_view.start(self.manager.all_words(), mode="mcq", review_only=True)

    def _on_study_progress(self, word: str, is_correct: bool) -> None:
        self.stats.mark_studied()
        if not is_correct:
            self.stats.mark_wrong(word)

    def _on_study_finished(self, wrong_words: list[str], total: int, correct: int) -> None:
        self.last_wrong_words = wrong_words
        self.storage.save_words(self.manager.all_words(), self.stats.stats)
        self.result_view.set_result(total, correct, total - correct)
        self.stack.setCurrentWidget(self.result_view)
        self._refresh_all()

    def _retry_wrong(self) -> None:
        wrong_set = set(self.last_wrong_words)
        words = [w for w in self.manager.all_words() if w.word in wrong_set]
        self.stack.setCurrentWidget(self.study_view)
        self.study_view.start(words, mode="mcq", review_only=False)

    def _go_home(self) -> None:
        self.stack.setCurrentWidget(self.home)
        self._refresh_all()

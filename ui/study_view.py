from __future__ import annotations

from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from models import WordEntry
from study_engine import Question, StudyEngine


class StudyView(QWidget):
    def __init__(self, on_finished, on_progress) -> None:
        super().__init__()
        self.on_finished = on_finished
        self.on_progress = on_progress

        self.engine: StudyEngine | None = None
        self.questions: list[Question] = []
        self.index = 0
        self.correct = 0
        self.mode = "meaning"

        v = QVBoxLayout(self)
        self.progress = QLabel("0/0")
        self.prompt = QLabel("문제")
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("뜻 입력")

        self.choice_group = QButtonGroup(self)
        self.choice_buttons = [QRadioButton() for _ in range(4)]
        for b in self.choice_buttons:
            self.choice_group.addButton(b)

        row = QHBoxLayout()
        self.check_btn = QPushButton("정답 확인")
        self.unknown_btn = QPushButton("모르겠어요")
        self.next_btn = QPushButton("다음 문제")
        self.check_btn.clicked.connect(self._check)
        self.unknown_btn.clicked.connect(self._unknown)
        self.next_btn.clicked.connect(self._next)
        row.addWidget(self.check_btn)
        row.addWidget(self.unknown_btn)
        row.addWidget(self.next_btn)

        v.addWidget(self.progress)
        v.addWidget(self.prompt)
        v.addWidget(self.answer_input)
        for b in self.choice_buttons:
            v.addWidget(b)
            b.hide()
        v.addLayout(row)

    def start(self, words: list[WordEntry], mode: str = "meaning", review_only: bool = False) -> None:
        self.engine = StudyEngine(words)
        pool = self.engine.select_words(review_only=review_only)
        self.mode = mode
        self.questions = [self.engine.build_question(w, mode, pool) for w in pool]
        self.index = 0
        self.correct = 0
        if not self.questions:
            QMessageBox.information(self, "안내", "출제할 단어가 없습니다.")
            self.on_finished([], 0, 0)
            return
        self._render()

    def _render(self) -> None:
        q = self.questions[self.index]
        self.progress.setText(f"{self.index + 1}/{len(self.questions)}")
        self.prompt.setText(q.prompt)
        self.answer_input.clear()
        if q.choices:
            self.answer_input.hide()
            for i, b in enumerate(self.choice_buttons):
                b.setText(q.choices[i] if i < len(q.choices) else "")
                b.setChecked(False)
                b.show()
        else:
            self.answer_input.show()
            for b in self.choice_buttons:
                b.hide()

    def _check(self) -> None:
        q = self.questions[self.index]
        if q.choices:
            selected = ""
            for b in self.choice_buttons:
                if b.isChecked():
                    selected = b.text()
            is_correct = selected == q.answer
        else:
            guess = self.answer_input.text().strip()
            is_correct = guess and guess in q.answer

        self.engine.mark_result(q.word, bool(is_correct))
        self.on_progress(q.word.word, bool(is_correct))
        if is_correct:
            self.correct += 1
        else:
            QMessageBox.information(self, "정답", f"정답: {q.answer}")

    def _unknown(self) -> None:
        q = self.questions[self.index]
        self.engine.mark_result(q.word, False)
        self.on_progress(q.word.word, False)
        QMessageBox.information(self, "정답", f"정답: {q.answer}")

    def _next(self) -> None:
        if self.index >= len(self.questions) - 1:
            wrong = len(self.questions) - self.correct
            self.on_finished(self.engine.wrong_words, len(self.questions), self.correct)
            return
        self.index += 1
        self._render()

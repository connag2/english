from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ResultView(QWidget):
    def __init__(self, on_retry_wrong, on_close) -> None:
        super().__init__()
        self.on_retry_wrong = on_retry_wrong
        self.on_close = on_close

        v = QVBoxLayout(self)
        self.summary = QLabel("결과")
        retry = QPushButton("오답만 다시 풀기")
        close = QPushButton("종료")
        retry.clicked.connect(self.on_retry_wrong)
        close.clicked.connect(self.on_close)
        v.addWidget(self.summary)
        v.addWidget(retry)
        v.addWidget(close)

    def set_result(self, total: int, correct: int, wrong: int) -> None:
        rate = 0 if total == 0 else int(correct * 100 / total)
        self.summary.setText(
            f"총 {total}문제\n맞음 {correct}\n틀림 {wrong}\n정답률 {rate}%"
        )

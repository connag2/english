from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from word_manager import ParseResult, WordManager


class AddWordsView(QWidget):
    def __init__(self, word_manager: WordManager, on_saved) -> None:
        super().__init__()
        self.word_manager = word_manager
        self.on_saved = on_saved
        self.last_parsed = ParseResult()

        root = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_single_tab(), "직접 추가")
        self.tabs.addTab(self._build_bulk_tab(), "여러 줄 추가")
        self.tabs.addTab(self._build_file_tab(), "파일 불러오기")
        root.addWidget(self.tabs)

    def _build_single_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("apple")
        self.meaning_input = QLineEdit()
        self.meaning_input.setPlaceholderText("사과|과실")
        save_btn = QPushButton("추가")
        save_btn.clicked.connect(self._save_single)
        v.addWidget(QLabel("단어"))
        v.addWidget(self.word_input)
        v.addWidget(QLabel("뜻(|로 구분 가능)"))
        v.addWidget(self.meaning_input)
        v.addWidget(save_btn)
        return w

    def _build_bulk_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        self.bulk_input = QTextEdit()
        self.bulk_input.setPlaceholderText("apple=사과\nrun=달리다|운영하다")
        row = QHBoxLayout()
        preview = QPushButton("미리보기")
        preview.clicked.connect(self._preview_bulk)
        save = QPushButton("저장")
        save.clicked.connect(self._save_bulk)
        row.addWidget(preview)
        row.addWidget(save)
        self.preview_list = QListWidget()
        self.error_list = QListWidget()
        v.addWidget(QLabel("입력"))
        v.addWidget(self.bulk_input)
        v.addLayout(row)
        v.addWidget(QLabel("미리보기"))
        v.addWidget(self.preview_list)
        v.addWidget(QLabel("오류"))
        v.addWidget(self.error_list)
        return w

    def _build_file_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        open_btn = QPushButton("txt 파일 열기")
        open_btn.clicked.connect(self._open_file)
        v.addWidget(QLabel("파일을 불러오면 여러 줄 입력 탭으로 가져옵니다."))
        v.addWidget(open_btn)
        return w

    def _save_single(self) -> None:
        err = self.word_manager.add_single(self.word_input.text(), self.meaning_input.text())
        if err:
            QMessageBox.warning(self, "오류", err)
            return
        self.word_input.clear()
        self.meaning_input.clear()
        self.on_saved()

    def _preview_bulk(self) -> None:
        parsed = self.word_manager.parse_bulk(self.bulk_input.toPlainText())
        self.last_parsed = parsed
        self.preview_list.clear()
        self.error_list.clear()
        for word, meanings in sorted(parsed.merged.items()):
            self.preview_list.addItem(f"{word} = {' | '.join(sorted(meanings))}")
        for err in parsed.errors:
            self.error_list.addItem(err)

    def _save_bulk(self) -> None:
        if not self.last_parsed.merged and not self.last_parsed.errors:
            self._preview_bulk()
        if not self.last_parsed.merged:
            QMessageBox.information(self, "안내", "저장할 유효 단어가 없습니다.")
            return
        self.word_manager.apply_parse_result(self.last_parsed)
        self.bulk_input.clear()
        self.preview_list.clear()
        self.error_list.clear()
        self.last_parsed = ParseResult()
        self.on_saved()

    def _open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "파일 선택", "", "Text Files (*.txt)")
        if not path:
            return
        text = Path(path).read_text(encoding="utf-8")
        self.bulk_input.setPlainText(text)
        self.tabs.setCurrentIndex(1)
        self._preview_bulk()

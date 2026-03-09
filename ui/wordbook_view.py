from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from word_manager import WordManager


class EditDialog(QDialog):
    def __init__(self, word: str, meanings: list[str]) -> None:
        super().__init__()
        self.setWindowTitle("단어 수정")
        layout = QVBoxLayout(self)
        self.word_edit = QLineEdit(word)
        self.meaning_edit = QLineEdit("|".join(meanings))
        ok = QPushButton("저장")
        ok.clicked.connect(self.accept)
        layout.addWidget(QLabel("단어"))
        layout.addWidget(self.word_edit)
        layout.addWidget(QLabel("뜻(|로 구분)"))
        layout.addWidget(self.meaning_edit)
        layout.addWidget(ok)


class WordbookView(QWidget):
    def __init__(self, manager: WordManager, on_changed) -> None:
        super().__init__()
        self.manager = manager
        self.on_changed = on_changed
        v = QVBoxLayout(self)

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("검색")
        self.search.textChanged.connect(self.refresh)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["알파벳순", "최근추가순", "오답많은순"])
        self.sort_combo.currentIndexChanged.connect(self.refresh)
        top.addWidget(self.search)
        top.addWidget(self.sort_combo)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._edit_current)

        btns = QHBoxLayout()
        edit = QPushButton("수정")
        delete = QPushButton("삭제")
        edit.clicked.connect(self._edit_current)
        delete.clicked.connect(self._delete_current)
        btns.addWidget(edit)
        btns.addWidget(delete)

        v.addLayout(top)
        v.addWidget(self.list_widget)
        v.addLayout(btns)
        self.refresh()

    def refresh(self) -> None:
        q = self.search.text().strip().lower()
        words = self.manager.all_words()
        if self.sort_combo.currentText() == "알파벳순":
            words.sort(key=lambda w: w.word)
        elif self.sort_combo.currentText() == "최근추가순":
            words.sort(key=lambda w: w.created_at, reverse=True)
        else:
            words.sort(key=lambda w: w.wrong, reverse=True)

        self.list_widget.clear()
        for w in words:
            if q and q not in w.word and not any(q in m for m in w.meanings):
                continue
            it = QListWidgetItem(f"{w.word} = {' | '.join(w.meanings)}")
            it.setData(Qt.ItemDataRole.UserRole, w.word)
            self.list_widget.addItem(it)

    def _current_word(self) -> str | None:
        it = self.list_widget.currentItem()
        if not it:
            return None
        return it.data(Qt.ItemDataRole.UserRole)

    def _edit_current(self, *_args) -> None:
        word = self._current_word()
        if not word:
            return
        entry = next((w for w in self.manager.all_words() if w.word == word), None)
        if not entry:
            return
        dlg = EditDialog(entry.word, entry.meanings)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        new_meanings = [m.strip() for m in dlg.meaning_edit.text().split("|")]
        err = self.manager.upsert_word(entry.word, dlg.word_edit.text(), new_meanings)
        if err:
            QMessageBox.warning(self, "오류", err)
            return
        self.refresh()
        self.on_changed()

    def _delete_current(self) -> None:
        word = self._current_word()
        if not word:
            return
        self.manager.delete_word(word)
        self.refresh()
        self.on_changed()

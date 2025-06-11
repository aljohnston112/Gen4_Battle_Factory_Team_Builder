import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout

from data.Strings import string_clear


class TextOutputWidget(QWidget):
    """
    A QTextEdit used to display text from the standard output.
    The standard output is redirected to this widget.
    """

    def __clear_clicked__(self) -> None:
        """
        Clears the text.
        """
        self.log_output.clear()
        self.log_output.setAlignment(Qt.AlignCenter)

    def __init__(self):
        super().__init__()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setAlignment(Qt.AlignCenter)
        font = QFont("Courier New")
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.clear_button = QPushButton(string_clear)
        self.clear_button.clicked.connect(self.__clear_clicked__)

        layout = QVBoxLayout()
        layout.addWidget(self.log_output)
        layout.addWidget(self.clear_button)
        self.setLayout(layout)
        sys.stdout = self


    def write(self, text: str):
        self.log_output.moveCursor(QTextCursor.End)
        self.log_output.insertPlainText(text)
        self.log_output.ensureCursorVisible()

    def flush(self):
        pass

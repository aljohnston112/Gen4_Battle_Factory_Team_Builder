import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, \
    QGridLayout

from data.Strings import string_clear


class DualTextOutputWidget(QWidget):
    """
    A QTextEdit used to display text from the standard output.
    The standard output is redirected to this widget.
    """

    def __clear_clicked__(self) -> None:
        """
        Clears the text.
        """
        self.log_output_1.clear()
        self.log_output_1.setAlignment(Qt.AlignCenter)
        self.log_output_2.clear()
        self.log_output_2.setAlignment(Qt.AlignCenter)

    def __init__(self):
        super().__init__()
        self.log_output_1 = QTextEdit()
        self.log_output_1.setReadOnly(True)
        self.log_output_1.setAlignment(Qt.AlignCenter)

        self.log_output_2 = QTextEdit()
        self.log_output_2.setReadOnly(True)
        self.log_output_2.setAlignment(Qt.AlignCenter)

        grid = QGridLayout()
        grid.addWidget(self.log_output_1, 0, 0)
        grid.addWidget(self.log_output_2, 0, 1)
        grid_container = QWidget()
        grid_container.setLayout(grid)

        font = QFont("Courier New")
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.clear_button = QPushButton(string_clear)
        self.clear_button.clicked.connect(self.__clear_clicked__)

        layout = QVBoxLayout()
        layout.addWidget(grid_container)
        layout.addWidget(self.clear_button)
        self.setLayout(layout)

    def write_1(self, text: str):
        self.log_output_1.moveCursor(QTextCursor.End)
        self.log_output_1.insertPlainText(text)
        self.log_output_1.ensureCursorVisible()

    def write_2(self, text: str):
        self.log_output_2.moveCursor(QTextCursor.End)
        self.log_output_2.insertPlainText(text)
        self.log_output_2.ensureCursorVisible()

    def flush(self):
        pass

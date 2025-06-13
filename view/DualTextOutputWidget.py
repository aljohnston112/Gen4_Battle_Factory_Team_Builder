from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, \
    QGridLayout

from data.Strings import string_clear


class DualTextOutputWidget(QWidget):
    """
    A widget with two text output widgets side-by-side.
    """

    def __clear_clicked__(self) -> None:
        """
        Clears the text from both text boxes.
        """
        self.text_output_1.clear()
        self.text_output_1.setAlignment(Qt.AlignCenter)
        self.text_output_2.clear()
        self.text_output_2.setAlignment(Qt.AlignCenter)

    def __init__(self):
        super().__init__()

        # The textboxes inherit this font
        font: QFont = QFont("Courier New")
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.text_output_1: QTextEdit = QTextEdit()
        self.text_output_1.setReadOnly(True)
        self.text_output_1.setAlignment(Qt.AlignCenter)

        self.text_output_2: QTextEdit = QTextEdit()
        self.text_output_2.setReadOnly(True)
        self.text_output_2.setAlignment(Qt.AlignCenter)

        grid: QGridLayout = QGridLayout()
        # row, column
        grid.addWidget(self.text_output_1, 0, 0)
        grid.addWidget(self.text_output_2, 0, 1)
        grid_container: QWidget = QWidget()
        grid_container.setLayout(grid)

        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(grid_container)

        # Clear button
        self.clear_button: QPushButton = QPushButton(string_clear)
        self.clear_button.clicked.connect(self.__clear_clicked__)
        layout.addWidget(self.clear_button)

        self.setLayout(layout)

    def write_1(self, text: str):
        self.text_output_1.moveCursor(QTextCursor.End)
        self.text_output_1.insertPlainText(text)
        self.text_output_1.ensureCursorVisible()

    def write_2(self, text: str):
        self.text_output_2.moveCursor(QTextCursor.End)
        self.text_output_2.insertPlainText(text)
        self.text_output_2.ensureCursorVisible()

    def flush(self):
        pass

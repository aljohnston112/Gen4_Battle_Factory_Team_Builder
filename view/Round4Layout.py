from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from data.Strings import string_move
from view.combo_boxes.MoveComboBox import MoveComboBox


class Round4Layout(QWidget):
    """
    Allows the user to enter hints for round four of battle factory
    """
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        # One move
        label_move = QLabel(string_move)
        layout.addWidget(label_move)
        move = MoveComboBox()
        layout.addWidget(move)

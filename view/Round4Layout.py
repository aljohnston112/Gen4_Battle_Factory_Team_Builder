from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton

from data.Strings import string_move, string_confirm
from view.combo_boxes.MoveComboBox import MoveComboBox
from view_model.Round4ViewModel import Round4ViewModel


class Round4Layout(QWidget):
    """
    Allows the user to enter hints for round four of battle factory
    """
    def __init__(self, team_use_case):
        super().__init__()
        self.__view_model__ = Round4ViewModel(team_use_case)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # One move
        label_move = QLabel(string_move)
        layout.addWidget(label_move)
        move = MoveComboBox()
        move.currentTextChanged.connect(self.__view_model__.set_pokemon_move)
        layout.addWidget(move)

        button_confirm = QPushButton(string_confirm)
        layout.addWidget(button_confirm)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

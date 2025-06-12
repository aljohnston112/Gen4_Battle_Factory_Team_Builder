from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, \
    QSizePolicy, QGridLayout, QSpacerItem

from data.Strings import string_move, string_confirm
from view.combo_boxes.MoveComboBox import MoveComboBox
from view_model.Round4ViewModel import Round4ViewModel


class Round4Layout(QWidget):
    """
    Allows the user to enter hints for round four of the battle factory
    """
    def __init__(self, team_use_case, print_use_case, level):
        super().__init__()
        self.__view_model__ = Round4ViewModel(
            team_use_case=team_use_case,
            print_use_case=print_use_case,
            level=level
        )

        layout = QGridLayout()
        self.setLayout(layout)

        # One move
        layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            0
        )
        label_move = QLabel(string_move)
        layout.addWidget(label_move, 0, 1)
        layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            2
        )
        move = MoveComboBox()
        move.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        move.currentTextChanged.connect(self.__view_model__.set_pokemon_move)
        layout.addWidget(move, 0, 3)
        layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            4
        )

        button_confirm = QPushButton(string_confirm)
        layout.addWidget(button_confirm, 1, 1, 1, 3)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

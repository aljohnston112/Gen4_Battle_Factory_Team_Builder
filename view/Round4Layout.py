from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, \
    QGridLayout

from data.Strings import string_move, string_confirm
from view.LayoutUtil import add_expanding_spacer
from view.combo_boxes.MoveComboBox import MoveComboBox
from view_model.Round4ViewModel import Round4ViewModel


class Round4Layout(QWidget):
    """
    Allows the user to enter hints for round four of the battle factory
    """

    def __init__(self, team_use_case, print_use_case, level):
        super().__init__()
        self.__view_model__: Round4ViewModel = Round4ViewModel(
            team_use_case=team_use_case,
            print_use_case=print_use_case,
            level=level
        )

        layout: QGridLayout = QGridLayout()
        self.setLayout(layout)

        # One move
        add_expanding_spacer(grid_layout=layout, row=0, column=0)
        label_move: QLabel = QLabel(string_move)
        # row, column
        layout.addWidget(label_move, 0, 1)
        add_expanding_spacer(grid_layout=layout, row=0, column=2)

        move_combo_box: MoveComboBox = MoveComboBox()
        move_combo_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        move_combo_box.currentTextChanged.connect(
            self.__view_model__.set_pokemon_move
        )
        # row, column
        layout.addWidget(move_combo_box, 0, 3)
        add_expanding_spacer(grid_layout=layout, row=0, column=4)

        button_confirm: QPushButton = QPushButton(string_confirm)
        # row, column, row_span, column_span
        layout.addWidget(button_confirm, 1, 1, 1, 3)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

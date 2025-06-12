from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, \
    QGridLayout, QSpacerItem, QSizePolicy

from data.Strings import string_type, string_confirm
from view.combo_boxes.PokemonTypeComboBox import PokemonTypeComboBox
from view_model.Round5ViewModel import Round5ViewModel


class Round5Layout(QWidget):
    """
    Allows the user to enter hints for round five of the battle factory
    """

    def __init__(
            self,
            team_use_case,
            print_use_case,
            current_round_use_case,
            level
    ):
        super().__init__()
        self.__view_model__ = Round5ViewModel(
            team_use_case=team_use_case,
            print_use_case=print_use_case,
            current_round_use_case=current_round_use_case,
            level=level
        )
        layout = QGridLayout()
        self.setLayout(layout)

        # Most common type
        layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            0
        )
        label_type = QLabel(string_type)
        layout.addWidget(label_type, 0, 1)
        pokemon_type = PokemonTypeComboBox()
        pokemon_type.currentTextChanged.connect(
            self.__view_model__.set_pokemon_type)
        layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            2
        )
        layout.addWidget(pokemon_type, 0, 3)
        layout.addItem(
            QSpacerItem(0, 1, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            4
        )

        button_confirm = QPushButton(string_confirm)
        layout.addWidget(button_confirm, 1, 1, 1, 3)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton

from data.Strings import string_type, string_confirm
from view.combo_boxes.PokemonTypeComboBox import PokemonTypeComboBox
from view_model.Round5ViewModel import Round5ViewModel


class Round5Layout(QWidget):
    """
    Allows the user to enter hints for round five of battle factory
    """
    def __init__(self, team_use_case):
        super().__init__()
        self.__view_model__ = Round5ViewModel(team_use_case)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Most common type
        label_type = QLabel(string_type)
        layout.addWidget(label_type)
        pokemon_type = PokemonTypeComboBox()
        pokemon_type.currentTextChanged.connect(self.__view_model__.set_pokemon_type)
        layout.addWidget(pokemon_type)

        button_confirm = QPushButton(string_confirm)
        layout.addWidget(button_confirm)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

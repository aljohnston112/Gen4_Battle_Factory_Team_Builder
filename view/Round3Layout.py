from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from data.Strings import string_name, string_move, string_confirm
from view.combo_boxes.MoveComboBox import MoveComboBox
from view.combo_boxes.PokemonComboBox import PokemonComboBox
from view_model.Round3ViewModel import Round3ViewModel


class Round3Layout(QWidget):
    """
    Allows the user to enter hints for round three of battle factory
    """
    def __init__(self, team_use_case):
        super().__init__()
        self.__view_model__ = Round3ViewModel(team_use_case)

        root_layout = QVBoxLayout()
        self.setLayout(root_layout)

        pokemon_and_move_layout = QHBoxLayout()

        # One names
        label_name = QLabel(string_name)
        pokemon_and_move_layout.addWidget(label_name)
        pokemon_combo_box = PokemonComboBox()
        pokemon_combo_box.currentTextChanged.connect(self.text_changed)
        pokemon_and_move_layout.addWidget(pokemon_combo_box)
        self.pokemonComboBox = pokemon_combo_box

        # One move
        label_move = QLabel(string_move)
        pokemon_and_move_layout.addWidget(label_move)
        move = MoveComboBox()
        move.currentTextChanged.connect(self.text_changed)
        pokemon_and_move_layout.addWidget(move)
        self.moveComboBox = move
        root_layout.addLayout(pokemon_and_move_layout)

        button_confirm = QPushButton(string_confirm)
        root_layout.addWidget(button_confirm)
        button_confirm.clicked.connect(self.__view_model__.confirm_clicked)

    def text_changed(self):
        self.__view_model__.set_pokemon_name_and_move(self.get_pokemon(), self.get_move())

    def get_pokemon(self):
        return self.pokemonComboBox.currentText()

    def get_move(self):
        return self.moveComboBox.currentText()
